<template>
    <UDashboardGroup unit="rem">
        <UDashboardSidebar
            id="default"
            v-model:open="open"
            collapsible
            resizable
            class="bg-elevated/25"
            :ui="{ footer: 'lg:border-t lg:border-default' }"
        >
            <template #default="{ collapsed }">
                <UNavigationMenu
                    :collapsed="collapsed"
                    :items="primaryLinks"
                    orientation="vertical"
                    tooltip
                    popover
                />
                <UNavigationMenu
                    :collapsed="collapsed"
                    :items="secondaryLinks"
                    orientation="vertical"
                    tooltip
                    class="mt-auto"
                />
            </template>
        </UDashboardSidebar>

        <slot />
    </UDashboardGroup>
</template>
<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";

const route = useRoute();
const toast = useSingleToast();
const { folders, tags, refresh } = useSidebarCatalog();

const open = ref(false);

const closeSidebar = () => {
  open.value = false;
};

const primaryLinks = computed<NavigationMenuItem[]>(() => [
    {
        label: "Dashboard",
        icon: "i-lucide-house",
        to: "/",
        onSelect: closeSidebar,
    },
    {
        label: "Bookmarks",
        icon: "i-lucide-bookmark",
        to: "/bookmarks",
        onSelect: closeSidebar,
    },
    {
        label: "Folders",
        icon: "i-lucide-folder",
        to: "/folders",
        defaultOpen: false,
        children: folders.value.map((folder) => ({
            label: folder.name,
            to: `/folders/${folder.id}`,
            exact: true,
            onSelect: closeSidebar,
        })),
    },
    {
        label: "Tags",
        icon: "i-lucide-tag",
        to: "/tags",
        defaultOpen: false,
        children: tags.value.map((tag) => ({
            label: tag.name,
            to: `/tags/${tag.id}`,
            exact: true,
            onSelect: closeSidebar,
        })),
    },
]);

const secondaryLinks = computed<NavigationMenuItem[]>(() => [
    {
        label: "Settings",
        icon: "i-lucide-settings",
        to: "/settings",
        onSelect: closeSidebar,
    },
]);

const groups = computed(() => [
    {
        id: "links",
        label: "Go to",
        items: [...primaryLinks.value, ...secondaryLinks.value],
    },
    {
        id: "code",
        label: "Code",
        items: [
            {
                id: "source",
                label: "View page source",
                icon: "i-simple-icons-github",
                to: `https://github.com/nuxt-ui-templates/dashboard/blob/main/app/pages${route.path === "/" ? "/index" : route.path}.vue`,
                target: "_blank",
            },
        ],
    },
]);

onMounted(async () => {
    await refresh();

    const cookie = useCookie("cookie-consent");
    if (cookie.value === "accepted") {
        return;
    }

    toast.show({
        title: "We use first-party cookies to enhance your experience on our website.",
        duration: 0,
        close: false,
        actions: [
            {
                label: "Accept",
                color: "neutral",
                variant: "outline",
                onClick: () => {
                    cookie.value = "accepted";
                },
            },
            {
                label: "Opt out",
                color: "neutral",
                variant: "ghost",
            },
        ],
    });
});
</script>
