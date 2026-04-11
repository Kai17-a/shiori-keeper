<template>
    <UDashboardPanel id="folder-detail">
        <template #header>
            <UDashboardNavbar title="Folder" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageCard
                    title="Folder details"
                    description="Inspect and manage a single folder"
                    :ui="{ body: 'space-y-4' }"
                >
                    <div v-if="state === 'loading'" class="space-y-3">
                        <USkeleton class="h-6 w-32" />
                        <USkeleton class="h-8 w-64" />
                        <USkeleton class="h-4 w-full max-w-md" />
                    </div>

                    <UAlert
                        v-else-if="state === 'error'"
                        title="Failed to load folder"
                        :description="errorMessage"
                        color="error"
                        variant="soft"
                    />

                    <UAlert
                        v-else-if="state === 'not-found'"
                        title="Folder not found"
                        description="The requested folder does not exist."
                        color="warning"
                        variant="soft"
                    />

                    <div v-else-if="folder" class="space-y-3">
                        <div class="flex flex-wrap items-center gap-2">
                            <UBadge color="primary" variant="soft">
                                Folder #{{ folder.id }}
                            </UBadge>
                            <span class="text-sm text-muted">
                                Created {{ folder.created_at }}
                            </span>
                        </div>
                        <h1 class="text-2xl font-semibold text-default">
                            {{ folder.name }}
                        </h1>
                        <p v-if="folder.description" class="text-sm text-muted">
                            {{ folder.description }}
                        </p>
                        <p class="text-sm text-muted">
                            {{ bookmarks.length }} bookmark{{ bookmarks.length === 1 ? "" : "s" }} in this folder.
                        </p>
                        <div class="flex flex-wrap gap-3">
                            <UButton to="/folders" variant="ghost" size="sm">
                                Back to folders
                            </UButton>
                            <UButton color="neutral" variant="soft" size="sm" icon="i-lucide-pencil" @click="openEdit">
                                <span class="sr-only">Edit folder</span>
                            </UButton>
                            <UButton color="error" variant="soft" size="sm" icon="i-lucide-trash-2" @click="confirmOpen = true">
                                <span class="sr-only">Delete folder</span>
                            </UButton>
                        </div>
                    </div>
                </UPageCard>

                <UPageCard
                    title="Bookmarks in this folder"
                    description="Bookmarks associated with the selected folder"
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
                        No bookmarks in this folder.
                    </div>
                </UPageCard>

                <UModal
                    v-model:open="editOpen"
                    title="Edit folder"
                    description="Rename this folder."
                >
                    <template #content="{ close }">
                        <form class="space-y-4 p-6" @submit.prevent="saveFolder">
                            <UFormField label="Folder name">
                                <UInput v-model="editForm.name" />
                            </UFormField>
                            <UFormField label="Description">
                                <UTextarea v-model="editForm.description" :rows="3" />
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
                    title="Delete folder"
                    description="This action cannot be undone."
                >
                    <template #content>
                        <div class="space-y-4 p-6">
                            <p class="text-sm text-default">
                                Delete <strong>{{ folder?.name }}</strong>?
                            </p>
                            <div class="flex justify-end gap-3">
                                <UButton color="neutral" variant="ghost" @click="confirmOpen = false">
                                    Cancel
                                </UButton>
                                <UButton color="error" :loading="deleting" @click="deleteFolder">
                                    Delete folder
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
import type { BookmarkListResponse, FolderResponse } from "~/types";

const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();
const toast = useSingleToast();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();

const state = ref<"loading" | "ready" | "error" | "not-found">("loading");
const errorMessage = ref("");
const folder = ref<FolderResponse | null>(null);
const bookmarks = ref<BookmarkListResponse["items"]>([]);
const editOpen = ref(false);
const confirmOpen = ref(false);
const saving = ref(false);
const deleting = ref(false);
const editForm = reactive({ name: "", description: "" });

const loadFolder = async () => {
    state.value = "loading";
    errorMessage.value = "";

    try {
        const [foldersRes, bookmarksRes] = await Promise.all([
            request("/folders"),
            request(`/bookmarks?folder_id=${route.params.id}`),
        ]);

        folder.value =
            foldersRes.find(
                (item: FolderResponse) =>
                    String(item.id) === String(route.params.id),
            ) || null;
        bookmarks.value = bookmarksRes.items || [];
        state.value = folder.value ? "ready" : "not-found";
    } catch (err) {
        folder.value = null;
        bookmarks.value = [];
        errorMessage.value =
            err instanceof Error ? err.message : "Failed to load folder.";
        state.value = "error";
    }
};

const openEdit = () => {
    if (!folder.value) return;
    editForm.name = folder.value.name;
    editForm.description = folder.value.description || "";
    editOpen.value = true;
};

const saveFolder = async () => {
    if (!folder.value) return;
    const name = editForm.name.trim();
    if (!name) {
        toast.show({
            title: "Folder name is required.",
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        return;
    }

    saving.value = true;
    try {
        await request(`/folders/${folder.value.id}`, {
            method: "PATCH",
            body: JSON.stringify({
                name,
                description: editForm.description || null,
            }),
        });
        await refreshSidebarCatalog();
        await loadFolder();
        editOpen.value = false;
        toast.show({
            title: "Folder updated.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        toast.show({
            title: "Failed to update folder.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        saving.value = false;
    }
};

const deleteFolder = async () => {
    if (!folder.value) return;
    deleting.value = true;
    try {
        await request(`/folders/${folder.value.id}`, { method: "DELETE" });
        await refreshSidebarCatalog();
        toast.show({
            title: "Folder deleted.",
            color: "success",
            icon: "i-lucide-check",
        });
        await router.push("/folders");
    } catch (err) {
        toast.show({
            title: "Failed to delete folder.",
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
        void loadFolder();
    },
);

onMounted(loadFolder);
</script>
