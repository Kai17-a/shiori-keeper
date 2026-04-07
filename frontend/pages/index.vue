<template>
    <div class="shell">
        <header class="hero">
            <div>
                <p class="eyebrow">Bookmark Manager</p>
                <h1>Dashboard</h1>
                <p class="lede">
                    At-a-glance view of your bookmark system. Jump to bookmarks,
                    folders, and tags without leaving the Nuxt SPA.
                </p>
            </div>
            <div class="controls">
                <label>API Base URL</label>
                <input v-model="apiBase" />
                <button @click="saveApiBase">Save API URL</button>
                <button @click="refreshAll">Reload data</button>
                <p class="hint">
                    Default is proxied through nginx at <code>/api</code>.
                </p>
            </div>
        </header>

        <section class="dashboard">
            <article class="panel hero-card">
                <div class="panel-title">
                    <div>
                        <p class="eyebrow">Overview</p>
                        <h2>System health</h2>
                    </div>
                    <span>{{ bookmarks.length }} bookmarks</span>
                </div>

                <div class="metrics">
                    <div class="metric">
                        <span>Total bookmarks</span>
                        <strong>{{ bookmarks.length }}</strong>
                    </div>
                    <div class="metric">
                        <span>Folders</span>
                        <strong>{{ folders.length }}</strong>
                    </div>
                    <div class="metric">
                        <span>Tags</span>
                        <strong>{{ tags.length }}</strong>
                    </div>
                    <div class="metric">
                        <span>Tagged bookmarks</span>
                        <strong>{{ taggedCount }}</strong>
                    </div>
                </div>
            </article>

            <article class="panel message">{{ message }}</article>
        </section>
    </div>
</template>

<script setup>
const {
    apiBase,
    defaultApiBase,
    loadApiBase,
    saveApiBase: persistApiBase,
    request,
} = useBookmarkApi();
const message = ref("Ready.");
const bookmarks = ref([]);
const folders = ref([]);
const tags = ref([]);

const taggedCount = computed(
    () => bookmarks.value.filter((b) => b.tags.length).length,
);

const refreshAll = async () => {
    try {
        const [bm, folderRows, tagRows] = await Promise.all([
            request("/bookmarks"),
            request("/folders"),
            request("/tags"),
        ]);
        bookmarks.value = bm;
        folders.value = folderRows;
        tags.value = tagRows;
        message.value = "Dashboard loaded successfully.";
    } catch (err) {
        message.value = err.message;
    }
};

const saveApiBase = async () => {
    try {
        await persistApiBase(apiBase.value || defaultApiBase);
        message.value = "API base URL saved.";
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

const goToBookmarks = (bookmark) => {
    navigateTo({ path: "/bookmarks", query: { edit: String(bookmark.id) } });
};

const filterByFolder = (id) =>
    navigateTo({ path: "/bookmarks", query: { folder_id: String(id) } });
const filterByTag = (id) =>
    navigateTo({ path: "/bookmarks", query: { tag_id: String(id) } });

onMounted(refreshAll);
onMounted(loadApiBase);
</script>

<style scoped>
:global(body) {
    margin: 0;
    font-family: Inter, ui-sans-serif, system-ui, sans-serif;
    background:
        radial-gradient(
            circle at top,
            rgba(125, 211, 252, 0.18),
            transparent 30%
        ),
        linear-gradient(180deg, #020617 0%, #0b1020 100%);
    color: #e2e8f0;
}

.shell {
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 20px 48px;
}
.hero,
.panel {
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(2, 6, 23, 0.72);
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.32);
}
.hero {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    padding: 28px;
    border-radius: 28px;
    margin-bottom: 20px;
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
h1 {
    font-size: clamp(2.2rem, 4vw, 4.3rem);
    line-height: 1;
    margin-bottom: 14px;
}
.lede {
    max-width: 720px;
    color: #cbd5e1;
}
.controls {
    min-width: 320px;
    display: grid;
    gap: 10px;
}
.controls input {
    width: 100%;
    border-radius: 14px;
    border: 1px solid #334155;
    background: #0f172ae6;
    color: #e2e8f0;
    padding: 12px 14px;
}
.controls button,
.panel-link,
.shortcut {
    border: 0;
    border-radius: 14px;
    background: #7dd3fc;
    color: #08111f;
    font-weight: 700;
    padding: 12px 14px;
    text-decoration: none;
    display: inline-block;
}
.controls button {
    width: 100%;
}
.hint {
    font-size: 12px;
    color: #94a3b8;
}
.dashboard {
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
}
.lists-wrap {
    grid-column: 1 / -1;
    display: grid;
    gap: 20px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
}
.panel {
    border-radius: 28px;
    padding: 20px;
}
.hero-card,
.wide {
    grid-column: 1 / -1;
}
.panel-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}
.section-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
}
.metrics {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    margin-top: 16px;
}
.metric {
    border-radius: 18px;
    border: 1px solid rgba(51, 65, 85, 1);
    background: rgba(15, 23, 42, 0.6);
    padding: 16px;
    display: grid;
    gap: 6px;
}
.metric span {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.2em;
}
.metric strong {
    font-size: 2rem;
}
.stack,
.chips {
    display: grid;
    gap: 10px;
    margin-top: 12px;
}
.chips {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
}
.chip {
    border-radius: 999px;
    border: 1px solid rgba(51, 65, 85, 1);
    background: rgba(15, 23, 42, 0.95);
    color: #e2e8f0;
    padding: 10px 14px;
}
.list {
    display: grid;
    gap: 12px;
}
.list-item {
    border-radius: 20px;
    border: 1px solid rgba(51, 65, 85, 1);
    background: rgba(15, 23, 42, 0.6);
    padding: 16px;
}
.list-item.compact {
    padding: 14px 16px;
}
.list-main {
    display: grid;
    gap: 6px;
}
.item-title {
    color: #ffffff;
    font-weight: 700;
    text-decoration: none;
}
.item-meta,
.item-desc {
    color: #94a3b8;
    font-size: 13px;
    margin: 0;
    word-break: break-all;
}
.folder-chip,
.tag-chip {
    justify-content: space-between;
    display: flex;
    align-items: center;
    gap: 10px;
    text-align: left;
    width: 100%;
}
.folder-name {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.folder-id {
    color: #f8fafc;
    font-size: 12px;
    opacity: 0.7;
    flex-shrink: 0;
}
.message {
    grid-column: 1 / -1;
}
@media (max-width: 1024px) {
    .hero,
    .dashboard {
        grid-template-columns: 1fr;
        display: grid;
    }
    .lists-wrap {
        grid-template-columns: 1fr;
    }
    .metrics {
        grid-template-columns: 1fr;
    }
    .section-head {
        align-items: flex-start;
        flex-direction: column;
    }
    .folder-chip,
    .tag-chip {
        justify-content: flex-start;
    }
}
</style>
