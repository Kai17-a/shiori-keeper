<template>
    <UDashboardPanel id="home">
        <template #header>
            <UDashboardNavbar title="Dashboard" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageGrid class="grid gap-4 lg:grid-cols-3">
                    <CardsStatCard
                        v-for="stat in stats"
                        :key="stat.title"
                        :title="stat.title"
                        :to="stat.to"
                        :value="stat.value"
                    />
                </UPageGrid>

                <UPageCard
                    title="Bookmarks"
                    description="Latest bookmarks at a glance"
                    :ui="{ body: 'space-y-4' }"
                >
                    <div v-if="bookmarks.items.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        <CardsBookmarkPreviewCard
                            v-for="bookmark in bookmarks.items.slice(0, 6)"
                            :key="bookmark.id"
                            :bookmark="bookmark"
                        />
                    </div>

                    <div v-else class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted">
                        <p>No bookmarks yet.</p>
                    </div>

                    <div class="flex items-center justify-between gap-3">
                        <p class="text-xs uppercase tracking-[0.08em] text-muted">
                            {{ bookmarks.total }} items
                        </p>
                        <UButton to="/bookmarks" icon="i-lucide-arrow-right">
                            More
                        </UButton>
                    </div>
                </UPageCard>

                <UPageGrid class="grid gap-4 lg:grid-cols-2">
                    <UPageCard
                        title="Folders"
                        description="Saved folders"
                        :ui="{ body: 'space-y-3' }"
                    >
                        <div class="flex flex-wrap gap-2">
                            <UButton
                                v-for="folder in folders.slice(0, 10)"
                                :key="folder.id"
                                :label="folder.name"
                                color="neutral"
                                variant="soft"
                                size="xs"
                                class="rounded-full"
                                :to="`/folders/${folder.id}`"
                            />
                        </div>
                        <div class="flex items-center justify-between gap-3">
                            <p class="text-xs uppercase tracking-[0.08em] text-muted">
                                {{ folders.length }} folders
                            </p>
                            <UButton to="/folders" variant="ghost" size="sm">
                                More
                            </UButton>
                        </div>
                    </UPageCard>

                    <UPageCard
                        title="Tags"
                        description="Saved tags"
                        :ui="{ body: 'space-y-3' }"
                    >
                        <div class="flex flex-wrap gap-2">
                            <UButton
                                v-for="tag in tags.slice(0, 10)"
                                :key="tag.id"
                                :label="tag.name"
                                color="neutral"
                                variant="soft"
                                size="xs"
                                class="rounded-full"
                                :to="`/tags/${tag.id}`"
                            />
                        </div>
                        <div class="flex items-center justify-between gap-3">
                            <p class="text-xs uppercase tracking-[0.08em] text-muted">
                                {{ tags.length }} tags
                            </p>
                            <UButton to="/tags" variant="ghost" size="sm">
                                More
                            </UButton>
                        </div>
                    </UPageCard>
                </UPageGrid>
            </div>
        </template>
    </UDashboardPanel>
</template>

<script setup lang="ts">
import type {
    BookmarkListResponse,
    FolderResponse,
    TagResponse,
} from "~/types";

const { request } = useBookmarkApi();
const toast = useSingleToast();
const bookmarks = ref<BookmarkListResponse>({
    items: [],
    total: 0,
    page: 1,
    per_page: 20,
    total_pages: 0,
});
const folders = ref<FolderResponse[]>([]);
const tags = ref<TagResponse[]>([]);

const stats = ref([
    {
        title: "Total bookmarks",
        to: "/bookmarks",
        value: 0,
    },
    {
        title: "Folders",
        to: "/folders",
        value: 0,
    },
    {
        title: "Tags",
        to: "/tags",
        value: 0,
    },
]);

onMounted(async () => {
    try {
        const [healthRes, bookmarksRes, tagsRes, foldersRes] =
            await Promise.all([
                request("/health"),
                request("/bookmarks"),
                request("/tags"),
                request("/folders"),
        ]);

        bookmarks.value = bookmarksRes;
        tags.value = tagsRes;
        folders.value = foldersRes;
        toast.show({
            title:
                healthRes?.status === "ok"
                    ? "API server is reachable."
                    : "API server responded unexpectedly.",
            color: healthRes?.status === "ok" ? "success" : "warning",
            icon:
                healthRes?.status === "ok"
                    ? "i-lucide-check"
                    : "i-lucide-circle-alert",
        });

        stats.value[0].value = bookmarks.value.total;
        stats.value[1].value = folders.value.length;
        stats.value[2].value = tags.value.length;
    } catch (error) {
        toast.show({
            title: "Failed to load dashboard.",
            description:
                error instanceof Error ? error.message : "Unknown error",
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        console.error("Failed to load data:", error);
    }
});
</script>
