<template>
  <UDashboardPanel id="rss">
    <template #header>
      <UDashboardNavbar title="RSS" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton label="Register" icon="i-lucide-plus" size="sm" @click="openCreateModal" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
        <UPageCard
          title="RSS feeds"
          description="Manage external feed links separately from bookmarks"
          :ui="{ body: 'space-y-4' }"
        >
          <div
            class="flex flex-col gap-3 border-b border-default pb-4 md:flex-row md:items-center md:justify-between"
          >
            <p class="text-xs uppercase tracking-[0.08em] text-muted">
              Total {{ feedList.total }} feeds
            </p>
            <div class="flex items-center gap-2">
              <UButton
                size="sm"
                variant="ghost"
                color="neutral"
                :disabled="page <= 1 || loading"
                @click="setPage(page - 1)"
              >
                Prev
              </UButton>
              <template
                v-for="(item, index) in paginationItems"
                :key="`${item.type}-${index}-${item.value ?? 'ellipsis'}`"
              >
                <UButton
                  v-if="item.type === 'page'"
                  size="sm"
                  :color="item.value === page ? 'primary' : 'neutral'"
                  :variant="item.value === page ? 'solid' : 'ghost'"
                  :disabled="loading"
                  @click="setPage(item.value)"
                >
                  {{ item.label }}
                </UButton>
                <UButton v-else size="sm" variant="ghost" color="neutral" disabled> ... </UButton>
              </template>
              <UButton
                size="sm"
                variant="ghost"
                color="neutral"
                :disabled="page >= pageCount || loading"
                @click="setPage(page + 1)"
              >
                Next
              </UButton>
            </div>
          </div>

          <div v-if="feedList.items.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <UCard
              v-for="feed in feedList.items"
              :key="feed.id"
              class="border border-default bg-elevated/30"
              :ui="{ body: 'space-y-4' }"
            >
              <template #header>
                <div class="space-y-1">
                  <h3 class="text-base font-semibold text-default">
                    {{ feed.title }}
                  </h3>
                  <p class="break-all text-sm text-muted">
                    {{ feed.url }}
                  </p>
                </div>
              </template>

              <p v-if="feed.description" class="text-sm text-default">
                {{ feed.description }}
              </p>
              <p v-else class="text-sm text-muted">No description.</p>

              <div class="flex items-center justify-between gap-3 pt-2">
                <div class="text-xs text-muted">
                  Updated {{ formatDate(feed.updated_at) }}
                </div>
                <div class="flex gap-2">
                  <UButton size="xs" variant="ghost" color="neutral" @click="openEditModal(feed)">
                    Edit
                  </UButton>
                  <UButton size="xs" color="error" variant="ghost" @click="askDelete(feed)">
                    Delete
                  </UButton>
                </div>
              </div>
            </UCard>
          </div>

          <div
            v-else
            class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
          >
            <p v-if="loading">Loading RSS feeds...</p>
            <p v-else-if="loadError">
              {{ loadError }}
            </p>
            <p v-else>No RSS feeds yet.</p>
          </div>
        </UPageCard>

        <UModal
          v-model:open="modalOpen"
          :title="feedForm.id ? 'Edit RSS feed' : 'Register RSS feed'"
          :description="
            feedForm.id ? 'Update the selected feed.' : 'Create a new feed link.'
          "
          :ui="{
            content:
              'w-[calc(100vw-2rem)] max-w-lg max-h-[calc(100dvh-2rem)] sm:max-h-[calc(100dvh-4rem)]',
          }"
        >
          <template #content="{ close }">
            <form class="space-y-4 p-6" @submit.prevent="saveFeed">
              <UFormField label="URL" required class="w-full">
                <UInput
                  v-model="feedForm.url"
                  placeholder="https://example.com/feed.xml"
                  class="w-full"
                />
              </UFormField>

              <UFormField label="Title" required class="w-full">
                <UInput v-model="feedForm.title" placeholder="Feed title" class="w-full" />
              </UFormField>

              <UFormField label="Description" class="w-full">
                <UTextarea
                  v-model="feedForm.description"
                  placeholder="Optional description"
                  :rows="4"
                  class="w-full"
                />
              </UFormField>

              <div class="flex justify-end gap-3">
                <UButton color="neutral" variant="ghost" @click="close"> Cancel </UButton>
                <UButton type="submit" :loading="saving"> Save feed </UButton>
              </div>
            </form>
          </template>
        </UModal>

        <UModal
          v-model:open="deleteOpen"
          title="Delete RSS feed"
          description="This action cannot be undone."
        >
          <template #content>
            <div class="space-y-4 p-6">
              <p class="text-sm text-default">
                Delete
                <strong>{{ pendingFeed?.title }}</strong>
                and remove it from the list?
              </p>
              <div class="flex justify-end gap-3">
                <UButton color="neutral" variant="ghost" @click="closeDelete"> Cancel </UButton>
                <UButton color="error" :loading="deleting" @click="confirmDelete">
                  Delete feed
                </UButton>
              </div>
            </div>
          </template>
        </UModal>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type { RSSFeedListResponse, RSSFeedResponse } from "~/types";

type PaginationItem = { type: "page"; label: string; value: number } | { type: "ellipsis" };

const { request } = useBookmarkApi();
const toast = useSingleToast();

const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const loadError = ref("");
const modalOpen = ref(false);
const deleteOpen = ref(false);
const pendingFeed = ref<RSSFeedResponse | null>(null);
const feedList = ref<RSSFeedListResponse>({
  items: [],
  total: 0,
  page: 1,
  per_page: 20,
  total_pages: 0,
});
const page = ref(1);
const feedForm = reactive({ id: "", url: "", title: "", description: "" });

const pageCount = computed(() => Math.max(feedList.value.total_pages, 1));
const paginationItems = computed<PaginationItem[]>(() => {
  const total = pageCount.value;
  const current = page.value;
  if (total <= 5) {
    return Array.from({ length: total }, (_, index) => ({
      type: "page" as const,
      label: String(index + 1),
      value: index + 1,
    }));
  }
  const pages = new Set<number>([1, total, current]);
  if (current > 1) pages.add(current - 1);
  if (current < total) pages.add(current + 1);
  return Array.from({ length: total }, (_, index) => index + 1)
    .filter((value) => pages.has(value))
    .reduce<PaginationItem[]>((items, value, index, arr) => {
      items.push({ type: "page", label: String(value), value });
      const next = arr[index + 1];
      if (next && next - value > 1) items.push({ type: "ellipsis" });
      return items;
    }, []);
});

const formatDate = (value: string) =>
  new Intl.DateTimeFormat("ja-JP", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const openCreateModal = () => {
  feedForm.id = "";
  feedForm.url = "";
  feedForm.title = "";
  feedForm.description = "";
  modalOpen.value = true;
};

const openEditModal = (feed: RSSFeedResponse) => {
  feedForm.id = String(feed.id);
  feedForm.url = feed.url;
  feedForm.title = feed.title;
  feedForm.description = feed.description || "";
  modalOpen.value = true;
};

const closeModal = () => {
  modalOpen.value = false;
};

const loadFeeds = async () => {
  loading.value = true;
  loadError.value = "";
  try {
    feedList.value = await request<RSSFeedListResponse>(`/rss-feeds?page=${page.value}`);
  } catch (err) {
    loadError.value = err instanceof Error ? err.message : "Failed to load RSS feeds.";
    toast.show({
      title: "Failed to load RSS feeds.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    loading.value = false;
  }
};

const setPage = async (nextPage: number) => {
  page.value = Math.min(Math.max(nextPage, 1), pageCount.value);
  await loadFeeds();
};

const saveFeed = async () => {
  const url = feedForm.url.trim();
  const title = feedForm.title.trim();
  if (!url || !title) {
    toast.show({
      title: "URL and title are required.",
      color: "error",
      icon: "i-lucide-circle-alert",
    });
    return;
  }

  saving.value = true;
  try {
    const body = {
      url,
      title,
      description: feedForm.description.trim() || null,
    };
    if (feedForm.id) {
      await request(`/rss-feeds/${feedForm.id}`, { method: "PATCH", body: JSON.stringify(body) });
      toast.show({
        title: "RSS feed updated.",
        color: "success",
        icon: "i-lucide-check",
      });
    } else {
      await request("/rss-feeds", { method: "POST", body: JSON.stringify(body) });
      toast.show({
        title: "RSS feed created.",
        color: "success",
        icon: "i-lucide-check",
      });
    }
    closeModal();
    await loadFeeds();
  } catch (err) {
    toast.show({
      title: feedForm.id ? "Failed to update RSS feed." : "Failed to create RSS feed.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    saving.value = false;
  }
};

const askDelete = (feed: RSSFeedResponse) => {
  pendingFeed.value = feed;
  deleteOpen.value = true;
};

const closeDelete = () => {
  deleteOpen.value = false;
  pendingFeed.value = null;
};

const confirmDelete = async () => {
  if (!pendingFeed.value) return;
  deleting.value = true;
  try {
    await request(`/rss-feeds/${pendingFeed.value.id}`, { method: "DELETE" });
    toast.show({
      title: "RSS feed deleted.",
      color: "success",
      icon: "i-lucide-check",
    });
    closeDelete();
    await loadFeeds();
  } catch (err) {
    toast.show({
      title: "Failed to delete RSS feed.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    deleting.value = false;
  }
};

onMounted(loadFeeds);
</script>
