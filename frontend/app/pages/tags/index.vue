<template>
    <UDashboardPanel id="tags">
        <template #header>
            <UDashboardNavbar title="Tags" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageCard
                    title="Create tag"
                    description="Add a new tag for organizing bookmarks"
                    :ui="{ body: 'space-y-4' }"
                >
                    <form
                        class="flex flex-col gap-3 sm:flex-row"
                        @submit.prevent="createTag"
                    >
                        <UInput
                            v-model="tagName"
                            placeholder="New tag name"
                            class="flex-1"
                        />
                        <UButton type="submit" icon="i-lucide-plus">
                            Add tag
                        </UButton>
                    </form>
                </UPageCard>

                <UPageCard
                    title="Tag list"
                    description="All tags in the database"
                    :ui="{ body: 'space-y-3' }"
                >
                    <div v-if="tags.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        <UCard
                            v-for="tag in tags"
                            :key="tag.id"
                            :ui="{
                                body: 'space-y-4',
                                header: 'space-y-2',
                            }"
                        >
                            <template #header>
                                <div class="flex items-start justify-between gap-3">
                                    <div class="min-w-0">
                                        <NuxtLink
                                            :to="`/tags/${tag.id}`"
                                            class="truncate text-base font-semibold text-default hover:underline"
                                        >
                                            {{ tag.name }}
                                        </NuxtLink>
                                        <p class="mt-1 text-sm text-muted">
                                            Tag ID {{ tag.id }}
                                        </p>
                                    </div>
                                    <div class="flex shrink-0 items-center gap-2">
                                        <UButton
                                            size="xs"
                                            variant="ghost"
                                            color="neutral"
                                            icon="i-lucide-pencil"
                                            @click="openEdit(tag)"
                                        >
                                            <span class="sr-only">Edit</span>
                                        </UButton>
                                        <UButton
                                            size="xs"
                                            variant="soft"
                                            color="error"
                                            icon="i-lucide-trash-2"
                                            @click="askDelete(tag)"
                                        />
                                    </div>
                                </div>
                            </template>

                            <p class="text-sm text-muted">
                                Manage this tag and review its associated bookmarks from the detail page.
                            </p>
                        </UCard>
                    </div>
                    <div
                        v-else
                        class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
                    >
                        No tags yet.
                    </div>
                </UPageCard>

                <UModal
                    v-model:open="editOpen"
                    title="Edit tag"
                    description="Rename the selected tag."
                    :ui="{
                        content:
                            'w-[calc(100vw-2rem)] max-w-md max-h-[calc(100dvh-2rem)] sm:max-h-[calc(100dvh-4rem)]',
                    }"
                >
                    <template #content="{ close }">
                        <div class="space-y-4 p-6">
                            <UFormField label="Tag name" class="w-full">
                                <UInput
                                    v-model="editForm.name"
                                    placeholder="Tag name"
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
                                <UButton @click="saveEdit">Save changes</UButton>
                            </div>
                        </div>
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
                                Delete
                                <strong>{{ pendingTag?.name }}</strong>
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
import type { TagResponse } from "~/types";

const { request } = useBookmarkApi();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();
const toast = useSingleToast();

const connectionLabel = ref("Connecting...");
const connectionColor = ref<"warning" | "success" | "error">("warning");
const tags = ref<TagResponse[]>([]);
const tagName = ref("");
const editOpen = ref(false);
const confirmOpen = ref(false);
const pendingTag = ref<TagResponse | null>(null);
const editForm = reactive({ id: "", name: "" });

const refresh = async () => {
    try {
        tags.value = await request("/tags");
        await refreshSidebarCatalog();
        connectionLabel.value = "Connected";
        connectionColor.value = "success";
        toast.show({
            title: "Tags loaded.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        connectionLabel.value = "Serverに接続できない";
        connectionColor.value = "error";
        toast.show({
            title: "Failed to load tags.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const createTag = async () => {
    const name = tagName.value.trim();
    if (!name) {
        toast.show({
            title: "Tag name is required.",
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        return;
    }
    try {
        await request("/tags", {
            method: "POST",
            body: JSON.stringify({ name }),
        });
        tagName.value = "";
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to create tag.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const openEdit = (tag: TagResponse) => {
    editForm.id = String(tag.id);
    editForm.name = tag.name;
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
        await request(`/tags/${editForm.id}`, {
            method: "PATCH",
            body: JSON.stringify({ name }),
        });
        closeEdit();
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to update tag.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

const askDelete = (tag: TagResponse) => {
    pendingTag.value = tag;
    confirmOpen.value = true;
};

const closeConfirm = () => {
    confirmOpen.value = false;
    pendingTag.value = null;
};

const confirmDelete = async () => {
    if (!pendingTag.value) return;
    try {
        await request(`/tags/${pendingTag.value.id}`, { method: "DELETE" });
        closeConfirm();
        await refresh();
    } catch (err) {
        toast.show({
            title: "Failed to delete tag.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

onMounted(refresh);
</script>
