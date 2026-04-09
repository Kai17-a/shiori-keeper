import type { FolderResponse, TagResponse } from "~/types";

export type SidebarCatalogState = {
  folders: FolderResponse[];
  tags: TagResponse[];
  loaded: boolean;
};

export const createSidebarCatalogState = (): SidebarCatalogState => ({
  folders: [],
  tags: [],
  loaded: false,
});

export const applySidebarCatalogResults = (
  state: SidebarCatalogState,
  folders: FolderResponse[],
  tags: TagResponse[],
) => {
  state.folders = folders;
  state.tags = tags;
  state.loaded = true;
  return state;
};
