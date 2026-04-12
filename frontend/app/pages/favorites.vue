<template>
  <UDashboardPanel id="favorites">
    <template #header>
      <UDashboardNavbar title="Favorites" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            label="Refresh"
            icon="i-lucide-refresh-cw"
            size="sm"
            color="neutral"
            variant="ghost"
            :loading="loading"
            @click="loadFavorites"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
        <UPageCard
          title="Favorite bookmarks"
          description="Bookmarks marked with a star through the dedicated favorite API"
          :ui="{ body: 'space-y-4' }"
        >
          <div class="flex flex-col gap-3 border-b border-default pb-4 md:flex-row md:items-center md:justify-between">
            <p class="text-xs uppercase tracking-[0.08em] text-muted">
              {{ favoriteBookmarks.length }} favorites
            </p>
            <p class="text-xs uppercase tracking-[0.08em] text-muted">
              {{ allBookmarks.length }} loaded
            </p>
          </div>

          <div v-if="loading" class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted">
            Loading favorites...
          </div>

          <div v-else-if="loadError" class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted">
            {{ loadError }}
          </div>

          <div v-else-if="favoriteBookmarks.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="bookmark in favoriteBookmarks"
              :key="bookmark.id"
              class="rounded-2xl border border-default bg-elevated/40 p-4 space-y-4"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <NuxtLink
                    :to="bookmark.url"
                    external
                    target="_blank"
                    rel="noreferrer"
                    class="block truncate text-base font-semibold text-default hover:underline"
                  >
                    {{ bookmark.title }}
                  </NuxtLink>
                  <p class="mt-1 break-all text-sm text-muted">
                    {{ bookmark.url }}
                  </p>
                </div>

                <UButton
                  type="button"
                  size="xs"
                  variant="soft"
                  color="warning"
                  :icon="bookmark.is_favorite ? 'i-lucide-star' : 'i-lucide-star-off'"
                  :loading="togglingBookmarkId === bookmark.id"
                  @click.stop="toggleFavorite(bookmark)"
                >
                  <span class="sr-only">
                    {{ bookmark.is_favorite ? "Unfavorite" : "Favorite" }}
                  </span>
                </UButton>
              </div>

              <p v-if="bookmark.description" class="text-sm text-default">
                {{ bookmark.description }}
              </p>

              <div v-if="bookmark.tags.length" class="flex flex-wrap gap-2">
                <UBadge
                  v-for="tag in bookmark.tags"
                  :key="tag.id"
                  size="xs"
                  color="neutral"
                  variant="subtle"
                  :ui="{ rounded: 'rounded-full' }"
                >
                  {{ tag.name }}
                </UBadge>
              </div>
            </article>
          </div>

          <div v-else class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted">
            No favorites yet.
          </div>
        </UPageCard>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type { BookmarkResponse, BookmarkListResponse } from "~/types";

const { request } = useBookmarkApi();
const toast = useSingleToast();

const loading = ref(false);
const togglingBookmarkId = ref<number | null>(null);
const loadError = ref("");
const allBookmarks = ref<BookmarkResponse[]>([]);

const favoriteBookmarks = computed(() =>
  allBookmarks.value.filter((bookmark) => bookmark.is_favorite),
);

const loadAllBookmarks = async () => {
  const firstPage = await request<BookmarkListResponse>("/bookmarks?per_page=100&page=1");
  const items = [...firstPage.items];

  for (let page = 2; page <= firstPage.total_pages; page += 1) {
    const nextPage = await request<BookmarkListResponse>(`/bookmarks?per_page=100&page=${page}`);
    items.push(...nextPage.items);
  }

  allBookmarks.value = items;
};

const loadFavorites = async () => {
  loading.value = true;
  loadError.value = "";
  try {
    await loadAllBookmarks();
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
};

const toggleFavorite = async (bookmark: BookmarkResponse) => {
  togglingBookmarkId.value = bookmark.id;
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
  } finally {
    togglingBookmarkId.value = null;
  }
};

onMounted(loadFavorites);
</script>
