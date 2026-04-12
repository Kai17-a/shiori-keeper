import {
  applySidebarCatalogResults,
  createSidebarCatalogState,
  type SidebarCatalogState,
} from "~/utils/sidebarCatalog";
import type { FolderResponse, TagResponse } from "~/types";

export const useSidebarCatalog = () => {
  const state = useState<SidebarCatalogState>("sidebar-catalog", createSidebarCatalogState);

  const { request } = useBookmarkApi();
  const loading = ref(false);
  let loadPromise: Promise<void> | null = null;

  const refresh = async () => {
    if (loadPromise) {
      return loadPromise;
    }

    loadPromise = (async () => {
      loading.value = true;
      try {
        const [foldersRes, tagsRes] = await Promise.all([
          request<FolderResponse[]>("/folders"),
          request<TagResponse[]>("/tags"),
        ]);

        applySidebarCatalogResults(state.value, foldersRes, tagsRes);
      } finally {
        loading.value = false;
        loadPromise = null;
      }
    })();

    return loadPromise;
  };

  return {
    folders: computed(() => state.value.folders),
    tags: computed(() => state.value.tags),
    loaded: computed(() => state.value.loaded),
    loading: computed(() => loading.value),
    refresh,
  };
};
