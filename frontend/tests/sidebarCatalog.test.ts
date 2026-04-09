import { describe, expect, it } from "vitest";

import {
  applySidebarCatalogResults,
  createSidebarCatalogState,
} from "~/utils/sidebarCatalog";

describe("sidebarCatalog helpers", () => {
  it("creates a predictable empty state", () => {
    expect(createSidebarCatalogState()).toEqual({
      folders: [],
      tags: [],
      loaded: false,
    });
  });

  it("applies loaded catalog data to the state object", () => {
    const state = createSidebarCatalogState();
    const folders = [{ id: 1, name: "Work", created_at: "2026-04-10T00:00:00Z" }];
    const tags = [{ id: 2, name: "Frontend" }];

    expect(applySidebarCatalogResults(state, folders, tags)).toBe(state);
    expect(state).toEqual({
      folders,
      tags,
      loaded: true,
    });
  });
});
