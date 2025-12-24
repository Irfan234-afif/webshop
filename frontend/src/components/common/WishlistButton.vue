<script setup lang="ts">
interface Props {
  isInWishlist: boolean
  isLoading?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  size: 'md'
})

const emit = defineEmits<{
  toggle: []
}>()

const sizeClasses = {
  sm: 'h-10 w-10',
  md: 'h-12 w-12',
  lg: 'h-14 w-14'
}

const iconSizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6'
}
</script>

<template>
  <button
    type="button"
    :class="[
      'flex items-center justify-center rounded-full bg-white shadow-md transition-all hover:shadow-lg active:scale-95 disabled:cursor-not-allowed disabled:opacity-50',
      sizeClasses[size]
    ]"
    :disabled="isLoading"
    @click="emit('toggle')"
    :aria-label="isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="isLoading"
      :class="['animate-spin', iconSizeClasses[size]]"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>

    <!-- Heart Icon -->
    <svg
      v-else
      :class="[
        iconSizeClasses[size],
        'transition-all',
        isInWishlist ? 'text-red-500' : 'text-gray-700'
      ]"
      viewBox="0 0 24 24"
      :fill="isInWishlist ? 'currentColor' : 'none'"
      :stroke="isInWishlist ? 'none' : 'currentColor'"
      stroke-width="2"
    >
      <path
        d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
      />
    </svg>
  </button>
</template>
