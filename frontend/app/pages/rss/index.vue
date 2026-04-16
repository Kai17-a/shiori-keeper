<template>
  <UDashboardPanel id="rss">
    <template #header>
      <PageHeaderActions title="RSS" />
    </template>

    <template #body>
      <div class="space-y-6">
        <div class="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <UPageCard
            title="Webhook"
            description="Configure the global Discord webhook used by RSS execution"
            :ui="{ body: 'space-y-5' }"
          >
            <form class="space-y-4" @submit.prevent="saveWebhook">
              <UFormField
                label="Discord webhook URL"
                description="This single webhook setting is shared across app integrations."
                class="w-full"
              >
                <UInput
                  v-model="webhookForm.webhookUrl"
                  class="w-full"
                  placeholder="https://discord.com/api/webhooks/..."
                />
              </UFormField>

              <div class="flex flex-wrap items-center gap-3">
                <UButton
                  type="button"
                  color="neutral"
                  variant="ghost"
                  icon="i-lucide-bell-ring"
                  :loading="webhookChecking"
                  @click="pingWebhook()"
                >
                  Test
                </UButton>
                <UButton type="submit" icon="i-lucide-save" :loading="webhookSaving">
                  Save webhook
                </UButton>
              </div>

              <p class="text-sm text-muted">
                <span v-if="webhookConfigured">Webhook is configured.</span>
                <span v-else>No webhook is configured yet.</span>
              </p>
            </form>
          </UPageCard>

          <UPageCard
            title="RSS periodic execution"
            description="Enable or disable the scheduled RSS batch process"
            :ui="{ body: 'space-y-4' }"
          >
            <div class="space-y-3">
              <div class="space-y-1">
                <p class="text-sm font-medium text-default">Run on schedule</p>
                <p class="text-sm text-muted">
                  When enabled, the batch process is allowed to run RSS delivery jobs once
                  every hour.
                </p>
              </div>
              <USwitch v-model="rssExecutionEnabled" :loading="rssExecutionLoading" />
            </div>
          </UPageCard>
        </div>

        <UPageCard :ui="{ body: 'space-y-4' }">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-default">RSS feeds</h2>
              <p class="text-sm text-muted">Manage external feed links separately from bookmarks</p>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <UButton
                icon="i-lucide-refresh-cw"
                color="neutral"
                variant="ghost"
                size="sm"
                :loading="loading"
                @click="refreshFeeds"
              >
                Refresh
              </UButton>
              <UButton label="Register" icon="i-lucide-plus" size="sm" @click="openCreateModal" />
            </div>
          </div>

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
            <RSSFeedCard
              v-for="feed in feedList.items"
              :key="feed.id"
              :feed="feed"
              :to="`/rss/${feed.id}`"
              :running="executingFeedId === feed.id"
              @edit="openEditModal"
              @execute="executeFeed"
              @remove="askDelete"
            />
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

        <RSSFeedEditorModal
          v-model:open="modalOpen"
          :form="feedForm"
          :title="feedForm.id ? 'Edit RSS feed' : 'Register RSS feed'"
          :description="feedForm.id ? 'Update the selected feed.' : 'Create a new feed link.'"
          title-placeholder="Feed title"
          url-placeholder="https://example.com/feed.xml"
          description-placeholder="Optional description"
          submit-label="Save feed"
          :saving="saving"
          @save="saveFeed"
        />

        <DeleteConfirmModal
          v-model:open="deleteOpen"
          title="Delete RSS feed"
          :subject="pendingFeed?.title"
          confirm-label="Delete feed"
          :loading="deleting"
          @cancel="pendingFeed = null"
          @confirm="confirmDelete"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type {
  RSSFeedExecuteResponse,
  RSSFeedListResponse,
  RSSFeedResponse,
  SettingsRssExecutionResponse,
  SettingsWebhookPingResponse,
  SettingsWebhookResponse,
} from "~/types";

type PaginationItem = { type: "page"; label: string; value: number } | { type: "ellipsis" };

const { request } = useBookmarkApi();
const toast = useSingleToast();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();

const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);
const webhookLoading = ref(false);
const webhookChecking = ref(false);
const webhookSaving = ref(false);
const webhookConfigured = ref(false);
const rssExecutionLoading = ref(false);
const rssExecutionSaving = ref(false);
const executingFeedId = ref<number | null>(null);
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
const feedForm = reactive({ id: "", title: "", url: "", description: "" });
const webhookForm = reactive({
  webhookUrl: "",
});
const rssExecutionEnabled = ref(false);

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

const pingWebhook = async (webhookUrl = webhookForm.webhookUrl.trim()) => {
  webhookChecking.value = true;
  try {
    await request<SettingsWebhookPingResponse>("/settings/webhook/ping", {
      method: "POST",
      body: JSON.stringify({ webhook_url: webhookUrl }),
    });
    toast.show({
      title: "Webhook endpoint is reachable.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    toast.show({
      title: "Failed to ping webhook setting.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    webhookChecking.value = false;
  }
};

const loadWebhook = async () => {
  webhookLoading.value = true;
  try {
    const response = await request<SettingsWebhookResponse>("/settings/webhook");
    webhookForm.webhookUrl = response.webhook_url;
    webhookConfigured.value = true;
  } catch (err) {
    webhookForm.webhookUrl = "";
    webhookConfigured.value = false;
    if (err instanceof Error && err.message.includes("404")) {
      return;
    }
    toast.show({
      title: "Failed to load webhook setting.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    webhookLoading.value = false;
  }
};

const saveWebhook = async () => {
  const webhookUrl = webhookForm.webhookUrl.trim();
  if (!webhookUrl) {
    toast.show({
      title: "Webhook URL is required.",
      color: "error",
      icon: "i-lucide-circle-alert",
    });
    return;
  }

  webhookSaving.value = true;
  try {
    const response = await request<SettingsWebhookResponse>("/settings/webhook", {
      method: "PUT",
      body: JSON.stringify({ webhook_url: webhookUrl }),
    });
    webhookForm.webhookUrl = response.webhook_url;
    webhookConfigured.value = true;
    toast.show({
      title: "Webhook setting saved.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    toast.show({
      title: "Failed to save webhook setting.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    webhookSaving.value = false;
  }
};

const loadRssExecution = async () => {
  rssExecutionLoading.value = true;
  try {
    const response = await request<SettingsRssExecutionResponse>("/settings/rss-execution");
    rssExecutionEnabled.value = response.enabled;
  } catch (err) {
    toast.show({
      title: "Failed to load RSS execution setting.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    rssExecutionLoading.value = false;
  }
};

watch(rssExecutionEnabled, async (enabled, previous) => {
  if (rssExecutionLoading.value || enabled === previous) return;
  rssExecutionSaving.value = true;
  try {
    const response = await request<SettingsRssExecutionResponse>("/settings/rss-execution", {
      method: "PUT",
      body: JSON.stringify({ enabled }),
    });
    rssExecutionEnabled.value = response.enabled;
    toast.show({
      title: response.enabled
        ? "RSS periodic execution enabled."
        : "RSS periodic execution disabled.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    rssExecutionEnabled.value = previous;
    toast.show({
      title: "Failed to update RSS execution setting.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    rssExecutionSaving.value = false;
  }
});

type LoadToastKind = "loaded" | "refreshed";

const loadFeeds = async (showToast = true, toastKind: LoadToastKind = "loaded") => {
  loading.value = true;
  loadError.value = "";
  try {
    feedList.value = await request<RSSFeedListResponse>(`/rss-feeds?page=${page.value}`);
    if (showToast) {
      toast.show({
        title: toastKind === "loaded" ? "RSS feeds loaded." : "RSS feeds refreshed.",
        color: "success",
        icon: "i-lucide-check",
      });
    }
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

const refreshFeeds = async () => {
  await loadFeeds(true, "refreshed");
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
      await refreshSidebarCatalog();
      toast.show({
        title: "RSS feed updated.",
        color: "success",
        icon: "i-lucide-check",
      });
    } else {
      await request("/rss-feeds", { method: "POST", body: JSON.stringify(body) });
      await refreshSidebarCatalog();
    }
    closeModal();
    await loadFeeds(false);
    toast.show({
      title: feedForm.id ? "RSS feed updated." : "RSS feed created.",
      color: "success",
      icon: "i-lucide-check",
    });
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

const executeFeed = async (feed: RSSFeedResponse) => {
  executingFeedId.value = feed.id;
  try {
    const result = await request<RSSFeedExecuteResponse>(`/rss-feeds/${feed.id}/execute`, {
      method: "POST",
    });
    toast.show({
      title: "RSS feed executed.",
      description: result.message ?? `Delivered to ${result.webhook_url}`,
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    toast.show({
      title: "Failed to execute RSS feed.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    executingFeedId.value = null;
  }
};

const confirmDelete = async () => {
  if (!pendingFeed.value) return;
  deleting.value = true;
  try {
    await request(`/rss-feeds/${pendingFeed.value.id}`, { method: "DELETE" });
    await refreshSidebarCatalog();
    deleteOpen.value = false;
    pendingFeed.value = null;
    await loadFeeds(false);
    toast.show({
      title: "RSS feed deleted.",
      color: "success",
      icon: "i-lucide-check",
    });
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

onMounted(async () => {
  await Promise.all([loadFeeds(), loadWebhook(), loadRssExecution()]);
});
</script>
