import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.PLAYWRIGHT_API_BASE_URL ?? "http://127.0.0.1:8000";

test.describe.configure({ mode: "serial" });

test.describe("bookmarks", () => {
  test("creates, edits, searches, and deletes bookmarks", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;

    await page.goto("/bookmarks");
    await page.getByRole("button", { name: "Register" }).click();
    await page.getByLabel("URL").fill(`https://example.com/${suffix}`);
    await page.getByLabel("Title").fill(`Example Bookmark ${suffix}`);
    await page.getByLabel("Description").fill("Original description");
    await page.getByRole("button", { name: "Save bookmark" }).click();

    const bookmarkLink = page.getByRole("link", { name: `Example Bookmark ${suffix}` });
    await expect(bookmarkLink).toBeVisible();
    await expect(page.getByText("Original description").first()).toBeVisible();

    await page.getByPlaceholder("Search by title or URL").fill(`Example Bookmark ${suffix}`);
    await expect(bookmarkLink).toBeVisible();

    await page.getByPlaceholder("Search by title or URL").fill("");
    await page.getByRole("button", { name: "Edit" }).first().click();
    await page.getByLabel("Title").fill(`Updated Bookmark ${suffix}`);
    await page.getByRole("button", { name: "Save bookmark" }).click();
    const updatedLink = page.getByRole("link", { name: `Updated Bookmark ${suffix}` });
    await expect(updatedLink).toBeVisible();

    await page.getByRole("button", { name: "Edit" }).first().click();
    const lookup = await page.request.get(
      `${apiBaseUrl}/bookmarks?q=${encodeURIComponent(`https://example.com/${suffix}`)}`,
    );
    expect(lookup.status()).toBe(200);
    const lookupBody = (await lookup.json()) as {
      items: Array<{ id: number; url: string }>;
    };
    const createdBookmark = lookupBody.items.find(
      (item) => item.url === `https://example.com/${suffix}`,
    );
    expect(createdBookmark?.id).toBeTruthy();

    const deleted = await page.request.delete(
      `${apiBaseUrl}/bookmarks/${createdBookmark?.id}`,
    );
    expect(deleted.status()).toBe(204);
    await expect(updatedLink).toHaveCount(0);
  });
});

test.describe("folders", () => {
  test("creates, renames, opens, and deletes folders", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;

    await page.goto("/folders");
    await page.getByPlaceholder("New folder name").fill(`Folder ${suffix}`);
    await page.getByRole("button", { name: "Add folder" }).click();
    await expect(page.getByText(`Folder ${suffix}`)).toBeVisible();

    await page.getByRole("button", { name: "Edit" }).first().click();
    await page.getByLabel("Folder name").fill(`Folder Updated ${suffix}`);
    await page.getByRole("button", { name: "Save changes" }).click();
    await expect(page.getByText(`Folder Updated ${suffix}`)).toBeVisible();

    await page.getByRole("link", { name: `Folder Updated ${suffix}` }).click();
    await expect(page.getByRole("heading", { name: `Folder Updated ${suffix}` })).toBeVisible();
    await page.getByRole("button", { name: "Delete folder" }).click();
    await page.getByRole("button", { name: "Delete folder" }).last().click();
    await expect(page).toHaveURL(/\/folders$/);
  });
});

test.describe("tags", () => {
  test("creates, renames, opens, and deletes tags", async ({ page }) => {
    const suffix = `${Date.now()}-${test.info().workerIndex}`;

    await page.goto("/tags");
    await page.getByPlaceholder("New tag name").fill(`Tag ${suffix}`);
    await page.getByRole("button", { name: "Add tag" }).click();
    await expect(page.getByText(`Tag ${suffix}`)).toBeVisible();

    await page.getByRole("button", { name: "Edit" }).first().click();
    await page.getByLabel("Tag name").fill(`Tag Updated ${suffix}`);
    await page.getByRole("button", { name: "Save changes" }).click();
    await expect(page.getByText(`Tag Updated ${suffix}`)).toBeVisible();

    await page.getByRole("link", { name: `Tag Updated ${suffix}` }).click();
    await expect(page.getByRole("heading", { name: `Tag Updated ${suffix}` })).toBeVisible();
    await page.getByRole("button", { name: "Delete tag" }).click();
    await page.getByRole("button", { name: "Delete tag" }).last().click();
    await expect(page).toHaveURL(/\/tags$/);
  });
});
