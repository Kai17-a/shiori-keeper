<template>
    <UDashboardPanel id="bookmarks">
        <template #header>
            <UDashboardNavbar title="Bookmarks" :ui="{ right: 'gap-3' }">
                <template #leading>
                    <UDashboardSidebarCollapse />
                </template>

                <template #trailing>
                    <UBadge
                        :label="connectionLabel"
                        variant="soft"
                        :color="connectionColor"
                    />
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
                            <UFormField label="URL" required>
                                <UInput
                                    v-model="bookmarkForm.url"
                                    placeholder="https://example.com"
                                />
                            </UFormField>

                            <UFormField label="Title" required>
                                <UInput
                                    v-model="bookmarkForm.title"
                                    placeholder="Bookmark title"
                                />
                            </UFormField>

                            <UFormField label="Description">
                                <UTextarea
                                    v-model="bookmarkForm.description"
                                    placeholder="Optional description"
                                    :rows="4"
                                />
                            </UFormField>

                            <UFormField label="Folder">
                            <USelectMenu
                                    v-model="selectedBookmarkFolder"
                                    :items="bookmarkFolderOptions"
                                    placeholder="No folder"
                                />
                            </UFormField>

                            <UFormField
                                label="Tags"
                                description="Attach one or more tags to this bookmark."
                            >
                                <USelectMenu
                                    v-model="selectedBookmarkTags"
                                    :items="bookmarkTagOptions"
                                    placeholder="No tags"
                                    multiple
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

const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();
const toast = useSingleToast();

const connectionLabel = ref("Connecting...");
const connectionColor = ref<"warning" | "success" | "error">("warning");
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
const page = ref(Number(route.query.page || 1) || 1);
const bookmarkForm = reactive({
    id: "",
    url: "",
    title: "",
    description: "",
    folder_id: "",
    tag_ids: [] as string[],
});

const filterFolderOptions = computed(() => [
    { label: "All folders", value: "" },
    ...folders.value.map((folder) => ({
        label: folder.name,
        value: String(folder.id),
    })),
]);

const filterTagOptions = computed(() => [
    { label: "All tags", value: "" },
    ...tags.value.map((tag) => ({
        label: tag.name,
        value: String(tag.id),
    })),
]);

const bookmarkFolderOptions = computed(() => [
    { label: "No folder", value: "" },
    ...folders.value.map((folder) => ({
        label: folder.name,
        value: String(folder.id),
    })),
]);

const bookmarkTagOptions = computed(() => [
    { label: "No tag", value: "" },
    ...tags.value.map((tag) => ({
        label: tag.name,
        value: String(tag.id),
    })),
]);

type SelectOption = {
    label: string;
    value: string;
};

const normalizeSelectValue = (value: unknown) => {
    if (typeof value === "string" || typeof value === "number") {
        return String(value);
    }

    if (value && typeof value === "object" && "value" in value) {
        const raw = (value as { value?: unknown }).value;
        return raw == null ? "" : String(raw);
    }

    return "";
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

const selectedBookmarkTags = computed<SelectOption[]>({
    get: () =>
        bookmarkTagOptions.value.filter((option) =>
            bookmarkForm.tag_ids.includes(option.value),
        ),
    set: (value) => {
        bookmarkForm.tag_ids = (Array.isArray(value) ? value : [])
            .map((item) => item?.value || "")
            .filter(Boolean);
    },
});

const bookmarkCards = computed(() =>
    bookmarkList.value.items.map((bookmark) => ({
        ...bookmark,
        folder_name:
            folders.value.find((folder) => folder.id === bookmark.folder_id)
                ?.name || null,
    })),
);

const pageCount = computed(() =>
    Math.max(
        Math.ceil(bookmarkList.value.total / Math.max(bookmarkList.value.per_page, 1)),
        1,
    ),
);

const paginationItems = computed(() => {
    const total = pageCount.value;
    const current = Math.min(Math.max(page.value, 1), total);
    const items: Array<
        | { type: "page"; value: number; label: string }
        | { type: "ellipsis" }
    > = [];

    if (total <= 7) {
        for (let number = 1; number <= total; number += 1) {
            items.push({ type: "page", value: number, label: String(number) });
        }
        return items;
    }

    items.push({ type: "page", value: 1, label: "1" });

    if (current > 3) {
        items.push({ type: "ellipsis" });
    }

    const middleStart = Math.max(2, current - 1);
    const middleEnd = Math.min(total - 1, current + 1);

    for (let number = middleStart; number <= middleEnd; number += 1) {
        items.push({ type: "page", value: number, label: String(number) });
    }

    if (current < total - 2) {
        items.push({ type: "ellipsis" });
    }

    items.push({ type: "page", value: total, label: String(total) });

    return items;
});

const queryPath = computed(() => {
    const params = new URLSearchParams();
    if (filterFolder.value) params.set("folder_id", filterFolder.value);
    if (filterTag.value) params.set("tag_id", filterTag.value);
    if (searchQ.value.trim()) params.set("q", searchQ.value.trim());
    params.set("page", String(page.value));
    return params.toString() ? `/bookmarks?${params}` : "/bookmarks";
});

const syncQuery = () => {
    router.replace({
        query: Object.fromEntries(
            Object.entries({
                q: searchQ.value || undefined,
                folder_id: filterFolder.value || undefined,
                tag_id: filterTag.value || undefined,
                page: page.value > 1 ? String(page.value) : undefined,
            }).filter(([, value]) => value !== undefined),
        ),
    });
};

const loadData = async () => {
    loading.value = true;
    loadError.value = "";
    bookmarkList.value.items = [];
    try {
        const [bookmarkRes, folderRes, tagRes] = await Promise.all([
            request(queryPath.value),
            request("/folders"),
            request("/tags"),
        ]);

        const result = bookmarkRes as BookmarkListResponse;
        bookmarkList.value = result;
        page.value = result.page || 1;
        folders.value = folderRes;
        tags.value = tagRes;
        connectionLabel.value = "Connected";
        connectionColor.value = "success";
        toast.show({
            title: "Bookmarks loaded.",
            color: "success",
            icon: "i-lucide-check",
        });
    } catch (err) {
        loadError.value =
            err instanceof Error ? err.message : "Failed to load bookmarks.";
        connectionLabel.value = "Serverに接続できない";
        connectionColor.value = "error";
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
    bookmarkForm.id = "";
    bookmarkForm.url = "";
    bookmarkForm.title = "";
    bookmarkForm.description = "";
    bookmarkForm.folder_id = "";
    bookmarkForm.tag_ids = [];
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

const closeModal = () => {
    modalOpen.value = false;
};

const setPage = async (nextPage: number) => {
    const next = Math.min(Math.max(nextPage, 1), pageCount.value);
    if (next === page.value) return;
    page.value = next;
};

const refreshAll = async () => {
    await loadData();
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
            const created = (await request("/bookmarks", {
                method: "POST",
                body: JSON.stringify({
                    ...payload,
                }),
            })) as BookmarkResponse;
            if (created?.id) {
                bookmarkForm.id = String(created.id);
            }
        }

        resetBookmarkForm();
        modalOpen.value = false;
        await refreshAll();
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
        await refreshAll();
    } catch (err) {
        toast.show({
            title: "Failed to delete bookmark.",
            description: err instanceof Error ? err.message : undefined,
            color: "error",
            icon: "i-lucide-circle-alert",
        });
    }
};

onMounted(refreshAll);

watch([searchQ, filterFolder, filterTag], async () => {
    page.value = 1;
    syncQuery();
    await loadData();
});

watch(page, async (next, prev) => {
    if (next === prev) return;
    await loadData();
    syncQuery();
});

watch(
    () => route.query.page,
    async (next) => {
        const nextPage = Number(next || 1) || 1;
        if (nextPage !== page.value) {
            page.value = nextPage;
        }
    },
);
</script>
