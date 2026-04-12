<template>
  <UDashboardPanel id="settings">
    <template #header>
      <UDashboardNavbar title="Settings" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div class="space-y-6">
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
                icon="i-lucide-refresh-cw"
                :loading="webhookLoading"
                @click="loadWebhook"
              >
                Refresh
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
          title="Theme"
          description="Switch the app appearance between light, dark, and system"
          :ui="{ body: 'space-y-5' }"
        >
          <div class="space-y-3">
            <div>
              <p class="text-sm font-medium text-default">Appearance</p>
              <p class="text-sm text-muted">Changes apply immediately and are saved in your browser.</p>
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

        <UPageCard
          title="API Base URL"
          description="Configured from runtime environment"
          :ui="{ body: 'space-y-5' }"
        >
          <div class="space-y-2">
            <UFormField label="Current value" description="This is the base URL used by the app">
              <div class="flex flex-wrap items-center gap-3">
                <p
                  class="rounded-xl border border-default bg-elevated px-4 py-3 text-sm text-default"
                >
                  {{ form.apiBaseUrl || defaultApiBase }}
                </p>

                <UButton
                  icon="i-lucide-heart-pulse"
                  variant="soft"
                  :loading="checking"
                  @click="checkHealth"
                >
                  /health
                </UButton>
              </div>
            </UFormField>
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
const webhookSaving = ref(false);
const webhookConfigured = ref(false);
const form = reactive({
  apiBaseUrl: "",
});
const webhookForm = reactive({
  webhookUrl: "",
});

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

const syncSettings = () => {
  form.apiBaseUrl = apiBase.value || defaultApiBase;
};

const checkHealth = async () => {
  if (!form.apiBaseUrl) {
    toast.show({
      title: "API base URL is not configured.",
      color: "error",
      icon: "i-lucide-circle-alert",
    });
    return;
  }

  checking.value = true;
  try {
    const res = await fetch(`${form.apiBaseUrl.replace(/\/$/, "")}/health`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const body = await res.json();
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
    await request<SettingsWebhookPingResponse>("/settings/webhook/ping", {
      method: "POST",
      body: JSON.stringify({ webhook_url: webhookUrl }),
    });
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

onMounted(async () => {
  syncSettings();
  await loadWebhook();
});
</script>
