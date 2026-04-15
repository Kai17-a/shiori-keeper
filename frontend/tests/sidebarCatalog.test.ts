import { describe, expect, it } from "vitest";

import { applySidebarCatalogResults, createSidebarCatalogState } from "~/utils/sidebarCatalog";

describe("sidebarCatalog helpers", () => {
  it("creates a predictable empty state", () => {
    expect(createSidebarCatalogState()).toEqual({
      folders: [],
      tags: [],
      rssFeeds: [],
      loaded: false,
    });
  });

  it("applies loaded catalog data to the state object", () => {
    const state = createSidebarCatalogState();
    const folders = [{ id: 1, name: "Work", created_at: "2026-04-10T00:00:00Z" }];
    const tags = [{ id: 2, name: "Frontend" }];
    const rssFeeds = [{ id: 3, title: "Daily", url: "https://example.com/feed", description: null, created_at: "2026-04-10T00:00:00Z", updated_at: "2026-04-10T00:00:00Z" }];

    expect(applySidebarCatalogResults(state, folders, tags, rssFeeds)).toBe(state);
    expect(state).toEqual({
      folders,
      tags,
      rssFeeds,
      loaded: true,
    });
  });
});
