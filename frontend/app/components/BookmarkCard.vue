<template>
    <article class="rounded-2xl border border-default bg-elevated/40 p-4 space-y-4">
        <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
                <NuxtLink
                    :to="bookmark.url"
                    external
                    target="_blank"
                    rel="noreferrer"
                    class="block truncate text-base font-semibold text-default hover:underline"
                >
                    {{ bookmark.title }}
                </NuxtLink>
                <p class="mt-1 break-all text-sm text-muted">
                    {{ bookmark.url }}
                </p>
            </div>

            <UBadge size="xs" variant="soft">#{{ bookmark.id }}</UBadge>
        </div>

        <p v-if="bookmark.description" class="text-sm text-default">
            {{ bookmark.description }}
        </p>

        <div v-if="bookmark.folder_name || bookmark.tags.length" class="flex flex-wrap gap-2">
            <UBadge
                v-if="bookmark.folder_name"
                size="xs"
                color="primary"
                variant="soft"
                icon="i-lucide-folder"
            >
                {{ bookmark.folder_name }}
            </UBadge>

            <UBadge
                v-for="tag in bookmark.tags"
                :key="tag.id"
                size="xs"
                color="neutral"
                variant="subtle"
                :ui="{ rounded: 'rounded-full' }"
            >
                {{ tag.name }}
            </UBadge>
        </div>

        <div class="flex justify-end gap-2">
            <UButton
                size="xs"
                variant="ghost"
                color="neutral"
                icon="i-lucide-pencil"
                @click="$emit('edit', bookmark)"
            >
                <span class="sr-only">Edit</span>
            </UButton>
            <UButton
                size="xs"
                variant="soft"
                color="error"
                icon="i-lucide-trash-2"
                @click="$emit('remove', bookmark.id)"
            />
        </div>
    </article>
</template>

<script setup lang="ts">
import type { BookmarkResponse } from "~/types";

defineProps<{
    bookmark: BookmarkResponse & { folder_name?: string | null };
}>();

defineEmits<{
    edit: [bookmark: BookmarkResponse & { folder_name?: string | null }];
    remove: [id: number];
}>();
</script>
