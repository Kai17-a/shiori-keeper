<template>
  <UDashboardPanel id="tag-detail">
    <template #header>
      <PageHeaderActions title="Tag" />
    </template>

    <template #body>
      <div class="space-y-6">
        <UPageCard
          title="Tag details"
          description="Inspect and manage a single tag"
          :ui="{ body: 'space-y-4' }"
        >
          <UAlert
            v-if="state === 'error'"
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
              <UBadge color="primary" variant="soft"> Tag #{{ tag.id }} </UBadge>
              <span class="text-sm text-muted">
                {{ bookmarks.length }} bookmark{{ bookmarks.length === 1 ? "" : "s" }}
              </span>
            </div>
            <h1 class="text-2xl font-semibold text-default">
              {{ tag.name }}
            </h1>
            <div class="space-y-1">
              <p class="text-xs font-medium uppercase tracking-wide text-muted">Description</p>
              <p v-if="tag.description" class="text-sm leading-6 text-default/90">
                {{ tag.description }}
              </p>
              <p v-else class="text-sm text-muted">No description provided.</p>
            </div>
            <div class="flex flex-wrap gap-3">
              <UButton to="/tags" variant="ghost" size="sm"> Back to tags </UButton>
              <UButton
                color="neutral"
                variant="soft"
                size="sm"
                icon="i-lucide-pencil"
                @click="openEdit"
              >
                <span class="sr-only">Edit tag</span>
              </UButton>
              <UButton
                color="error"
                variant="soft"
                size="sm"
                icon="i-lucide-trash-2"
                @click="confirmOpen = true"
              >
                <span class="sr-only">Delete tag</span>
              </UButton>
            </div>
          </div>
        </UPageCard>

        <UPageCard :ui="{ body: 'space-y-3' }">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h2 class="text-lg font-semibold text-default">Bookmarks with this tag</h2>
              <p class="text-sm text-muted">Bookmarks associated with the selected tag</p>
            </div>
            <UButton
              icon="i-lucide-refresh-cw"
              color="neutral"
              variant="ghost"
              size="sm"
              :loading="refreshing"
              @click="loadTag(true)"
            >
              Refresh
            </UButton>
          </div>

          <div v-if="bookmarks.length" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <BookmarkCard
              v-for="bookmark in bookmarksWithRelations"
              :key="bookmark.id"
              :bookmark="bookmark"
              :show-folder="true"
              :show-tags="false"
              @edit="loadBookmarkForm"
              @remove="askDeleteBookmark"
              @favorite="toggleFavorite"
            />
          </div>
          <div
            v-else
            class="rounded-2xl border border-dashed border-default p-6 text-sm text-muted"
          >
            No bookmarks with this tag.
          </div>
        </UPageCard>

        <EntityEditorModal
          v-model:open="editOpen"
          :form="editForm"
          title="Edit tag"
          description="Rename this tag."
          name-label="Tag name"
          name-placeholder="Tag name"
          description-label="Description"
          description-placeholder="Optional tag description"
          submit-label="Save changes"
          :saving="saving"
          @save="saveTag"
        />

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
                <UButton color="neutral" variant="ghost" @click="close"> Cancel </UButton>
                <UButton type="submit" :loading="saving"> Save bookmark </UButton>
              </div>
            </form>
          </template>
        </UModal>

        <DeleteConfirmModal
          v-model:open="deleteBookmarkOpen"
          title="Delete bookmark"
          :subject="pendingBookmark?.title"
          confirm-label="Delete bookmark"
          :loading="deletingBookmark"
          @cancel="pendingBookmark = null"
          @confirm="confirmDeleteBookmark"
        />

        <DeleteConfirmModal
          v-model:open="confirmOpen"
          title="Delete tag"
          :subject="tag?.name"
          confirm-label="Delete tag"
          :loading="deleting"
          @cancel="confirmOpen = false"
          @confirm="deleteTag"
        />
      </div>
    </template>
  </UDashboardPanel>
</template>

<script setup lang="ts">
import type { BookmarkListResponse, BookmarkResponse, FolderResponse, TagResponse } from "~/types";
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
const tag = ref<TagResponse | null>(null);
const bookmarks = ref<BookmarkListResponse["items"]>([]);
const folders = ref<FolderResponse[]>([]);
const allTags = ref<TagResponse[]>([]);
const editOpen = ref(false);
const editBookmarkOpen = ref(false);
const deleteBookmarkOpen = ref(false);
const confirmOpen = ref(false);
const saving = ref(false);
const deleting = ref(false);
const deletingBookmark = ref(false);
const refreshing = ref(false);
const editForm = reactive({ name: "", description: "" });
const bookmarkForm = reactive<BookmarkFormState>(createBookmarkFormState());
const pendingBookmark = ref<BookmarkResponse | null>(null);

const loadTag = async (showToast = false) => {
  refreshing.value = true;
  state.value = "loading";
  errorMessage.value = "";

  try {
    const [tagsRes, foldersRes, bookmarksRes] = await Promise.all([
      request("/tags"),
      request("/folders"),
      request(`/bookmarks?tag_id=${route.params.id}`),
    ]);

    tag.value =
      tagsRes.find((item: TagResponse) => String(item.id) === String(route.params.id)) || null;
    allTags.value = tagsRes;
    folders.value = foldersRes;
    bookmarks.value = bookmarksRes.items || [];
    state.value = tag.value ? "ready" : "not-found";
    if (showToast) {
      toast.show({
        title: "Tag refreshed.",
        color: "success",
        icon: "i-lucide-check",
      });
    }
  } catch (err) {
    tag.value = null;
    bookmarks.value = [];
    errorMessage.value = err instanceof Error ? err.message : "Failed to load tag.";
    state.value = "error";
  } finally {
    refreshing.value = false;
  }
};

const bookmarksWithRelations = computed(() =>
  bookmarks.value.map((bookmark) => ({
    ...bookmark,
    folder_name: folders.value.find((folder) => folder.id === bookmark.folder_id)?.name || null,
    tags: bookmark.tags.filter((item) => item.id === Number(route.params.id)),
  })),
);

const bookmarkFolderOptions = computed<SelectOption[]>(() => [
  { label: "No folder", value: "" },
  ...createSelectOptions(
    folders.value,
    (folder) => folder.name,
    (folder) => folder.id,
  ),
]);

const bookmarkTagOptions = computed<SelectOption[]>(() =>
  createSelectOptions(
    allTags.value,
    (tag) => tag.name,
    (tag) => tag.id,
  ),
);

const selectedBookmarkFolder = computed<SelectOption | null>({
  get: () =>
    bookmarkFolderOptions.value.find((option) => option.value === bookmarkForm.folder_id) || null,
  set: (value) => {
    bookmarkForm.folder_id = normalizeSelectValue(value);
  },
});

const openEdit = () => {
  if (!tag.value) return;
  editForm.name = tag.value.name;
  editForm.description = tag.value.description || "";
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
      body: JSON.stringify({
        name,
        description: editForm.description || null,
      }),
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
  if (!bookmarkForm.id) return;
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
    await loadTag();
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

const confirmDeleteBookmark = async () => {
  if (!pendingBookmark.value) return;

  deletingBookmark.value = true;
  try {
    await request(`/bookmarks/${pendingBookmark.value.id}`, { method: "DELETE" });
    deleteBookmarkOpen.value = false;
    pendingBookmark.value = null;
    await loadTag();
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

const toggleFavorite = async (bookmark: BookmarkResponse) => {
  try {
    const updated = await request<BookmarkResponse>("/bookmarks/favorite", {
      method: "PATCH",
      body: JSON.stringify({
        bookmark_id: bookmark.id,
        is_favorite: !bookmark.is_favorite,
      }),
    });

    const index = bookmarks.value.findIndex((item) => item.id === updated.id);
    if (index >= 0) {
      bookmarks.value[index] = updated;
    }

    toast.show({
      title: updated.is_favorite ? "Added to favorites." : "Removed from favorites.",
      color: "success",
      icon: "i-lucide-check",
    });
  } catch (err) {
    toast.show({
      title: "Failed to update favorite.",
      description: err instanceof Error ? err.message : undefined,
      color: "error",
      icon: "i-lucide-circle-alert",
    });
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
