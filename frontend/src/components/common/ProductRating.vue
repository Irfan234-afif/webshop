<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  rating: number
  reviewCount?: number
  showReviewCount?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  reviewCount: 0,
  showReviewCount: true,
  size: 'md'
})

// Size configurations
const starSizeClasses = {
  sm: 'h-3 w-3',
  md: 'h-4 w-4',
  lg: 'h-5 w-5'
}

const textSizeClasses = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base'
}

const gapClasses = {
  sm: 'gap-0.5',
  md: 'gap-1',
  lg: 'gap-1.5'
}

// Calculate filled stars (support decimal ratings)
const filledStars = computed(() => Math.floor(props.rating))
const hasHalfStar = computed(() => props.rating % 1 >= 0.5)
const emptyStars = computed(() => 5 - filledStars.value - (hasHalfStar.value ? 1 : 0))

// Format review count
const formattedReviewCount = computed(() => {
  if (!props.reviewCount) return '(0)'

  // Format large numbers (e.g., 1,240 reviews)
  return `(${props.reviewCount.toLocaleString('id-ID')})`
})
</script>

<template>
  <div class="flex items-center gap-2">
    <!-- Stars -->
    <div :class="['flex items-center', gapClasses[size]]">
      <!-- Filled Stars -->
      <svg
        v-for="star in filledStars"
        :key="`filled-${star}`"
        :class="[starSizeClasses[size], 'text-yellow-400']"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
        />
      </svg>

      <!-- Half Star (if applicable) -->
      <svg
        v-if="hasHalfStar"
        :class="[starSizeClasses[size], 'text-yellow-400']"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <defs>
          <linearGradient id="half-star-gradient">
            <stop offset="50%" stop-color="currentColor" />
            <stop offset="50%" stop-color="#D1D5DB" stop-opacity="1" />
          </linearGradient>
        </defs>
        <path
          fill="url(#half-star-gradient)"
          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
        />
      </svg>

      <!-- Empty Stars -->
      <svg
        v-for="star in emptyStars"
        :key="`empty-${star}`"
        :class="[starSizeClasses[size], 'text-gray-300']"
        fill="currentColor"
        viewBox="0 0 20 20"
      >
        <path
          d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
        />
      </svg>
    </div>

    <!-- Rating Number and Review Count -->
    <span
      v-if="showReviewCount"
      :class="[textSizeClasses[size], 'font-semibold text-gray-500']"
    >
      {{ rating.toFixed(1) }} {{ formattedReviewCount }} Reviews
    </span>
    <span
      v-else
      :class="[textSizeClasses[size], 'font-semibold text-gray-500']"
    >
      {{ rating.toFixed(1) }}
    </span>
  </div>
</template>
