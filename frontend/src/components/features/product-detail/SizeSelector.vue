<script setup lang="ts">
interface Props {
  sizes: string[]
  selectedSize: string | null
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  select: [size: string]
  customize: []
}>()
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Label -->
    <h3 class="text-base font-semibold text-gray-900">Ukuran Tersedia</h3>

    <!-- Size Buttons Grid -->
    <div class="flex flex-wrap gap-3">
      <!-- Size Buttons -->
      <button
        v-for="size in sizes"
        :key="size"
        type="button"
        :disabled="disabled"
        :class="[
          'min-w-[60px] rounded-lg border-2 px-4 py-2.5 text-sm font-semibold transition-all',
          selectedSize === size
            ? 'border-primary bg-primary/10 text-primary'
            : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400 hover:bg-gray-50',
          disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
        ]"
        @click="emit('select', size)"
        :aria-pressed="selectedSize === size"
      >
        {{ size }}
      </button>

      <!-- Customize Size Button -->
      <button
        type="button"
        :disabled="disabled"
        class="min-w-[120px] rounded-lg border-2 border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:border-gray-400 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
        @click="emit('customize')"
      >
        Customize Size
      </button>
    </div>

    <!-- Size Validation Message -->
    <p v-if="!selectedSize && !disabled" class="text-xs text-gray-500">
      Silakan pilih ukuran terlebih dahulu
    </p>
  </div>
</template>
