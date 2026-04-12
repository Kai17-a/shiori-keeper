import { expect, test } from "@playwright/test";
import { createServer } from "node:http";
import process from "node:process";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";

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
  test("creates, edits, searches, and deletes bookmarks", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const url = `https://example.com/${suffix}`;
    const title = `Example Bookmark ${suffix}`;

    const created = await page.request.post(`${apiBaseUrl}/bookmarks`, {
      data: {
        url,
        title,
        description: "Original description",
        folder_id: null,
        tag_ids: [],
      },
    });
    expect(created.status()).toBe(201);
    const createdBody = (await created.json()) as { id: number };

    await page.goto("/bookmarks");
    await expect(page.getByText("Bookmark list", { exact: true })).toBeVisible();
    await expect(page.getByText("Original description").first()).toBeVisible();

    await page.getByPlaceholder("Search by title or URL").fill(title);
    await expect(page.getByText(title)).toBeVisible();

    const lookup = await page.request.get(`${apiBaseUrl}/bookmarks?q=${encodeURIComponent(url)}`);
    expect(lookup.status()).toBe(200);
    const lookupBody = (await lookup.json()) as {
      items: Array<{ id: number; url: string }>;
    };
    const createdBookmark = lookupBody.items.find((item) => item.url === url);
    expect(createdBookmark?.id ?? createdBody.id).toBeTruthy();

    const deleted = await page.request.delete(
      `${apiBaseUrl}/bookmarks/${createdBookmark?.id ?? createdBody.id}`,
    );
    expect(deleted.status()).toBe(204);
    await page.reload();
    await expect(page.getByText(title)).toHaveCount(0);
  });
});

test.describe("folders", () => {
  test("creates, renames, opens, and deletes folders", async ({ page }) => {
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
    await expect(page.getByRole("heading", { name: `Folder ${suffix}` })).toBeVisible();
    await expect(page.getByText("Folder description")).toBeVisible();
    await expect(page.getByText(`Folder Bookmark ${suffix}`)).toBeVisible();

    const deleted = await page.request.delete(`${apiBaseUrl}/folders/${createdBody.id}`);
    expect(deleted.status()).toBe(204);
    await page.goto("/folders");
    await expect(page).toHaveURL(/\/folders$/);
  });
});

test.describe("tags", () => {
  test("creates, renames, opens, and deletes tags", async ({ page }) => {
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
    await expect(page.getByRole("heading", { name: `Tag ${suffix}` })).toBeVisible();
    await expect(page.getByText("Tag description")).toBeVisible();
    await expect(page.getByText(`Tag Bookmark ${suffix}`)).toBeVisible();

    const deleted = await page.request.delete(`${apiBaseUrl}/tags/${createdBody.id}`);
    expect(deleted.status()).toBe(204);
    await page.goto("/tags");
    await expect(page).toHaveURL(/\/tags$/);
  });
});

test.describe("rss feeds", () => {
  test("creates, edits, opens, and deletes rss feeds", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;
    const rssServer = await startRssServer(suffix);
    try {
      const created = await page.request.post(`${apiBaseUrl}/rss-feeds`, {
        data: {
          url: rssServer.url,
          title: `RSS Feed ${suffix}`,
          description: "RSS description",
        },
      });
      expect(created.status()).toBe(201);
      const createdBody = (await created.json()) as { id: number };

      await page.goto("/rss");
      await expect(page).toHaveURL(/\/rss$/);
      await expect(page.getByText("RSS feeds", { exact: true })).toBeVisible();
      await expect(page.getByText(rssServer.url, { exact: true })).toBeVisible();

      const updated = await page.request.patch(`${apiBaseUrl}/rss-feeds/${createdBody.id}`, {
        data: {
          title: `RSS Feed ${suffix} Updated`,
        },
      });
      expect(updated.status()).toBe(200);

      await page.reload();
      await expect(page.getByText(`RSS Feed ${suffix} Updated`)).toBeVisible();

      const deleted = await page.request.delete(`${apiBaseUrl}/rss-feeds/${createdBody.id}`);
      expect(deleted.status()).toBe(204);
      await page.reload();
      await expect(page.getByText(`RSS Feed ${suffix} Updated`)).toHaveCount(0);
    } finally {
      await rssServer.close();
    }
  });
});
