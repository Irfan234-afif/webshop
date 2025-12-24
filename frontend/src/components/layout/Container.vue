<script setup lang="ts">
/**
 * Container component for consistent max-width and responsive padding across the app.
 *
 * Usage:
 * <Container>Your content here</Container>
 * <Container class="py-8">Content with additional classes</Container>
 */

interface Props {
  /**
   * Additional CSS classes to apply to the container
   */
  class?: string
}

withDefaults(defineProps<Props>(), {
  class: ''
})
</script>

<template>
  <div :class="['max-w-7xl mx-auto px-4', $props.class]">
    <slot />
  </div>
</template>
