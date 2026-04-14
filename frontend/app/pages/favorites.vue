<template>
  <UDashboardPanel id="favorites">
    <template #header>
      <PageHeaderActions title="Favorites" />
    </template>

    <template #body>
      <div class="space-y-6">
        <UPageCard :ui="{ body: 'space-y-4' }">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-default">Favorite bookmarks</h2>
              <p class="text-sm text-muted">
                Bookmarks marked with a star through the dedicated favorite API
              </p>
            </div>
            <UButton
              icon="i-lucide-refresh-cw"
              color="neutral"
              variant="ghost"
              size="sm"
              :loading="loading"
              @click="loadFavorites"
            >
              Refresh
            </UButton>
          </div>

          <div
            class="flex flex-col gap-3 border-b border-default pb-4 md:flex-row md:items-center md:justify-between"
          >
            <p class="text-xs uppercase tracking-[0.08em] text-muted">
              {{ favoriteBookmarks.length }} favorites
            </p>
            <p class="text-xs uppercase tracking-[0.08em] text-muted">
              {{ allBookmarks.length }} loaded
            </p>
          </div>

          <div
            v-if="loading"
            class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
          >
            Loading favorites...
          </div>

          <div
            v-else-if="loadError"
            class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
          >
            {{ loadError }}
          </div>

          <div
            v-else-if="favoriteBookmarks.length"
            class="grid gap-4 md:grid-cols-2 xl:grid-cols-3"
          >
            <BookmarkCard
              v-for="bookmark in favoriteBookmarksWithFolderNames"
              :key="bookmark.id"
              :bookmark="bookmark"
              :show-folder="true"
              :show-tags="true"
              @edit="loadBookmarkForm"
              @remove="removeBookmark"
              @favorite="toggleFavorite"
            />
          </div>
          <div
            v-else
            class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
          >
            No favorites yet.
          </div>

          <BookmarkEditorModal
            v-model:open="modalOpen"
            v-model:selected-folder="selectedBookmarkFolder"
            :form="bookmarkForm"
            :folder-options="bookmarkFolderOptions"
            :tag-options="bookmarkTagOptions"
            :title="bookmarkForm.id ? 'Edit bookmark' : 'Register bookmark'"
            :description="
              bookmarkForm.id
                ? 'Update the bookmark details.'
                : 'Create a bookmark and attach tags.'
            "
            :submit-label="saving ? 'Saving...' : 'Save bookmark'"
            :saving="saving"
            @save="saveBookmark"
          />

          <DeleteConfirmModal
            v-model:open="deleteOpen"
            title="Delete bookmark"
            subject="this bookmark"
            confirm-label="Delete bookmark"
            :loading="deleting"
            @cancel="pendingBookmark = null"
            @confirm="confirmDelete"
          />
        </UPageCard>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type { BookmarkListResponse, BookmarkResponse, FolderResponse } from "~/types";
import { mapBookmarksWithFolderNames } from "~/utils/bookmarkList";

const { request } = useBookmarkApi();
const toast = useSingleToast();

const loading = ref(false);
const loadError = ref("");
const allBookmarks = ref<BookmarkResponse[]>([]);
const folders = ref<FolderResponse[]>([]);
const bookmarkFolderOptions = computed(() => [
  { label: "No folder", value: "" },
  ...folders.value.map((folder) => ({ label: folder.name, value: String(folder.id) })),
]);

const favoriteBookmarks = computed(() =>
  allBookmarks.value.filter((bookmark) => bookmark.is_favorite),
);

const favoriteBookmarksWithFolderNames = computed(() =>
  mapBookmarksWithFolderNames(favoriteBookmarks.value, folders.value),
);

const bookmarkTagOptions = computed(() =>
  favoriteBookmarks.value.flatMap((bookmark) =>
    bookmark.tags.map((tag) => ({ label: tag.name, value: String(tag.id) })),
  ),
);

const loadAllBookmarks = async () => {
  const firstPage = await request<BookmarkListResponse>("/bookmarks?per_page=100&page=1");
  const items = [...firstPage.items];

  for (let page = 2; page <= firstPage.total_pages; page += 1) {
    const nextPage = await request<BookmarkListResponse>(`/bookmarks?per_page=100&page=${page}`);
    items.push(...nextPage.items);
  }

  allBookmarks.value = items;
  folders.value = await request<FolderResponse[]>("/folders");
};

async function loadFavorites() {
  loading.value = true;
  loadError.value = "";
  try {
    await loadAllBookmarks();
    toast.show({
      title: "Favorites loaded.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    loadError.value = err instanceof Error ? err.message : "Failed to load favorites.";
    toast.show({
      title: "Failed to load favorites.",
      description: loadError.value,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    loading.value = false;
  }
}

const {
  bookmarkForm,
  confirmDelete,
  deleteOpen,
  deleting,
  loadBookmarkForm,
  modalOpen,
  removeBookmark,
  saveBookmark,
  saving,
} = useBookmarkEditor({
  request,
  refresh: loadFavorites,
  findBookmarkById: (id) => allBookmarks.value.find((item) => item.id === id) || null,
});

const selectedBookmarkFolder = computed({
  get: () =>
    bookmarkFolderOptions.value.find((option) => option.value === bookmarkForm.folder_id) || null,
  set: (value) => {
    bookmarkForm.folder_id = value?.value || "";
  },
});

const toggleFavorite = async (bookmark: BookmarkResponse) => {
  try {
    const updated = await request<BookmarkResponse>("/bookmarks/favorite", {
      method: "PATCH",
      body: JSON.stringify({
        bookmark_id: bookmark.id,
        is_favorite: !bookmark.is_favorite,
      }),
    });

    const index = allBookmarks.value.findIndex((item) => item.id === updated.id);
    if (index >= 0) {
      allBookmarks.value[index] = updated;
    }

    toast.show({
      title: updated.is_favorite ? "Added to favorites." : "Removed from favorites.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    toast.show({
      title: "Failed to update favorite.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  }
};

onMounted(loadFavorites);
</script>
