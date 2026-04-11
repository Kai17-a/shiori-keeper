<template>
    <UDashboardPanel id="folders">
        <template #header>
            <UDashboardNavbar title="Folders" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageCard
                    title="Create folder"
                    description="Add a new folder to organize bookmarks"
                    :ui="{ body: 'space-y-4' }"
                >
                    <form
                        class="flex flex-col gap-3 sm:flex-row"
                        @submit.prevent="createFolder"
                    >
                        <UInput
                            v-model="folderName"
                            placeholder="New folder name"
                            class="flex-1"
                        />
                        <UButton type="submit" icon="i-lucide-plus" @click="createFolder">
                            Add folder
                        </UButton>
                    </form>
                </UPageCard>

                <UPageCard
                    title="Folder list"
                    description="All folders in the database"
                    :ui="{ body: 'space-y-3' }"
                >
                    <div v-if="folders.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        <CardsEntityCard
                            v-for="folder in folders"
                            :key="folder.id"
                            :title="folder.name"
                            :to="`/folders/${folder.id}`"
                            :meta="`Folder ID ${folder.id}`"
                            description="Manage this folder and review bookmarks assigned to it from the detail page."
                            @edit="openEdit(folder)"
                            @remove="askDelete(folder)"
                        />
                    </div>
                    <div
                        v-else
                        class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
                    >
                        No folders yet.
                    </div>
                </UPageCard>

                <UModal
                    v-model:open="editOpen"
                    title="Edit folder"
                    description="Rename the selected folder."
                    :ui="{
                        content:
                            'w-[calc(100vw-2rem)] max-w-md max-h-[calc(100dvh-2rem)] sm:max-h-[calc(100dvh-4rem)]',
                    }"
                >
                    <template #content="{ close }">
                        <div class="space-y-4 p-6">
                            <UFormField label="Folder name" class="w-full">
                                <UInput
                                    v-model="editForm.name"
                                    placeholder="Folder name"
                                    class="w-full"
                                />
                            </UFormField>
                            <div class="flex justify-end gap-3">
                                <UButton
                                    color="neutral"
                                    variant="ghost"
                                    @click="close"
                                >
                                    Cancel
                                </UButton>
                                <UButton @click="saveEdit">
                                    Save changes
                                </UButton>
                            </div>
                        </div>
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
                                Delete
                                <strong>{{ pendingFolder?.name }}</strong>
                                and remove it from the list?
                            </p>
                            <div class="flex justify-end gap-3">
                                <UButton
                                    color="neutral"
                                    variant="ghost"
                                    @click="closeConfirm"
                                >
                                    Cancel
                                </UButton>
                                <UButton color="error" @click="confirmDelete">
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
import type { FolderResponse } from "~/types";

const { request } = useBookmarkApi();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();
const toast = useSingleToast();

const folders = ref<FolderResponse[]>([]);
const folderName = ref("");
const editOpen = ref(false);
const confirmOpen = ref(false);
const pendingFolder = ref<FolderResponse | null>(null);
const editForm = reactive({ id: "", name: "" });

const refresh = async () => {
    try {
        folders.value = await request("/folders");
        await refreshSidebarCatalog();
        toast.show({
            title: "Folders loaded.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        toast.show({
            title: "Failed to load folders.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const createFolder = async () => {
    const name = folderName.value.trim();
    if (!name) {
        toast.show({
            title: "Folder name is required.",
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        return;
    }
    try {
        await request("/folders", {
            method: "POST",
            body: JSON.stringify({ name }),
        });
        folderName.value = "";
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to create folder.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const openEdit = (folder: FolderResponse) => {
    editForm.id = String(folder.id);
    editForm.name = folder.name;
    editOpen.value = true;
};

const closeEdit = () => {
    editOpen.value = false;
    editForm.id = "";
    editForm.name = "";
};

const saveEdit = async () => {
    const name = editForm.name.trim();
    if (!name) return;
    try {
        await request(`/folders/${editForm.id}`, {
            method: "PATCH",
            body: JSON.stringify({ name }),
        });
        closeEdit();
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to update folder.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const askDelete = (folder: FolderResponse) => {
    pendingFolder.value = folder;
    confirmOpen.value = true;
};

const closeConfirm = () => {
    confirmOpen.value = false;
    pendingFolder.value = null;
};

const confirmDelete = async () => {
    if (!pendingFolder.value) return;
    try {
        await request(`/folders/${pendingFolder.value.id}`, {
            method: "DELETE",
        });
        closeConfirm();
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to delete folder.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

onMounted(refresh);
</script>
