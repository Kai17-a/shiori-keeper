<template>
  <UButton
    type="button"
    :size="size"
    :variant="variant"
    :color="color"
    :icon="icon"
    :loading="loading"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <span class="sr-only">
      {{ label }}
    </span>
  </UButton>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
});

withDefaults(
  defineProps<{
    icon: string;
    label: string;
    color?: "primary" | "secondary" | "success" | "info" | "warning" | "error" | "neutral";
    variant?: "solid" | "soft" | "subtle" | "outline" | "ghost";
    size?: "xs" | "sm" | "md" | "lg" | "xl";
    loading?: boolean;
  }>(),
  {
    color: "neutral",
    variant: "ghost",
    size: "xs",
    loading: false,
  },
);

defineEmits<{
  click: [event: MouseEvent];
}>();
</script>
