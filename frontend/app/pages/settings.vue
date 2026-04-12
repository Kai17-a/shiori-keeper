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
const { apiBase, defaultApiBase } = useBookmarkApi();
const toast = useSingleToast();
const checking = ref(false);
const form = reactive({
  apiBaseUrl: "",
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

onMounted(async () => {
  syncSettings();
});
</script>
