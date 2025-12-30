<script setup lang="ts">
import type { FilterOption } from '@/types/product'

interface Props {
  title: string
  options: FilterOption[]
  selected: (string | number)[]
}

interface Emits {
  (e: 'toggle', value: string | number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isSelected = (value: string | number): boolean => {
  return props.selected.includes(value)
}
</script>

<template>
  <div class="flex flex-col gap-6 border-b border-gray-200 pb-6 last:border-b-0 lg:gap-8 lg:pb-8">
    <!-- Section Title -->
    <h4 class="text-sm !font-bold capitalize text-gray-900 md:text-base">
      {{ title }}
    </h4>

    <!-- Filter Options -->
    <div class="flex flex-col gap-3 lg:gap-4">
      <label
        v-for="option in options"
        :key="option.value"
        class="flex cursor-pointer items-center gap-4 transition-opacity hover:opacity-80"
      >
        <!-- Checkbox -->
        <div class="relative flex h-6 w-6 shrink-0 items-center justify-center">
          <input
            type="checkbox"
            :checked="isSelected(option.value)"
            @change="emit('toggle', option.value)"
            class="peer sr-only"
          />
          <!-- Unchecked state -->
          <div
            class="h-6 w-6 rounded border-2 border-gray-400 transition-all peer-checked:border-secondary-alt peer-checked:bg-secondary-alt"
          ></div>
          <!-- Checkmark -->
          <svg
            class="pointer-events-none absolute h-4 w-4 scale-0 text-white transition-transform peer-checked:scale-100"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="3"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>

        <!-- Label -->
        <span
          class="text-sm font-semibold"
          :class="isSelected(option.value) ? 'text-gray-900' : 'text-gray-500'"
        >
          {{ option.label }}
        </span>

        <!-- Count Badge (optional) -->
        <span v-if="option.count !== undefined" class="ml-auto text-xs text-gray-400">
          ({{ option.count }})
        </span>
      </label>
    </div>
  </div>
</template>

<style scoped>
/* Additional styles if needed */
</style>
