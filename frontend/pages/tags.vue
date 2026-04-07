<template>
    <div class="page">
        <header class="topbar">
            <div>
                <p class="eyebrow">Tags</p>
                <h1>Tag dashboard</h1>
            </div>
        </header>

        <section class="panel">
            <form class="form" @submit.prevent="createTag">
                <input v-model="tagName" placeholder="New tag" required />
                <button>Add tag</button>
            </form>
        </section>

        <section class="panel">
            <div class="list">
                <article v-for="tag in tags" :key="tag.id" class="item">
                    <div class="row">
                        <div class="row-main">
                            <strong>{{ tag.name }}</strong>
                            <p>Tag ID {{ tag.id }}</p>
                        </div>
                        <div class="actions">
                            <button type="button" class="edit" @click="openEdit(tag)">Edit</button>
                            <button
                                type="button"
                                class="trash"
                                aria-label="Delete tag"
                                @click="askDelete(tag)"
                            >
                                <span class="material-symbols-outlined">delete</span>
                            </button>
                        </div>
                    </div>
                </article>
            </div>
        </section>

        <div v-if="editOpen" class="modal-backdrop" @click.self="closeEdit">
            <div class="modal">
                <div class="modal-head">
                    <div>
                        <p class="eyebrow">Edit</p>
                        <h2>Edit tag</h2>
                    </div>
                    <button type="button" class="modal-close" @click="closeEdit">×</button>
                </div>
                <form class="form modal-form" @submit.prevent="saveEdit">
                    <input v-model="editForm.name" placeholder="Tag name" required />
                    <button>Save</button>
                </form>
            </div>
        </div>

        <div v-if="confirmOpen" class="modal-backdrop" @click.self="closeConfirm">
            <div class="modal">
                <div class="modal-head">
                    <div>
                        <p class="eyebrow">Confirm</p>
                        <h2>Delete tag?</h2>
                    </div>
                    <button type="button" class="modal-close" @click="closeConfirm">×</button>
                </div>
                <p class="confirm-text">
                    Delete <strong>{{ pendingTag?.name }}</strong> permanently?
                </p>
                <div class="confirm-actions">
                    <button type="button" class="cancel" @click="closeConfirm">Cancel</button>
                    <button type="button" class="danger" @click="confirmDelete">Delete</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const { request } = useBookmarkApi();
const tags = ref([]);
const tagName = ref("");
const message = ref("Ready.");
const editOpen = ref(false);
const editForm = reactive({ id: "", name: "" });
const confirmOpen = ref(false);
const pendingTag = ref(null);

const refresh = async () => {
    try {
        tags.value = await request("/tags");
    } catch (err) {
        message.value = err.message;
    }
};

const createTag = async () => {
    try {
        const name = tagName.value.trim();
        if (!name) {
            message.value = "Tag name is required.";
            return;
        }
        await request("/tags", {
            method: "POST",
            body: JSON.stringify({ name }),
        });
        tagName.value = "";
        await refresh();
    } catch (err) {
        message.value = err.message;
    }
};

const askDelete = (tag) => {
    pendingTag.value = tag;
    confirmOpen.value = true;
};

const openEdit = (tag) => {
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
        message.value = err.message;
    }
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
        message.value = err.message;
    }
};

onMounted(refresh);
</script>

<style scoped>
.page {
    max-width: 1100px;
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
.eyebrow {
    margin: 0 0 10px;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: #7dd3fc;
    font-size: 12px;
}
h1,
p {
    margin-top: 0;
}
.back,
button {
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
.form {
    display: flex;
    gap: 12px;
}
.form input {
    flex: 1;
    border-radius: 14px;
    border: 1px solid #334155;
    background: #0f172ae6;
    color: #e2e8f0;
    padding: 12px 14px;
}
.list {
    display: grid;
    gap: 12px;
    margin-top: 16px;
}
.item {
    border-radius: 20px;
    border: 1px solid #334155;
    background: rgba(15, 23, 42, 0.6);
    padding: 16px;
}
.row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
}
.row-main {
    min-width: 0;
}
.row-main strong {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.row-main p {
    color: #94a3b8;
    font-size: 13px;
    margin: 6px 0 0;
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
    flex-shrink: 0;
}
.actions {
    display: flex;
    gap: 10px;
    align-items: center;
    flex-shrink: 0;
}
.edit {
    background: transparent;
    border: 1px solid #334155;
    color: #e2e8f0;
    padding: 8px 12px;
}
.material-symbols-outlined {
    font-size: 18px;
    line-height: 1;
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
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
    width: min(520px, 100%);
    border-radius: 28px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: rgba(2, 6, 23, 0.96);
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
    padding: 20px;
}
.modal-form {
    display: flex;
    flex-direction: column;
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
.confirm-text {
    color: #cbd5e1;
}
.confirm-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 20px;
}
.cancel {
    background: transparent;
    color: #e2e8f0;
    border: 1px solid rgba(51, 65, 85, 1);
}
.danger {
    background: #7dd3fc;
    color: #08111f;
}
.message {
    margin-top: 20px;
}
@media (max-width: 800px) {
    .topbar,
    .form {
        flex-direction: column;
        align-items: stretch;
    }
    .row {
        align-items: flex-start;
    }
}
</style>
