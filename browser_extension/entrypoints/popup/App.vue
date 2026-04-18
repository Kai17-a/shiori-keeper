<template>
  <UApp>
    <div class="min-h-screen px-2 py-3 text-slate-100">
      <div class="mx-auto flex w-full max-w-[340px] flex-col gap-2">
        <div class="flex items-center justify-between px-1">
          <h1 class="text-lg font-semibold tracking-tight text-slate-100">Shiori Keeper</h1>
          <UButton color="neutral" variant="ghost" icon="i-lucide-x" size="sm" />
        </div>

        <UCard>
          <div class="space-y-2">
            <label class="text-xs font-semibold text-slate-300">API Server URL</label>
            <div class="flex items-center gap-2 w-full">
              <UInput
                v-model="apiUrl"
                size="md"
                placeholder="http://localhost:8000"
                type="url"
                class="w-full"
              />
              <UButton
                icon="i-lucide-cable"
                :loading="isHealthChecking"
                size="md"
                @click="connectApiServer"
              />
            </div>

            <div
              class="items-center gap-2 text-xs font-medium text-slate-400"
              :class="apiStatusMessageColor"
            >
              {{ apiStatusMessage }}
            </div>
          </div>
        </UCard>

        <UCard>
          <UForm :schema="schema" :state="state" class="space-y-4">
            <UFormField label="Title" class="w-72">
              <UInput v-model="state.title" placeholder="example.com" class="w-full" />
            </UFormField>
            <UFormField label="URL" class="w-72">
              <UInput v-model="state.url" placeholder="https://example.com" class="w-full" />
            </UFormField>
            <UFormField label="Description" class="w-72">
              <UTextarea v-model="state.description" :rows="2" class="w-full" />
            </UFormField>
            <div class="flex items-center gap-2">
              <UFormField label="Folder" class="w-full">
                <USelect
                  v-model="state.folder"
                  placeholder="folder"
                  :items="folderItems"
                  class="w-full"
                />
              </UFormField>
              <UFormField label="Tag" class="w-full">
                <USelect
                  v-model="state.tag"
                  placeholder="tag"
                  multiple
                  :items="tagItems"
                  class="w-35"
                />
              </UFormField>
            </div>

            <div class="flex items-center justify-between gap-3 px-1 pt-1">
              <span class="text-xs font-medium text-slate-400" :class="responseMessageColor">
                {{ responseMessage }}
              </span>
              <div class="ml-auto flex items-center gap-3">
                <UButton
                  :loading="isRemoving"
                  color="error"
                  variant="ghost"
                  icon="i-lucide-trash-2"
                  size="md"
                  @click="remove"
                />
                <UButton :loading="isPending" size="md" @click="save"> Save </UButton>
              </div>
            </div>
          </UForm>
        </UCard>
      </div>
    </div>
  </UApp>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { SelectItem } from "@nuxt/ui";

// health check
const isHealthChecking = ref(false);
const isApiServerConnect = ref(false);
const apiStatusMessageColor = ref("text-warning");
const apiStatusMessage = ref("Connecting to API...");
const apiUrl = ref("http://localhost:8000");

// api
const pending = ref(false);
const isRemoving = ref(false);
const responseMessage = ref("");
const responseMessageColor = ref("text-warning");

// form value
const state = reactive({
  title: "",
  url: "",
  description: "",
  folder: null,
  tag: [],
});

// select
const folderItems = ref<SelectItem[]>([]);
const tagItems = ref<SelectItem[]>([]);

const getActiveTab = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab;
};

const formatApiError = (body: unknown, status: number) => {
  if (typeof body === "string") return body;
  if (body && typeof body === "object") {
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (detail != null) return JSON.stringify(detail);
    return JSON.stringify(body);
  }
  return `HTTP ${status}`;
};

const connectApiServer = async () => {
  if (isHealthChecking.value) return;

  isHealthChecking.value = true;

  try {
    const response = await fetch(new URL("/health", apiUrl.value));
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    } else {
      apiStatusMessage.value = "Connected to API";
      apiStatusMessageColor.value = "text-success";
    }
    isApiServerConnect.value = true;
  } catch (error) {
    apiStatusMessage.value = "Failed to Connect to API";
    apiStatusMessageColor.value = "text-error";
  } finally {
    isHealthChecking.value = false;
  }
};

const register = async () => {
  if (pending.value) {
    return;
  }

  pending.value = true;

  try {
    const response = await fetch(new URL("/bookmarks", apiUrl.value), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: state.url,
        title: state.title,
        description: state.description,
        folder_id: state.folder ?? null,
        tag_ids: state.tag ?? [],
      }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(formatApiError(body, response.status));
    }

    responseMessageColor.value = "text-success";
    responseMessage.value = "Registered";
  } catch (error) {
    responseMessageColor.value = "text-error";
    responseMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    pending.value = false;
  }
};
const save = async () => {
  if (pending.value) {
    return;
  }

  pending.value = true;

  try {
    const url = new URL("/bookmarks/by-url", apiUrl.value);
    url.searchParams.set("url", state.url);

    const response = await fetch(url, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        title: state.title,
        description: state.description,
        folder_id: state.folder ?? null,
        tag_ids: state.tag ?? [],
      }),
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(formatApiError(body, response.status));
    }

    responseMessageColor.value = "text-success";
    responseMessage.value = "Updated";
  } catch (error) {
    responseMessageColor.value = "text-error";
    responseMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    pending.value = false;
  }
};
const remove = async () => {
  if (pending.value) return;

  pending.value = true;

  try {
    const url = new URL("/bookmarks", apiUrl.value);
    url.searchParams.set("url", state.url);
    const response = await fetch(url, {
      method: "DELETE",
    });

    if (!response.ok) {
      const body = await response.json().catch(() => null);
      throw new Error(formatApiError(body, response.status));
    }

    responseMessageColor.value = "text-success";
    responseMessage.value = "Removed";
  } catch (error) {
    responseMessageColor.value = "text-error";
    responseMessage.value = error instanceof Error ? error.message : String(error);
  } finally {
    pending.value = false;
  }
};

const isGetFolderPending = ref(false);
const getFolders = async () => {
  if (pending.value && isGetFolderPending.value) return;

  isGetFolderPending.value = true;

  try {
    const response = await fetch(new URL("/folders", apiUrl.value));

    if (!response.ok) {
      throw new Error(await response.json());
    }
    const tags = await response.json();

    tags.forEach((e) => {
      folderItems.value.push({
        label: e.name,
        value: e.id,
      });
    });
  } catch (error) {
    responseMessageColor.value = "text-error";
    responseMessage.value = error.message;
  } finally {
    isGetFolderPending.value = false;
  }
};

const isGetTags = ref(false);
const getTags = async () => {
  if (pending.value && isGetTags.value) return;

  isGetTags.value = true;

  try {
    const response = await fetch(new URL("/tags", apiUrl.value));

    if (!response.ok) {
      throw new Error(await response.json());
    }
    const tags = await response.json();

    tags.forEach((e) => {
      tagItems.value.push({
        label: e.name,
        value: e.id,
      });
    });
  } catch (error) {
    responseMessageColor.value = "text-error";
    responseMessage.value = error.message;
  } finally {
    isGetTags.value = false;
  }
};

onMounted(async () => {
  const tab = await getActiveTab();

  if (tab?.title) {
    state.title = tab.title;
  }

  if (tab?.url) {
    state.url = tab.url;
  }

  await connectApiServer();

  if (isApiServerConnect.value) {
    await register();
    await Promise.all([getFolders(), getTags()]);
  }
});
</script>
