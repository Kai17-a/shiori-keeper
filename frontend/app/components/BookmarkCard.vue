<template>
  <article class="rounded-2xl border border-default bg-elevated/40 p-4 space-y-4">
    <div class="flex items-start justify-between gap-4">
      <div class="min-w-0">
        <div class="flex items-center gap-1.5">
          <UButton
            type="button"
            size="xs"
            variant="ghost"
            class="shrink-0 px-1"
            :color="bookmark.is_favorite ? 'warning' : 'neutral'"
            :icon="bookmark.is_favorite ? 'i-lucide-star' : 'i-lucide-star-off'"
            @click.stop="$emit('favorite', bookmark)"
          >
            <span class="sr-only">
              {{ bookmark.is_favorite ? "Remove from favorites" : "Add to favorites" }}
            </span>
          </UButton>
          <NuxtLink
            :to="bookmark.url"
            external
            target="_blank"
            rel="noreferrer"
            class="block truncate text-base font-semibold text-default hover:underline"
          >
            {{ bookmark.title }}
          </NuxtLink>
        </div>
        <p class="mt-1 break-all text-sm text-muted">
          {{ bookmark.url }}
        </p>
      </div>

      <div class="hidden shrink-0 items-center gap-2 sm:flex">
        <UButton
          type="button"
          size="xs"
          variant="ghost"
          color="neutral"
          icon="i-lucide-pencil"
          @click.stop="$emit('edit', bookmark)"
        >
          <span class="sr-only">Edit</span>
        </UButton>
        <UButton
          type="button"
          size="xs"
          variant="soft"
          color="error"
          icon="i-lucide-trash-2"
          @click.stop="$emit('remove', bookmark.id)"
        />
      </div>
    </div>

    <p v-if="bookmark.description" class="text-sm text-default">
      {{ bookmark.description }}
    </p>

    <div v-if="showFolder || (showTags && bookmark.tags.length)" class="space-y-3">
      <div v-if="showFolder && bookmark.folder_name" class="flex flex-wrap gap-2">
        <UBadge size="xs" color="success" variant="soft" icon="i-lucide-folder">
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
    </div>

    <div class="flex justify-end gap-2 sm:hidden">
      <UButton
        type="button"
        size="xs"
        variant="ghost"
        color="neutral"
        icon="i-lucide-pencil"
        @click.stop="$emit('edit', bookmark)"
      >
        <span class="sr-only">Edit</span>
      </UButton>
      <UButton
        type="button"
        size="xs"
        variant="soft"
        color="error"
        icon="i-lucide-trash-2"
        @click.stop="$emit('remove', bookmark.id)"
      />
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

defineEmits<{
  edit: [bookmark: BookmarkResponse & { folder_name?: string | null }];
  remove: [id: number];
  favorite: [bookmark: BookmarkResponse & { folder_name?: string | null }];
}>();
</script>
