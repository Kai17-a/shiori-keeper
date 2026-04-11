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
                        <div class="space-y-1">
                            <p class="text-xs font-medium uppercase tracking-wide text-muted">
                                Description
                            </p>
                            <p v-if="folder.description" class="text-sm leading-6 text-default/90">
                                {{ folder.description }}
                            </p>
                            <p v-else class="text-sm text-muted">
                                No description provided.
                            </p>
                        </div>
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
                        <BookmarkCard
                            v-for="bookmark in bookmarks"
                            :key="bookmark.id"
                            :bookmark="bookmark"
                            :show-folder="false"
                            :show-tags="true"
                            @edit="loadBookmarkForm"
                            @remove="askDeleteBookmark"
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
                    v-model:open="editBookmarkOpen"
                    title="Edit bookmark"
                    description="Update the bookmark details."
                >
                    <template #content="{ close }">
                        <form class="space-y-4 p-6" @submit.prevent="saveBookmark">
                            <UFormField label="URL" required class="w-full">
                                <UInput v-model="bookmarkForm.url" class="w-full" />
                            </UFormField>

                            <UFormField label="Title" required class="w-full">
                                <UInput v-model="bookmarkForm.title" class="w-full" />
                            </UFormField>

                            <UFormField label="Description" class="w-full">
                                <UTextarea v-model="bookmarkForm.description" :rows="4" class="w-full" />
                            </UFormField>

                            <UFormField label="Folder" class="w-full">
                                <USelectMenu
                                    v-model="selectedBookmarkFolder"
                                    :items="bookmarkFolderOptions"
                                    placeholder="No folder"
                                    class="w-full"
                                />
                            </UFormField>

                            <UFormField
                                label="Tags"
                                description="Attach one or more tags to this bookmark."
                                class="w-full"
                            >
                                <USelectMenu
                                    v-model="bookmarkForm.tag_ids"
                                    :items="bookmarkTagOptions"
                                    placeholder="No tags"
                                    multiple
                                    value-key="value"
                                    class="w-full"
                                />
                            </UFormField>

                            <div class="flex justify-end gap-3">
                                <UButton color="neutral" variant="ghost" @click="close">
                                    Cancel
                                </UButton>
                                <UButton type="submit" :loading="saving">
                                    Save bookmark
                                </UButton>
                            </div>
                        </form>
                    </template>
                </UModal>

                <UModal
                    v-model:open="deleteBookmarkOpen"
                    title="Delete bookmark"
                    description="This action cannot be undone."
                >
                    <template #content>
                        <div class="space-y-4 p-6">
                            <p class="text-sm text-default">
                                Delete <strong>{{ pendingBookmark?.title }}</strong>?
                            </p>
                            <div class="flex justify-end gap-3">
                                <UButton color="neutral" variant="ghost" @click="closeBookmarkDelete">
                                    Cancel
                                </UButton>
                                <UButton color="error" :loading="deletingBookmark" @click="confirmDeleteBookmark">
                                    Delete bookmark
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
import type {
    BookmarkListResponse,
    BookmarkResponse,
    FolderResponse,
    TagResponse,
} from "~/types";
import {
    createBookmarkFormState,
    createSelectOptions,
    normalizeSelectValue,
    type BookmarkFormState,
    type SelectOption,
} from "~/utils/bookmarkList";

const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();
const toast = useSingleToast();
const { refresh: refreshSidebarCatalog } = useSidebarCatalog();

const state = ref<"loading" | "ready" | "error" | "not-found">("loading");
const errorMessage = ref("");
const folder = ref<FolderResponse | null>(null);
const bookmarks = ref<BookmarkListResponse["items"]>([]);
const folders = ref<FolderResponse[]>([]);
const tags = ref<TagResponse[]>([]);
const editOpen = ref(false);
const editBookmarkOpen = ref(false);
const deleteBookmarkOpen = ref(false);
const confirmOpen = ref(false);
const saving = ref(false);
const deleting = ref(false);
const deletingBookmark = ref(false);
const editForm = reactive({ name: "", description: "" });
const bookmarkForm = reactive<BookmarkFormState>(createBookmarkFormState());
const pendingBookmark = ref<BookmarkResponse | null>(null);

const loadFolder = async () => {
    state.value = "loading";
    errorMessage.value = "";

    try {
        const [foldersRes, tagsRes, bookmarksRes] = await Promise.all([
            request("/folders"),
            request("/tags"),
            request(`/bookmarks?folder_id=${route.params.id}`),
        ]);

        folder.value =
            foldersRes.find(
                (item: FolderResponse) =>
                    String(item.id) === String(route.params.id),
            ) || null;
        folders.value = foldersRes;
        tags.value = tagsRes;
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

const bookmarkFolderOptions = computed<SelectOption[]>(() => [
    { label: "No folder", value: "" },
    ...createSelectOptions(folders.value, (item) => item.name, (item) => item.id),
]);

const bookmarkTagOptions = computed<SelectOption[]>(() =>
    createSelectOptions(tags.value, (item) => item.name, (item) => item.id),
);

const selectedBookmarkFolder = computed<SelectOption | null>({
    get: () =>
        bookmarkFolderOptions.value.find(
            (option) => option.value === bookmarkForm.folder_id,
        ) || null,
    set: (value) => {
        bookmarkForm.folder_id = normalizeSelectValue(value);
    },
});

const openEdit = () => {
    if (!folder.value) return;
    editForm.name = folder.value.name;
    editForm.description = folder.value.description || "";
    editOpen.value = true;
};

const loadBookmarkForm = (bookmark: BookmarkResponse) => {
    bookmarkForm.id = String(bookmark.id);
    bookmarkForm.url = bookmark.url;
    bookmarkForm.title = bookmark.title;
    bookmarkForm.description = bookmark.description || "";
    bookmarkForm.folder_id = bookmark.folder_id ? String(bookmark.folder_id) : "";
    bookmarkForm.tag_ids = bookmark.tags.map((item) => String(item.id));
    editBookmarkOpen.value = true;
};

const saveBookmark = async () => {
    const url = bookmarkForm.url.trim();
    const title = bookmarkForm.title.trim();
    if (!url || !title) return;

    saving.value = true;
    try {
        await request(`/bookmarks/${bookmarkForm.id}`, {
            method: "PATCH",
            body: JSON.stringify({
                url,
                title,
                description: bookmarkForm.description || null,
                folder_id: bookmarkForm.folder_id ? Number(bookmarkForm.folder_id) : null,
                tag_ids: bookmarkForm.tag_ids.map((item) => Number(item)),
            }),
        });
        editBookmarkOpen.value = false;
        Object.assign(bookmarkForm, createBookmarkFormState());
        await loadFolder();
        toast.show({
            title: "Bookmark updated.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        toast.show({
            title: "Failed to save bookmark.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        saving.value = false;
    }
};

const askDeleteBookmark = (bookmark: BookmarkResponse) => {
    pendingBookmark.value = bookmark;
    deleteBookmarkOpen.value = true;
};

const closeBookmarkDelete = () => {
    deleteBookmarkOpen.value = false;
    pendingBookmark.value = null;
};

const confirmDeleteBookmark = async () => {
    if (!pendingBookmark.value) return;

    deletingBookmark.value = true;
    try {
        await request(`/bookmarks/${pendingBookmark.value.id}`, {
            method: "DELETE",
        });
        closeBookmarkDelete();
        await loadFolder();
        toast.show({
            title: "Bookmark deleted.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        toast.show({
            title: "Failed to delete bookmark.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        deletingBookmark.value = false;
    }
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
