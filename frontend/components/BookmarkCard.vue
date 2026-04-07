<template>
  <article class="card">
    <div class="head">
      <div class="content">
        <a :href="bookmark.url" target="_blank" rel="noreferrer">{{ bookmark.title }}</a>
        <p class="url">{{ bookmark.url }}</p>
        <p class="desc">{{ bookmark.description || "" }}</p>
        <div class="tags">
          <span v-for="tag in bookmark.tags" :key="tag.id" class="tag">{{ tag.name }}</span>
        </div>
      </div>
      <div class="actions">
        <button @click="$emit('edit', bookmark)">Edit</button>
        <button class="danger" @click="$emit('remove', bookmark.id)">Delete</button>
      </div>
    </div>
  </article>
</template>

<script setup>
defineProps({
  bookmark: {
    type: Object,
    required: true,
  },
})

defineEmits(["edit", "remove"])
</script>

<style scoped>
.card {
  border-radius: 20px;
  border: 1px solid rgba(51, 65, 85, 1);
  background: rgba(15, 23, 42, 0.82);
  padding: 14px;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.content {
  min-width: 0;
}

a {
  color: #ffffff;
  font-weight: 700;
  text-decoration: none;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.url,
.desc {
  color: #94a3b8;
  font-size: 13px;
  word-break: break-all;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  border-radius: 999px;
  border: 1px solid rgba(125, 211, 252, 0.3);
  background: rgba(125, 211, 252, 0.1);
  color: #bae6fd;
  padding: 4px 8px;
  font-size: 12px;
}

.actions {
  display: flex;
  gap: 8px;
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

.danger {
  border-color: rgba(244, 63, 94, 0.35);
  color: #fecdd3;
}
</style>
