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

        <div v-if="showFolder && bookmark.folder_name" class="flex flex-wrap gap-2">
            <UBadge
                size="xs"
                color="primary"
                variant="soft"
                icon="i-lucide-folder"
            >
                {{ bookmark.folder_name }}
            </UBadge>
        </div>

        <div v-if="showTags && bookmark.tags.length" class="flex flex-wrap gap-2">
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
    </article>
</template>

<script setup lang="ts">
import type { BookmarkResponse } from "~/types";

defineProps<{
    bookmark: BookmarkResponse & { folder_name?: string | null };
    showFolder?: boolean;
    showTags?: boolean;
}>();
</script>
