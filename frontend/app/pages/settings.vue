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
const colorMode = useColorMode();

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
</script>
