import { expect, test, type Page } from "@playwright/test";
import { createServer } from "node:http";
import process from "node:process";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";
const discordWebhookUrl = "https://discord.com/api/webhooks/1234567890/test-token";
const buttonByText = (page: Page, label: string) => page.locator(`button:has-text("${label}")`).first();
const headingByText = (page: Page, text: string) => page.locator("h1").filter({ hasText: text }).last();

const createBookmark = async (
  page: Page,
  suffix: string,
  overrides: Partial<{
    url: string;
    title: string;
    description: string;
    folder_id: number | null;
    tag_ids: number[];
    is_favorite: boolean;
  }> = {},
) => {
  const created = await page.request.post(`${apiBaseUrl}/bookmarks`, {
    data: {
      url: overrides.url ?? `https://example.com/${suffix}`,
      title: overrides.title ?? `Example Bookmark ${suffix}`,
      description: overrides.description ?? "Original description",
      folder_id: overrides.folder_id ?? null,
      tag_ids: overrides.tag_ids ?? [],
    },
  });
  expect(created.status()).toBe(201);
  const createdBody = (await created.json()) as { id: number };

  if (overrides.is_favorite) {
    const favorited = await page.request.patch(`${apiBaseUrl}/bookmarks/favorite`, {
      data: {
        bookmark_id: createdBody.id,
        is_favorite: true,
      },
    });
    expect(favorited.status()).toBe(200);
  }

  return createdBody;
};

const startRssServer = async (suffix: string) => {
  const server = createServer((_, res) => {
    res.writeHead(200, { "content-type": "application/rss+xml; charset=utf-8" });
    res.end(`<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>RSS Feed ${suffix}</title>
    <link>https://example.com/${suffix}</link>
    <description>RSS description</description>
    <item>
      <title>Item ${suffix}</title>
      <link>https://example.com/${suffix}/1</link>
      <description>Item description</description>
    </item>
  </channel>
</rss>`);
  });

  await new Promise<void>((resolve) => {
    server.listen(0, "127.0.0.1", resolve);
  });

  const address = server.address();
  if (!address || typeof address === "string") {
    throw new Error("Failed to start RSS test server");
  }

  return {
    url: `http://127.0.0.1:${address.port}/feed.xml`,
    close: () =>
      new Promise<void>((resolve, reject) => {
        server.close((err) => (err ? reject(err) : resolve()));
      }),
  };
};

test.describe.configure({ mode: "serial" });

test.describe("bookmarks", () => {
  test("loads, edits, searches, and deletes bookmarks", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const url = `https://example.com/${suffix}`;
    const title = `Example Bookmark ${suffix}`;
    const updatedTitle = `${title} Updated`;
    const updatedDescription = "Updated description";
    await createBookmark(page, suffix, { title, url });

    await page.goto("/bookmarks");
    await expect(page).toHaveURL(/\/bookmarks\/?$/);
    await buttonByText(page, "Refresh").click({ force: true });
    await expect(page.getByText(title, { exact: true })).toBeVisible();

    const bookmarkCard = page.locator("article").filter({ has: page.getByText(title, { exact: true }) });
    await bookmarkCard.getByRole("button", { name: "Edit" }).click({ force: true });
    await page.getByRole("textbox", { name: "Title" }).fill(updatedTitle);
    await page.getByRole("textbox", { name: "Description" }).fill(updatedDescription);
    await buttonByText(page, "Save bookmark").click();
    await expect(page.getByText(updatedTitle, { exact: true })).toBeVisible();

    const searchInput = page.getByPlaceholder("Search by title or URL");
    await searchInput.fill(updatedTitle);
    await expect(page.getByText(updatedTitle, { exact: true })).toBeVisible();
    await searchInput.fill("does-not-exist");
    await expect(page.getByText("No bookmarks yet.")).toBeVisible();
    await searchInput.fill(updatedTitle);
    await expect(page.getByText(updatedTitle, { exact: true })).toBeVisible();

    await page
      .locator("article")
      .filter({ has: page.getByText(updatedTitle, { exact: true }) })
      .getByRole("button")
      .last()
      .click({ force: true });
    await buttonByText(page, "Delete bookmark").click();
    await expect(page.getByText(updatedTitle, { exact: true })).toHaveCount(0);
  });
});

test.describe("folders", () => {
  test("opens folder detail pages and shows related bookmarks", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const created = await page.request.post(`${apiBaseUrl}/folders`, {
      data: { name: `Folder ${suffix}`, description: "Folder description" },
    });
    expect(created.status()).toBe(201);
    const createdBody = (await created.json()) as { id: number };

    const bookmarked = await page.request.post(`${apiBaseUrl}/bookmarks`, {
      data: {
        url: `https://example.com/folder-${suffix}`,
        title: `Folder Bookmark ${suffix}`,
        description: "Folder related bookmark",
        folder_id: createdBody.id,
        tag_ids: [],
      },
    });
    expect(bookmarked.status()).toBe(201);

    await page.goto(`/folders/${createdBody.id}`);
    await expect(page).toHaveURL(new RegExp(`/folders/${createdBody.id}/?$`));
    await expect(headingByText(page, `Folder ${suffix}`)).toBeVisible();
    await expect(page.getByText(`Folder Bookmark ${suffix}`, { exact: true })).toBeVisible();
  });
});

test.describe("tags", () => {
  test("opens tag detail pages and shows related bookmarks", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const created = await page.request.post(`${apiBaseUrl}/tags`, {
      data: { name: `Tag ${suffix}`, description: "Tag description" },
    });
    expect(created.status()).toBe(201);
    const createdBody = (await created.json()) as { id: number };

    const bookmarked = await page.request.post(`${apiBaseUrl}/bookmarks`, {
      data: {
        url: `https://example.com/tag-${suffix}`,
        title: `Tag Bookmark ${suffix}`,
        description: "Tag related bookmark",
        folder_id: null,
        tag_ids: [createdBody.id],
      },
    });
    expect(bookmarked.status()).toBe(201);

    await page.goto(`/tags/${createdBody.id}`);
    await expect(page).toHaveURL(new RegExp(`/tags/${createdBody.id}/?$`));
    await expect(headingByText(page, `Tag ${suffix}`)).toBeVisible();
    await expect(page.getByText(`Tag Bookmark ${suffix}`, { exact: true })).toBeVisible();
  });
});

test.describe("rss feeds", () => {
  test("loads, opens, and deletes rss feeds from the UI", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const rssServer = await startRssServer(suffix);
    try {
      const title = `RSS Feed ${suffix}`;
      const created = await page.request.post(`${apiBaseUrl}/rss-feeds`, {
        data: {
          url: rssServer.url,
          title,
          description: "RSS description",
        },
      });
      expect(created.status()).toBe(201);
      const createdBody = (await created.json()) as { id: number };

      await page.goto("/rss");
      await expect(page).toHaveURL(/\/rss\/?$/);
      await page.goto(`/rss/${createdBody.id}`);
      await expect(page).toHaveURL(/\/rss\/\d+\/?$/);
      await expect(headingByText(page, title)).toBeVisible();
      await page.goto("/rss");
      await expect(page).toHaveURL(/\/rss\/?$/);

      const deleted = await page.request.delete(`${apiBaseUrl}/rss-feeds/${createdBody.id}`);
      expect(deleted.status()).toBe(204);
    } finally {
      await rssServer.close();
    }
  });

  test("loads, saves webhook settings and toggles rss execution", async ({ page }) => {
    await page.request.put(`${apiBaseUrl}/settings/webhook`, {
      data: { webhook_url: discordWebhookUrl },
    });
    await page.request.put(`${apiBaseUrl}/settings/rss-execution`, {
      data: { enabled: false },
    });
    await page.request.put(`${apiBaseUrl}/settings/rss-webhook-notification`, {
      data: { enabled: false },
    });

    await page.goto("/rss");
    await page.reload();
    await expect(page.getByText("Webhook is configured.")).toBeVisible();

    const webhookInput = page.getByPlaceholder("https://discord.com/api/webhooks/...");
    await expect(webhookInput).toHaveValue(discordWebhookUrl);
    await webhookInput.fill(`${discordWebhookUrl}-updated`);
    await buttonByText(page, "Save webhook").click({ force: true });
    await expect(webhookInput).toHaveValue(`${discordWebhookUrl}-updated`);

    const rssExecutionSwitch = page.getByRole("switch").first();
    const rssWebhookNotificationSwitch = page.getByRole("switch").nth(1);
    await expect(rssExecutionSwitch).toHaveAttribute("aria-checked", "false");
    await rssExecutionSwitch.click({ force: true });
    await expect(rssExecutionSwitch).toHaveAttribute("aria-checked", "true");
    await expect(rssWebhookNotificationSwitch).toHaveAttribute("aria-checked", "false");
    await rssWebhookNotificationSwitch.click({ force: true });
    await expect(rssWebhookNotificationSwitch).toHaveAttribute("aria-checked", "true");
  });

});

test.describe("favorites", () => {
  test("loads favorite bookmarks and removes them through the favorite toggle", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    await createBookmark(page, `${suffix}-regular`, {
      title: `Regular Bookmark ${suffix}`,
      is_favorite: false,
    });
    await createBookmark(page, `${suffix}-favorite`, {
      title: `Favorite Bookmark ${suffix}`,
      is_favorite: true,
    });

    await page.goto("/favorites");
    await expect(page).toHaveURL(/\/favorites\/?$/);
    await buttonByText(page, "Refresh").click({ force: true });
    await expect(page.getByText(`Favorite Bookmark ${suffix}`, { exact: true })).toBeVisible();
    await expect(page.getByText(`Regular Bookmark ${suffix}`, { exact: true })).toHaveCount(0);

    const favoriteCard = page
      .locator("article")
      .filter({ has: page.getByText(`Favorite Bookmark ${suffix}`, { exact: true }) });
    await favoriteCard.getByRole("button", { name: "Remove from favorites" }).click({ force: true });
    await expect(page.getByText(`Favorite Bookmark ${suffix}`, { exact: true })).toHaveCount(0);
  });
});

test.describe("settings", () => {
  test("toggles theme and persists the selection", async ({ page }) => {
    await page.goto("/settings");
    await expect(page).toHaveURL(/\/settings\/?$/);
    await expect(page.getByText("Theme", { exact: true })).toBeVisible();
    const darkTab = page.locator('[role="tab"]').filter({ hasText: "Dark" });
    const systemTab = page.locator('[role="tab"]').filter({ hasText: "System" });

    await darkTab.focus();
    await page.keyboard.press("Enter");
    await expect(darkTab).toHaveAttribute("aria-selected", "true");
    await page.reload();
    await expect(darkTab).toHaveAttribute("aria-selected", "true");
    await systemTab.focus();
    await page.keyboard.press("Enter");
  });
});
