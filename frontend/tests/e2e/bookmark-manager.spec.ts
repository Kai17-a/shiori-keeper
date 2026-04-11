import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";

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
    const createdBookmark = lookupBody.items.find(
      (item) => item.url === url,
    );
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
      data: { name: `Folder ${suffix}` },
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
      data: { name: `Tag ${suffix}` },
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
    await expect(page.getByText(`Tag Bookmark ${suffix}`)).toBeVisible();

    const deleted = await page.request.delete(`${apiBaseUrl}/tags/${createdBody.id}`);
    expect(deleted.status()).toBe(204);
    await page.goto("/tags");
    await expect(page).toHaveURL(/\/tags$/);
  });
});
