<template>
    <UDashboardPanel id="bookmarks">
        <template #header>
            <UDashboardNavbar title="Bookmarks" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>

                <template #right>
                    <UButton
                        label="Register"
                        icon="i-lucide-plus"
                        size="sm"
                        @click="openCreateModal"
                    />
                </template>
            </UDashboardNavbar>
        </template>

        <template #body>
            <div class="space-y-6">
                <UPageCard
                    title="Search & filters"
                    description="Filter bookmarks by keyword, folder, or tag"
                    :ui="{ body: 'space-y-4' }"
                >
                    <form class="grid gap-3 lg:grid-cols-[2fr_1fr_1fr]">
                        <UInput
                            v-model="searchQ"
                            placeholder="Search by title or URL"
                        />
                        <USelectMenu
                            v-model="selectedFilterFolder"
                            :items="filterFolderOptions"
                            placeholder="All folders"
                            value-attribute="value"
                            option-attribute="label"
                        />
                        <USelectMenu
                            v-model="selectedFilterTag"
                            :items="filterTagOptions"
                            placeholder="All tags"
                            value-attribute="value"
                            option-attribute="label"
                        />
                    </form>
                </UPageCard>

                <UPageCard
                    title="Bookmark list"
                    description="Latest bookmarks matching the current filters"
                    :ui="{ body: 'space-y-4' }"
                >
                    <div
                        class="flex flex-col gap-3 border-b border-default pb-4 md:flex-row md:items-center md:justify-between"
                    >
                        <p class="text-xs uppercase tracking-[0.08em] text-muted">
                            Page {{ bookmarkList.page }} of
                            {{ pageCount }}
                        </p>
                        <div class="flex items-center gap-2">
                            <UButton
                                size="sm"
                                variant="ghost"
                                color="neutral"
                                :disabled="page <= 1 || loading"
                                @click="setPage(page - 1)"
                            >
                                Prev
                            </UButton>
                            <template v-for="(item, index) in paginationItems" :key="`${item.type}-${index}-${item.value ?? 'ellipsis'}`">
                                <UButton
                                    v-if="item.type === 'page'"
                                    size="sm"
                                    :color="item.value === page ? 'primary' : 'neutral'"
                                    :variant="item.value === page ? 'solid' : 'ghost'"
                                    :disabled="loading"
                                    @click="setPage(item.value)"
                                >
                                    {{ item.label }}
                                </UButton>
                                <UButton
                                    v-else
                                    size="sm"
                                    variant="ghost"
                                    color="neutral"
                                    disabled
                                >
                                    ...
                                </UButton>
                            </template>
                            <UButton
                                size="sm"
                                variant="ghost"
                                color="neutral"
                                :disabled="page >= pageCount || loading"
                                @click="setPage(page + 1)"
                            >
                                Next
                            </UButton>
                        </div>
                    </div>

                    <div v-if="bookmarkList.items.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                        <BookmarkCard
                            v-for="bookmark in bookmarkCards"
                            :key="bookmark.id"
                            :bookmark="bookmark"
                            @edit="loadBookmarkForm"
                            @remove="removeBookmark"
                        />
                    </div>

                    <div
                        v-else
                        class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
                    >
                        <p v-if="loading">Loading bookmarks...</p>
                        <p v-else-if="loadError">
                            {{ loadError }}
                        </p>
                        <p v-else>No bookmarks yet.</p>
                    </div>

                </UPageCard>

                <UModal
                    v-model:open="modalOpen"
                    :title="bookmarkForm.id ? 'Edit bookmark' : 'Register bookmark'"
                    :description="bookmarkForm.id ? 'Update the bookmark details.' : 'Create a bookmark and attach tags.'"
                >
                    <template #content="{ close }">
                        <form class="space-y-4 p-6" @submit.prevent="saveBookmark">
                            <UFormField label="URL" required class="w-full">
                                <UInput
                                    v-model="bookmarkForm.url"
                                    placeholder="https://example.com"
                                    class="w-full"
                                />
                            </UFormField>

                            <UFormField label="Title" required class="w-full">
                                <UInput
                                    v-model="bookmarkForm.title"
                                    placeholder="Bookmark title"
                                    class="w-full"
                                />
                            </UFormField>

                            <UFormField label="Description" class="w-full">
                                <UTextarea
                                    v-model="bookmarkForm.description"
                                    placeholder="Optional description"
                                    :rows="4"
                                    class="w-full"
                                />
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
                                <UButton
                                    color="neutral"
                                    variant="ghost"
                                    @click="close"
                                >
                                    Cancel
                                </UButton>
                                <UButton type="submit" :loading="saving">
                                    Save bookmark
                                </UButton>
                            </div>
                        </form>
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
    buildBookmarkQuery,
    buildPaginationItems,
    createEmptyBookmarkForm,
    createSelectOptions,
    mapBookmarksWithFolderNames,
    normalizeSelectValue,
    parsePositiveInteger,
    toBookmarkRouteQuery,
    type BookmarkFormState,
    type PaginationItem,
} from "~/utils/bookmarkList";

const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();
const toast = useSingleToast();

const loading = ref(false);
const saving = ref(false);
const loadError = ref("");
const modalOpen = ref(false);
const bookmarkList = ref<BookmarkListResponse>({
    items: [],
    total: 0,
    page: 1,
    per_page: 20,
    total_pages: 0,
});
const folders = ref<FolderResponse[]>([]);
const tags = ref<TagResponse[]>([]);
const searchQ = ref(String(route.query.q || ""));
const filterFolder = ref(String(route.query.folder_id || ""));
const filterTag = ref(String(route.query.tag_id || ""));
const page = ref(parsePositiveInteger(route.query.page, 1));
const bookmarkForm = reactive<BookmarkFormState>(createEmptyBookmarkForm());

const filterFolderOptions = computed(() => [
    { label: "All folders", value: "" },
    ...createSelectOptions(
        folders.value,
        (folder) => folder.name,
        (folder) => folder.id,
    ),
]);

const filterTagOptions = computed(() => [
    { label: "All tags", value: "" },
    ...createSelectOptions(tags.value, (tag) => tag.name, (tag) => tag.id),
]);

const bookmarkFolderOptions = computed(() => [
    { label: "No folder", value: "" },
    ...createSelectOptions(
        folders.value,
        (folder) => folder.name,
        (folder) => folder.id,
    ),
]);

const bookmarkTagOptions = computed(() => [
    ...createSelectOptions(tags.value, (tag) => tag.name, (tag) => tag.id),
]);

type SelectOption = {
    label: string;
    value: string;
};

const selectedFilterFolder = computed({
    get: () => filterFolder.value,
    set: (value) => {
        filterFolder.value = normalizeSelectValue(value);
    },
});

const selectedFilterTag = computed({
    get: () => filterTag.value,
    set: (value) => {
        filterTag.value = normalizeSelectValue(value);
    },
});

const selectedBookmarkFolder = computed<SelectOption | null>({
    get: () =>
        bookmarkFolderOptions.value.find(
            (option) => option.value === bookmarkForm.folder_id,
        ) || null,
    set: (value) => {
        bookmarkForm.folder_id = value?.value || "";
    },
});

const bookmarkCards = computed(() =>
    mapBookmarksWithFolderNames(bookmarkList.value.items, folders.value),
);

const pageCount = computed(() =>
    Math.max(
        Math.ceil(bookmarkList.value.total / Math.max(bookmarkList.value.per_page, 1)),
        1,
    ),
);

const paginationItems = computed<PaginationItem[]>(() =>
    buildPaginationItems(page.value, pageCount.value),
);

const loadData = async () => {
    loading.value = true;
    loadError.value = "";
    try {
        const [bookmarkRes, folderRes, tagRes] = await Promise.all([
            request<BookmarkListResponse>(
                buildBookmarkQuery({
                    searchQ: searchQ.value,
                    folderId: filterFolder.value,
                    tagId: filterTag.value,
                    page: page.value,
                }),
            ),
            request<FolderResponse[]>("/folders"),
            request<TagResponse[]>("/tags"),
        ]);

        bookmarkList.value = bookmarkRes;
        folders.value = folderRes;
        tags.value = tagRes;
    } catch (err) {
        loadError.value =
            err instanceof Error ? err.message : "Failed to load bookmarks.";
        toast.show({
            title: "Failed to load bookmarks.",
            description: loadError.value,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    } finally {
        loading.value = false;
    }
};

const resetBookmarkForm = () => {
    Object.assign(bookmarkForm, createEmptyBookmarkForm());
};

const loadBookmarkForm = (bookmark: BookmarkResponse) => {
    bookmarkForm.id = String(bookmark.id);
    bookmarkForm.url = bookmark.url;
    bookmarkForm.title = bookmark.title;
    bookmarkForm.description = bookmark.description || "";
    bookmarkForm.folder_id = bookmark.folder_id
        ? String(bookmark.folder_id)
        : "";
    bookmarkForm.tag_ids = bookmark.tags.map((tag) => String(tag.id));
    modalOpen.value = true;
};

const openCreateModal = () => {
    resetBookmarkForm();
    modalOpen.value = true;
};

const setPage = async (nextPage: number) => {
    const next = Math.min(Math.max(nextPage, 1), pageCount.value);
    if (next === page.value) return;
    page.value = next;
};

const validateBookmarkForm = () => {
    if (!bookmarkForm.url.trim()) {
        return "URL is required.";
    }

    try {
        new URL(bookmarkForm.url.trim());
    } catch {
        return "Please enter a valid URL.";
    }

    if (!bookmarkForm.title.trim()) {
        return "Title is required.";
    }

    return "";
};

const saveBookmark = async () => {
    const validationError = validateBookmarkForm();
    if (validationError) {
        toast.show({
            title: "Failed to save bookmark.",
            description: validationError,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
        return;
    }

    const payload = {
        url: bookmarkForm.url.trim(),
        title: bookmarkForm.title.trim(),
        description: bookmarkForm.description || null,
        folder_id: bookmarkForm.folder_id
            ? Number(bookmarkForm.folder_id)
            : null,
        tag_ids: bookmarkForm.tag_ids.map((tagId) => Number(tagId)),
    };

    saving.value = true;
    try {
        if (bookmarkForm.id) {
            await request(`/bookmarks/${bookmarkForm.id}`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });
        } else {
            const created = await request<BookmarkResponse>("/bookmarks", {
                method: "POST",
                body: JSON.stringify({
                    ...payload,
                }),
            });
            if (created?.id) {
                bookmarkForm.id = String(created.id);
            }
        }

        modalOpen.value = false;
        resetBookmarkForm();
        await loadData();
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

const removeBookmark = async (id: number) => {
    try {
        await request(`/bookmarks/${id}`, { method: "DELETE" });
        await loadData();
    } catch (err) {
        toast.show({
            title: "Failed to delete bookmark.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

watch(
    [searchQ, filterFolder, filterTag, page],
    async ([nextSearch, nextFolder, nextTag, nextPage]) => {
        await router.replace(
            toBookmarkRouteQuery({
                searchQ: nextSearch,
                folderId: nextFolder,
                tagId: nextTag,
                page: nextPage,
            }),
        );
        await loadData();
    },
    { immediate: true },
);

watch(
    () => route.query.page,
    async (next) => {
        const nextPage = parsePositiveInteger(next, 1);
        if (nextPage !== page.value) {
            page.value = nextPage;
        }
    },
);
</script>
