<template>
    <UDashboardPanel id="tag-detail">
        <template #header>
            <UDashboardNavbar title="Tag" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageCard
                    title="Tag details"
                    description="Inspect and manage a single tag"
                    :ui="{ body: 'space-y-4' }"
                >
                    <div v-if="state === 'loading'" class="space-y-3">
                        <USkeleton class="h-6 w-28" />
                        <USkeleton class="h-8 w-56" />
                        <USkeleton class="h-4 w-full max-w-md" />
                    </div>

                    <UAlert
                        v-else-if="state === 'error'"
                        title="Failed to load tag"
                        :description="errorMessage"
                        color="error"
                        variant="soft"
                    />

                    <UAlert
                        v-else-if="state === 'not-found'"
                        title="Tag not found"
                        description="The requested tag does not exist."
                        color="warning"
                        variant="soft"
                    />

                    <div v-else-if="tag" class="space-y-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <UBadge color="primary" variant="soft">
                                Tag #{{ tag.id }}
                            </UBadge>
                            <span class="text-sm text-muted">
                                {{ bookmarks.length }} bookmark{{ bookmarks.length === 1 ? "" : "s" }}
                            </span>
                        </div>
                        <h1 class="text-2xl font-semibold text-default">
                            {{ tag.name }}
                        </h1>
                        <div class="flex flex-wrap gap-3">
                            <UButton to="/tags" variant="ghost" size="sm">
                                Back to tags
                            </UButton>
                            <UButton color="neutral" variant="soft" size="sm" icon="i-lucide-pencil" @click="openEdit">
                                <span class="sr-only">Edit tag</span>
                            </UButton>
                            <UButton color="error" variant="soft" size="sm" icon="i-lucide-trash-2" @click="confirmOpen = true">
                                <span class="sr-only">Delete tag</span>
                            </UButton>
                        </div>
                    </div>
                </UPageCard>

                <UPageCard
                    title="Bookmarks with this tag"
                    description="Bookmarks associated with the selected tag"
                    :ui="{ body: 'space-y-3' }"
                >
                    <div v-if="state === 'loading'" class="space-y-3">
                        <USkeleton v-for="n in 3" :key="n" class="h-20 w-full" />
                    </div>

                    <div v-else-if="bookmarks.length" class="grid gap-3">
                        <CardsBookmarkPreviewCard
                            v-for="bookmark in bookmarks"
                            :key="bookmark.id"
                            :bookmark="bookmark"
                            :max-tags="0"
                        />
                    </div>
                    <div
                        v-else
                        class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
                    >
                        No bookmarks with this tag.
                    </div>
                </UPageCard>

                <UModal
                    v-model:open="editOpen"
                    title="Edit tag"
                    description="Rename this tag."
                >
                    <template #content="{ close }">
                        <form class="space-y-4 p-6" @submit.prevent="saveTag">
                            <UFormField label="Tag name">
                                <UInput v-model="editForm.name" />
                            </UFormField>
                            <div class="flex justify-end gap-3">
                                <UButton color="neutral" variant="ghost" @click="close">
                                    Cancel
                                </UButton>
                                <UButton type="submit" :loading="saving">
                                    Save changes
                                </UButton>
                            </div>
                        </form>
                    </template>
                </UModal>

                <UModal
                    v-model:open="confirmOpen"
                    title="Delete tag"
                    description="This action cannot be undone."
                >
                    <template #content>
                        <div class="space-y-4 p-6">
                            <p class="text-sm text-default">
                                Delete <strong>{{ tag?.name }}</strong>?
                            </p>
                            <div class="flex justify-end gap-3">
                                <UButton color="neutral" variant="ghost" @click="confirmOpen = false">
                                    Cancel
                                </UButton>
                                <UButton color="error" :loading="deleting" @click="deleteTag">
                                    Delete tag
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
import type { BookmarkListResponse, TagResponse } from "~/types";

const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();
const toast = useSingleToast();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();

const state = ref<"loading" | "ready" | "error" | "not-found">("loading");
const errorMessage = ref("");
const tag = ref<TagResponse | null>(null);
const bookmarks = ref<BookmarkListResponse["items"]>([]);
const editOpen = ref(false);
const confirmOpen = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editForm = reactive({ name: "" });

const loadTag = async () => {
    state.value = "loading";
    errorMessage.value = "";

    try {
        const [tagsRes, bookmarksRes] = await Promise.all([
            request("/tags"),
            request(`/bookmarks?tag_id=${route.params.id}`),
        ]);

        tag.value =
            tagsRes.find(
                (item: TagResponse) => String(item.id) === String(route.params.id),
            ) || null;
        bookmarks.value = bookmarksRes.items || [];
        state.value = tag.value ? "ready" : "not-found";
    } catch (err) {
        tag.value = null;
        bookmarks.value = [];
        errorMessage.value =
            err instanceof Error ? err.message : "Failed to load tag.";
        state.value = "error";
    }
};

const openEdit = () => {
    if (!tag.value) return;
    editForm.name = tag.value.name;
    editOpen.value = true;
};

const saveTag = async () => {
    if (!tag.value) return;
    const name = editForm.name.trim();
    if (!name) {
        toast.show({
            title: "Tag name is required.",
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        return;
    }

    saving.value = true;
    try {
        await request(`/tags/${tag.value.id}`, {
            method: "PATCH",
            body: JSON.stringify({ name }),
        });
        await refreshSidebarCatalog();
        await loadTag();
        editOpen.value = false;
        toast.show({
            title: "Tag updated.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        toast.show({
            title: "Failed to update tag.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        saving.value = false;
    }
};

const deleteTag = async () => {
    if (!tag.value) return;
    deleting.value = true;
    try {
        await request(`/tags/${tag.value.id}`, { method: "DELETE" });
        await refreshSidebarCatalog();
        toast.show({
            title: "Tag deleted.",
            color: "success",
            icon: "i-lucide-check",
        });
        await router.push("/tags");
    } catch (err) {
        toast.show({
            title: "Failed to delete tag.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        deleting.value = false;
        confirmOpen.value = false;
    }
};

watch(
    () => route.params.id,
    () => {
        void loadTag();
    },
);

onMounted(loadTag);
</script>
