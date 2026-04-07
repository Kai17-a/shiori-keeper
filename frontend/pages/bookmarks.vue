<template>
    <div class="page">
        <header class="topbar">
            <div>
                <p class="eyebrow">Bookmarks</p>
                <h1>Bookmark list</h1>
            </div>
            <div class="top-actions">
                <button class="back action" @click="openCreateModal">
                    Register bookmark
                </button>
            </div>
        </header>

        <section class="panel">
            <div class="filters">
                <input v-model="searchQ" placeholder="Search title or URL" />
                <select v-model="filterFolder">
                    <option value="">All folders</option>
                    <option
                        v-for="folder in folders"
                        :key="folder.id"
                        :value="String(folder.id)"
                    >
                        {{ folder.name }}
                    </option>
                </select>
                <select v-model="filterTag">
                    <option value="">All tags</option>
                    <option
                        v-for="tag in tags"
                        :key="tag.id"
                        :value="String(tag.id)"
                    >
                        {{ tag.name }}
                    </option>
                </select>
            </div>
        </section>

        <section class="panel">
            <article v-for="bm in bookmarks" :key="bm.id">
                <div class="row">
                    <div class="row-main">
                        <div class="title-line">
                            <a :href="bm.url" target="_blank" rel="noreferrer">
                                {{ bm.title }}
                            </a>
                            <span class="url">{{ bm.url }}</span>
                        </div>
                        <div class="meta">
                            <span v-if="bm.folder_id" class="badge folder">
                                Folder #{{ bm.folder_id }}
                            </span>
                            <span
                                v-for="tag in bm.tags"
                                :key="tag.id"
                                class="badge tag"
                            >
                                {{ tag.name }}
                            </span>
                        </div>
                    </div>
                    <div class="actions">
                        <button
                            type="button"
                            class="edit"
                            @click="openEdit(bm)"
                        >
                            Edit
                        </button>
                        <button
                            type="button"
                            class="trash"
                            aria-label="Delete bookmark"
                            @click="removeBookmark(bm.id)"
                        >
                            <span class="material-symbols-outlined"
                                >delete</span
                            >
                        </button>
                    </div>
                </div>
            </article>
        </section>

        <div v-if="modalOpen" class="modal-backdrop" @click.self="closeModal">
            <div class="modal">
                <div class="modal-head">
                    <div>
                        <p class="eyebrow">
                            {{ bookmarkForm.id ? "Edit" : "Create" }}
                        </p>
                        <h2>
                            {{
                                bookmarkForm.id
                                    ? "Edit bookmark"
                                    : "Register bookmark"
                            }}
                        </h2>
                    </div>
                    <button
                        type="button"
                        class="modal-close"
                        @click="closeModal"
                    >
                        ×
                    </button>
                </div>

                <form class="form" @submit.prevent="saveBookmark">
                    <input
                        v-model="bookmarkForm.url"
                        placeholder="https://example.com"
                        required
                    />
                    <input
                        v-model="bookmarkForm.title"
                        placeholder="Title"
                        required
                    />
                    <textarea
                        v-model="bookmarkForm.description"
                        rows="3"
                        placeholder="Description"
                    />
                    <select v-model="bookmarkForm.folder_id">
                        <option value="" disabled>No folder</option>
                        <option
                            v-for="folder in folders"
                            :key="folder.id"
                            :value="String(folder.id)"
                        >
                            {{ folder.name }}
                        </option>
                    </select>
                    <select v-model="attachForm.tag_id">
                        <option value="" disabled>Select tag to attach</option>
                        <option
                            v-for="tag in tags"
                            :key="tag.id"
                            :value="String(tag.id)"
                        >
                            {{ tag.name }}
                        </option>
                    </select>
                    <button>Save bookmark</button>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
const route = useRoute();
const router = useRouter();
const { request } = useBookmarkApi();

const message = ref("Ready.");
const modalOpen = ref(false);
const bookmarks = ref([]);
const folders = ref([]);
const tags = ref([]);
const searchQ = ref(String(route.query.q || ""));
const filterFolder = ref(String(route.query.folder_id || ""));
const filterTag = ref(String(route.query.tag_id || ""));
const bookmarkForm = reactive({
    id: "",
    url: "",
    title: "",
    description: "",
    folder_id: "",
});
const attachForm = reactive({ bookmark_id: "", tag_id: "" });

const queryPath = computed(() => {
    const params = new URLSearchParams();
    if (filterFolder.value) params.set("folder_id", filterFolder.value);
    if (filterTag.value) params.set("tag_id", filterTag.value);
    if (searchQ.value.trim()) params.set("q", searchQ.value.trim());
    return params.toString() ? `/bookmarks?${params}` : "/bookmarks";
});

const loadData = async () => {
    const [bm, fs, ts] = await Promise.all([
        request(queryPath.value),
        request("/folders"),
        request("/tags"),
    ]);
    bookmarks.value = bm;
    folders.value = fs;
    tags.value = ts;
};

const syncQuery = () => {
    router.replace({
        query: Object.fromEntries(
            Object.entries({
                q: searchQ.value || undefined,
                folder_id: filterFolder.value || undefined,
                tag_id: filterTag.value || undefined,
            }).filter(([, v]) => v !== undefined),
        ),
    });
};

const refreshAll = async () => {
    try {
        await loadData();
    } catch (err) {
        message.value = err.message;
    }
};

const resetBookmarkForm = () => {
    bookmarkForm.id = "";
    bookmarkForm.url = "";
    bookmarkForm.title = "";
    bookmarkForm.description = "";
    bookmarkForm.folder_id = "";
};

const loadBookmarkForm = (bookmark) => {
    bookmarkForm.id = String(bookmark.id);
    bookmarkForm.url = bookmark.url;
    bookmarkForm.title = bookmark.title;
    bookmarkForm.description = bookmark.description || "";
    bookmarkForm.folder_id = bookmark.folder_id
        ? String(bookmark.folder_id)
        : "";
    modalOpen.value = true;
};

const openCreateModal = () => {
    resetBookmarkForm();
    attachForm.tag_id = "";
    modalOpen.value = true;
};

const closeModal = () => {
    modalOpen.value = false;
};

const saveBookmark = async () => {
    const payload = {
        url: bookmarkForm.url,
        title: bookmarkForm.title,
        description: bookmarkForm.description || null,
        folder_id: bookmarkForm.folder_id
            ? Number(bookmarkForm.folder_id)
            : null,
    };
    try {
        if (bookmarkForm.id)
            await request(`/bookmarks/${bookmarkForm.id}`, {
                method: "PATCH",
                body: JSON.stringify(payload),
            });
        else {
            const created = await request("/bookmarks", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            if (created?.id && attachForm.tag_id) {
                await request(`/bookmarks/${created.id}/tags`, {
                    method: "POST",
                    body: JSON.stringify({ tag_id: Number(attachForm.tag_id) }),
                });
            }
        }
        resetBookmarkForm();
        attachForm.tag_id = "";
        modalOpen.value = false;
        await refreshAll();
    } catch (err) {
        message.value = err.message;
    }
};

const removeBookmark = async (id) => {
    try {
        await request(`/bookmarks/${id}`, { method: "DELETE" });
        await refreshAll();
    } catch (err) {
        message.value = err.message;
    }
};

onMounted(refreshAll);
watch([searchQ, filterFolder, filterTag], () => {
    if (process.client) syncQuery();
});
</script>

<style scoped>
.page {
    max-width: 1400px;
    margin: 0 auto;
    padding: 28px 20px 44px;
    color: #e2e8f0;
}
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 12px;
    margin-bottom: 18px;
}
.top-actions {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: flex-end;
}
.eyebrow {
    margin: 0 0 10px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #7dd3fc;
    font-size: 12px;
}
h1,
h2,
p {
    margin-top: 0;
}
.back,
.panel button {
    border-radius: 14px;
    background: #7dd3fc;
    color: #08111f;
    font-weight: 700;
    padding: 12px 14px;
    text-decoration: none;
    display: inline-block;
    border: 0;
}
.panel {
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(2, 6, 23, 0.72);
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
    border-radius: 28px;
    padding: 20px;
}
.panel + .panel {
    margin-top: 16px;
}
.filters,
.form,
.list,
.tags,
.actions {
    display: grid;
    gap: 12px;
}
.filters {
    grid-template-columns: 1.5fr 1fr 1fr;
    margin-bottom: 14px;
}
.filters input,
.filters select,
.form input,
.form textarea,
.form select {
    border-radius: 14px;
    border: 1px solid #334155;
    background: #0f172ae6;
    color: #e2e8f0;
    padding: 12px 14px;
}
.message {
    margin-top: 20px;
}
.action {
    cursor: pointer;
}
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(2, 6, 23, 0.72);
    display: grid;
    place-items: center;
    z-index: 60;
    padding: 20px;
}
.modal {
    width: min(720px, 100%);
    border-radius: 28px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(2, 6, 23, 0.96);
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
    padding: 20px;
}
.modal-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 16px;
}
.modal-close {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    border: 1px solid rgba(51, 65, 85, 1);
    background: rgba(15, 23, 42, 0.95);
    color: #e2e8f0;
    font-size: 24px;
    line-height: 1;
    padding: 0;
}
.list {
    margin-top: 16px;
}
.list article + article {
    margin-top: 12px;
}
.item,
.row,
.accordion {
    border: 1px solid #334155;
    border-radius: 22px;
    background: rgba(15, 23, 42, 0.5);
    padding: 14px;
}
.row-main a {
    color: #ffffff;
    font-weight: 700;
    text-decoration: none;
    word-break: break-word;
}
.title-line {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
    flex-wrap: wrap;
}
.url {
    color: #94a3b8;
    font-size: 12px;
    word-break: break-all;
}
.row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
}
.meta {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}
.row {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: flex-start;
}
.row-main {
    min-width: 0;
}
.tags {
    display: flex;
    flex-wrap: wrap;
}
.badge {
    border-radius: 999px;
    border: 1px solid rgba(125, 211, 252, 0.25);
    background: rgba(125, 211, 252, 0.08);
    color: #bae6fd;
    padding: 4px 10px;
    font-size: 12px;
}
.folder {
    border-color: rgba(56, 189, 248, 0.3);
    background: rgba(56, 189, 248, 0.12);
    color: #cffafe;
}
.tag {
    border-color: rgba(251, 191, 36, 0.28);
    background: rgba(251, 191, 36, 0.12);
    color: #fde68a;
}
.actions {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-shrink: 0;
}
button {
    border: 1px solid rgba(51, 65, 85, 1);
    background: transparent;
    color: #e2e8f0;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 12px;
}
.edit {
    background: transparent;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 8px 12px;
}
.danger {
    border-color: rgba(244, 63, 94, 0.35);
    color: #fecdd3;
}
.trash {
    display: grid;
    place-items: center;
    padding: 0;
    width: 32px;
    height: 32px;
    border-radius: 999px;
    background: transparent;
    color: #fecaca;
    border: 1px solid rgba(51, 65, 85, 1);
}
.material-symbols-outlined {
    font-size: 18px;
    line-height: 1;
    font-variation-settings:
        "FILL" 0,
        "wght" 400,
        "GRAD" 0,
        "opsz" 24;
}
.actions .edit {
    border-color: rgba(51, 65, 85, 1);
}
.actions .trash {
    color: #fecaca;
}
@media (max-width: 1024px) {
    .filters {
        grid-template-columns: 1fr;
    }
    .topbar {
        align-items: flex-start;
        flex-direction: column;
    }
    .top-actions {
        width: 100%;
        justify-content: stretch;
    }
    .top-actions .back {
        flex: 1;
    }
    .summary,
    .row {
        flex-direction: column;
    }
    .actions {
        align-self: flex-end;
        flex-direction: row;
    }
    .summary-meta {
        justify-content: flex-start;
    }
}
</style>
