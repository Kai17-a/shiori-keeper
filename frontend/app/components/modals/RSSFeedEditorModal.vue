<template>
  <UModal v-model:open="openModel" :title="title" :description="description">
    <template #content="{ close }">
      <form class="space-y-4 p-6" @submit.prevent="emit('save')">
        <UFormField label="Title" required class="w-full">
          <UInput v-model="form.title" :placeholder="titlePlaceholder" class="w-full" />
        </UFormField>

        <UFormField label="URL" required class="w-full">
          <UInput v-model="form.url" :placeholder="urlPlaceholder" class="w-full" />
        </UFormField>

        <UFormField label="Description" class="w-full">
          <UTextarea
            v-model="form.description"
            :placeholder="descriptionPlaceholder"
            :rows="4"
            class="w-full"
          />
        </UFormField>

        <div class="flex justify-end gap-3">
          <UButton type="button" color="neutral" variant="ghost" @click="close"> Cancel </UButton>
          <UButton type="submit" :loading="saving">
            {{ submitLabel }}
          </UButton>
        </div>
      </form>
    </template>
  </UModal>
</template>

<script setup lang="ts">
const openModel = defineModel<boolean>("open", { required: true });

defineProps<{
  form: {
    title: string;
    url: string;
    description: string;
  };
  title: string;
  description: string;
  titlePlaceholder: string;
  urlPlaceholder: string;
  descriptionPlaceholder: string;
  submitLabel: string;
  saving?: boolean;
}>();

const emit = defineEmits<{
  save: [];
}>();
</script>
