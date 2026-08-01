import { expect, test, type Locator, type Page } from "@playwright/test";
import { createServer } from "node:http";
import process from "node:process";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";
const discordWebhookUrl = "https://discord.com/api/webhooks/1234567890/test-token";
const buttonByText = (page: Page, label: string) => page.locator(`button:has-text("${label}")`).first();
const headingByText = (page: Page, text: string) => page.locator("h1").filter({ hasText: text }).last();
const activate = async (locator: Locator) => {
  await locator.focus();
  await locator.press("Enter");
};

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
    await page.goto("/bookmarks");
    await expect(page).toHaveURL(/\/bookmarks\/?$/);
    await activate(buttonByText(page, "Register"));
    await expect(page.getByRole("dialog")).toContainText("Register bookmark");
    await page.getByRole("textbox", { name: "Title" }).fill(title);
    await page.getByRole("textbox", { name: "URL" }).fill(url);
    await page.getByRole("textbox", { name: "Description" }).fill("Original description");
    await buttonByText(page, "Save bookmark").click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(page.getByText(title, { exact: true })).toBeVisible();

    const bookmarkCard = page.locator("article").filter({ has: page.getByText(title, { exact: true }) });
    await activate(bookmarkCard.locator("button").nth(1));
    await page.getByRole("textbox", { name: "Title" }).fill(updatedTitle);
    await page.getByRole("textbox", { name: "Description" }).fill(updatedDescription);
    await buttonByText(page, "Save bookmark").click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(page.getByText(updatedTitle, { exact: true })).toBeVisible();

    const updatedBookmarkCard = page
      .locator("article")
      .filter({ has: page.getByText(updatedTitle, { exact: true }) });
    await activate(updatedBookmarkCard.locator("button").nth(1));
    await page.getByRole("textbox", { name: "Description" }).fill("");
    await buttonByText(page, "Save bookmark").click();
    await expect(page.getByRole("dialog")).toHaveCount(0);

    await activate(updatedBookmarkCard.locator("button").nth(1));
    await expect(page.getByRole("textbox", { name: "Description" })).toHaveValue("");
    await buttonByText(page, "Cancel").click();

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

  test("normalizes an out-of-range page after narrowing results", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const titles = Array.from(
      { length: 21 },
      (_, index) => `Paged Bookmark ${suffix} ${index}`,
    );

    for (const [index, title] of titles.entries()) {
      await createBookmark(page, `${suffix}-${index}`, { title });
    }

    await page.goto("/bookmarks?page=999");
    await expect(page).toHaveURL((url) => url.searchParams.get("page") === "2");
    await expect(page.getByText("Page 2 of 2")).toBeVisible();

    const searchInput = page.getByPlaceholder("Search by title or URL");
    await searchInput.fill(titles[0]!);
    await expect(page).toHaveURL(
      (url) => url.searchParams.get("q") === titles[0] && !url.searchParams.has("page"),
    );
    await expect(page.getByText(titles[0]!, { exact: true })).toBeVisible();
    await expect(page.getByText("Page 1 of 1")).toBeVisible();
  });
});

test.describe("folders", () => {
  test("creates, edits, opens, and deletes folders from the UI", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const name = `Folder ${suffix}`;
    const updatedName = `${name} Updated`;
    const folderPanel = page.locator("#dashboard-panel-folders");

    await page.goto("/folders");
    await page.getByPlaceholder("New folder name").fill(name);
    await page.getByPlaceholder("Optional folder description").first().fill("Folder description");
    await activate(buttonByText(page, "Add folder"));
    await expect(folderPanel.getByText(name, { exact: true })).toBeVisible();

    let folderCard = folderPanel
      .getByText(name, { exact: true })
      .locator("xpath=ancestor::*[.//button][1]");
    await activate(folderCard.locator("button").first());
    await page.getByRole("textbox", { name: "Folder name" }).fill(updatedName);
    await page.getByRole("textbox", { name: "Description" }).fill("Updated folder description");
    await buttonByText(page, "Save changes").click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(folderPanel.getByText(updatedName, { exact: true })).toBeVisible();

    await activate(folderPanel.locator("a").filter({ hasText: updatedName }).first());
    await expect(page).toHaveURL(/\/folders\/\d+\/?$/);
    await expect(headingByText(page, updatedName)).toBeVisible();

    await page.getByRole("button", { name: "Delete" }).click();
    await buttonByText(page, "Delete folder").click();
    await expect(page).toHaveURL(/\/folders\/?$/);
    await expect(folderPanel.getByText(updatedName, { exact: true })).toHaveCount(0);
  });
});

test.describe("tags", () => {
  test("creates, edits, opens, and deletes tags from the UI", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const name = `Tag ${suffix}`;
    const updatedName = `${name} Updated`;
    const tagPanel = page.locator("#dashboard-panel-tags");

    await page.goto("/tags");
    await page.getByPlaceholder("New tag name").fill(name);
    await page.getByPlaceholder("Optional tag description").first().fill("Tag description");
    await activate(buttonByText(page, "Add tag"));
    await expect(tagPanel.getByText(name, { exact: true })).toBeVisible();

    let tagCard = tagPanel
      .getByText(name, { exact: true })
      .locator("xpath=ancestor::*[.//button][1]");
    await activate(tagCard.locator("button").first());
    await page.getByRole("textbox", { name: "Tag name" }).fill(updatedName);
    await page.getByRole("textbox", { name: "Description" }).fill("Updated tag description");
    await buttonByText(page, "Save changes").click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
    await expect(tagPanel.getByText(updatedName, { exact: true })).toBeVisible();

    await activate(tagPanel.locator("a").filter({ hasText: updatedName }).first());
    await expect(page).toHaveURL(/\/tags\/\d+\/?$/);
    await expect(headingByText(page, updatedName)).toBeVisible();

    await page.getByRole("button", { name: "Delete" }).click();
    await buttonByText(page, "Delete tag").click();
    await expect(page).toHaveURL(/\/tags\/?$/);
    await expect(tagPanel.getByText(updatedName, { exact: true })).toHaveCount(0);
  });
});

test.describe("rss feeds", () => {
  test("creates, edits, opens, and deletes rss feeds from the UI", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const rssServer = await startRssServer(suffix);
    try {
      const title = `RSS Feed ${suffix}`;
      const updatedTitle = `${title} Updated`;
      const rssPanel = page.locator("#dashboard-panel-rss");

      await page.goto("/rss");
      await expect(page).toHaveURL(/\/rss\/?$/);
      await activate(buttonByText(page, "Register"));
      await expect(page.getByRole("dialog")).toContainText("Register RSS feed");
      await page.getByRole("textbox", { name: "Title" }).fill(title);
      await page.getByRole("textbox", { name: "URL" }).fill(rssServer.url);
      await page.getByRole("textbox", { name: "Description" }).fill("RSS description");
      await buttonByText(page, "Save feed").click();
      await expect(page.getByRole("dialog")).toHaveCount(0);
      await expect(rssPanel.getByText(title, { exact: true })).toBeVisible();

      let feedCard = page.locator("article").filter({ has: page.getByText(title, { exact: true }) });
      await activate(feedCard.locator("button").nth(2));
      await page.getByRole("textbox", { name: "Title" }).fill(updatedTitle);
      await page.getByRole("textbox", { name: "Description" }).fill("Updated RSS description");
      await buttonByText(page, "Save feed").click();
      await expect(page.getByRole("dialog")).toHaveCount(0);
      await expect(rssPanel.getByText(updatedTitle, { exact: true })).toBeVisible();

      feedCard = page
        .locator("article")
        .filter({ has: page.getByText(updatedTitle, { exact: true }) });
      await activate(feedCard.locator("a").filter({ hasText: updatedTitle }).first());
      await expect(page).toHaveURL(/\/rss\/\d+\/?$/);
      await expect(headingByText(page, updatedTitle)).toBeVisible();
      await page.goto("/rss");
      await expect(page).toHaveURL(/\/rss\/?$/);

      feedCard = page
        .locator("article")
        .filter({ has: page.getByText(updatedTitle, { exact: true }) });
      await activate(feedCard.locator("button").nth(3));
      await buttonByText(page, "Delete feed").click();
      await expect(rssPanel.getByText(updatedTitle, { exact: true })).toHaveCount(0);
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

    const webhookInput = page.getByLabel("Webhook URL");
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
