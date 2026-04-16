<template>
  <UDashboardPanel id="settings">
    <template #header>
      <PageHeaderActions title="Settings" />
    </template>

    <template #body>
      <div class="space-y-6">
        <UPageCard
          title="Theme"
          description="Switch the app appearance between light, dark, and system"
          :ui="{ body: 'space-y-5' }"
        >
          <div class="space-y-3">
            <div>
              <p class="text-sm font-medium text-default">Appearance</p>
              <p class="text-sm text-muted">
                Changes apply immediately and are saved in your browser.
              </p>
            </div>

            <UTabs
              v-model="selectedTheme"
              :items="themeOptions"
              class="w-full max-w-sm"
              color="primary"
              variant="soft"
              orientation="horizontal"
              :ui="{
                list: 'bg-default/60 p-1 rounded-full gap-1',
                trigger:
                  'rounded-full px-4 py-2 text-sm font-medium text-muted transition-colors data-[state=active]:bg-primary data-[state=active]:text-inverted data-[state=active]:shadow-sm',
                indicator: 'hidden',
              }"
            />
          </div>
        </UPageCard>
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type { SettingsWebhookPingResponse, SettingsWebhookResponse } from "~/types";

const { apiBase, defaultApiBase, request } = useBookmarkApi();
const toast = useSingleToast();
const colorMode = useColorMode();
const checking = ref(false);
const webhookLoading = ref(false);
const webhookChecking = ref(false);
const webhookSaving = ref(false);
const webhookConfigured = ref(false);
const webhookForm = reactive({
  webhookUrl: "",
});
const apiBaseUrl = computed(() => apiBase.value || defaultApiBase);

const themeOptions = [
  { label: "System", value: "system", icon: "i-lucide-monitor" },
  { label: "Light", value: "light", icon: "i-lucide-sun-medium" },
  { label: "Dark", value: "dark", icon: "i-lucide-moon-star" },
] as const;

const selectedTheme = computed({
  get: () => colorMode.preference,
  set: (value) => {
    colorMode.preference = value;
  },
});

const checkHealth = async () => {
  checking.value = true;
  try {
    const body = await request<{ status?: string }>("/health");
    if (body?.status === "ok") {
      toast.show({
        title: "API server is reachable.",
        color: "success",
        icon: "i-lucide-check",
      });
    } else {
      toast.show({
        title: "API server responded unexpectedly.",
        color: "warning",
        icon: "i-lucide-circle-alert",
      });
    }
  } catch {
    toast.show({
      title: "API server is unreachable.",
      color: "error",
      icon: "i-lucide-circle-alert",
    });
  } finally {
    checking.value = false;
  }
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

onMounted(loadWebhook);
</script>
