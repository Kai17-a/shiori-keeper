import type { FolderResponse, RSSFeedResponse, TagResponse } from "~/types";

export type SidebarCatalogState = {
  folders: FolderResponse[];
  tags: TagResponse[];
  rssFeeds: RSSFeedResponse[];
  loaded: boolean;
};

export const createSidebarCatalogState = (): SidebarCatalogState => ({
  folders: [],
  tags: [],
  rssFeeds: [],
  loaded: false,
});

export const applySidebarCatalogResults = (
  state: SidebarCatalogState,
  folders: FolderResponse[],
  tags: TagResponse[],
  rssFeeds: RSSFeedResponse[],
) => {
  state.folders = folders;
  state.tags = tags;
  state.rssFeeds = rssFeeds;
  state.loaded = true;
  return state;
};

export const refreshSidebarCatalogSafely = async (
  refresh: (force?: boolean) => Promise<void>,
  force = false,
) => {
  try {
    await refresh(force);
    return true;
  } catch {
    return false;
  }
};
