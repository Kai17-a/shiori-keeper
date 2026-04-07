<template>
  <aside :class="['sidebar', { open: open }]">
    <div class="brand">
      <p>Bookmark Manager</p>
      <strong>Dashboard</strong>
    </div>

    <nav class="menu">
      <NuxtLink to="/" class="menu-link" @click="$emit('navigate')">Overview</NuxtLink>
      <NuxtLink to="/bookmarks" class="menu-link" @click="$emit('navigate')">Bookmarks</NuxtLink>
      <NuxtLink to="/folders" class="menu-link" @click="$emit('navigate')">Folders</NuxtLink>
      <NuxtLink to="/tags" class="menu-link" @click="$emit('navigate')">Tags</NuxtLink>
    </nav>
  </aside>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false,
  },
})

defineEmits(["navigate"])
</script>
