<template>
  <UDashboardGroup unit="rem">
    <UDashboardSidebar
      id="default"
      v-model:open="open"
      collapsible
      class="bg-elevated/25 lg:sticky lg:top-0 lg:h-dvh"
      :ui="{ footer: 'lg:border-t lg:border-default' }"
    >
      <template #default="{ collapsed }">
        <NavigationSidebarNav
          :collapsed="collapsed"
          :primary-links="primaryLinks"
          :secondary-links="secondaryLinks"
          :primary-model-value="sidebarOpenItems"
          @navigate="closeSidebar"
        />
      </template>

      <template #footer="{ collapsed }">
        <div class="flex flex-col gap-2 w-full">
          <UButton
            :label="collapsed ? undefined : 'GitHub'"
            icon="i-simple-icons-github"
            color="neutral"
            variant="ghost"
            :block="collapsed"
            to="https://github.com/Kai17-a/browser-bookmark-manager"
            target="_blank"
          />

          <UTooltip :delay-duration="0" text="Preparing...">
            <UButton
              :label="collapsed ? undefined : 'Extension'"
              icon="i-lucide-puzzle"
              color="neutral"
              variant="ghost"
              :block="collapsed"
              to=""
              target="_blank"
              disabled
            />
          </UTooltip>
        </div>
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const { folders, tags, refresh } = useSidebarCatalog();
const { checked: healthChecked, ok: healthOk, check: checkApiHealth } = useApiHealth();
const toast = useSingleToast();

const open = ref(true);

const closeSidebar = () => {
  open.value = false;
};

const isActive = (path: string) => route.path === path;
const isActivePrefix = (path: string) => route.path === path || route.path.startsWith(`${path}/`);
const sidebarOpenItems = computed(() => [
  ...(isActivePrefix("/folders") ? ["folders"] : []),
  ...(isActivePrefix("/tags") ? ["tags"] : []),
]);

const primaryLinks = computed<NavigationMenuItem[]>(() => [
  {
    label: "Dashboard",
    icon: "i-lucide-house",
    to: "/",
    active: isActive("/"),
    onSelect: closeSidebar,
  },
  {
    label: "Bookmarks",
    icon: "i-lucide-bookmark",
    to: "/bookmarks",
    active: isActivePrefix("/bookmarks"),
    onSelect: closeSidebar,
  },
  {
    label: "Favorites",
    icon: "i-lucide-star",
    to: "/favorites",
    active: isActive("/favorites"),
    onSelect: closeSidebar,
  },
  {
    label: "RSS",
    icon: "i-lucide-rss",
    to: "/rss",
    active: isActive("/rss"),
    onSelect: closeSidebar,
  },
  {
    label: "Folders",
    icon: "i-lucide-folder",
    to: "/folders",
    value: "folders",
    active: isActivePrefix("/folders"),
    defaultOpen: false,
    children: folders.value.map((folder) => ({
      label: folder.name,
      to: `/folders/${folder.id}`,
      exact: true,
      active: isActive(`/folders/${folder.id}`),
      onSelect: closeSidebar,
    })),
  },
  {
    label: "Tags",
    icon: "i-lucide-tag",
    to: "/tags",
    value: "tags",
    active: isActivePrefix("/tags"),
    defaultOpen: false,
    children: tags.value.map((tag) => ({
      label: tag.name,
      to: `/tags/${tag.id}`,
      exact: true,
      active: isActive(`/tags/${tag.id}`),
      onSelect: closeSidebar,
    })),
  },
]);

const secondaryLinks = computed<NavigationMenuItem[]>(() => [
  {
    label: "Settings",
    icon: "i-lucide-settings",
    to: "/settings",
    active: isActive("/settings"),
    onSelect: closeSidebar,
  },
]);

onMounted(async () => {
  await refresh();

  if (!healthChecked.value) {
    await checkApiHealth();
    toast.show({
      title: healthOk.value ? "API server is reachable." : "API server responded unexpectedly.",
      color: healthOk.value ? "success" : "warning",
      icon: healthOk.value ? "i-lucide-check" : "i-lucide-circle-alert",
    });
  }
});
</script>
