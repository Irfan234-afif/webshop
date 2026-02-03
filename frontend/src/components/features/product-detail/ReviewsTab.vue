<script setup lang="ts">
import { computed } from 'vue'
import type { Review } from '@/types/productDetail'
import ProductRating from '@/components/common/ProductRating.vue'

interface Props {
  reviews: Review[]
}

const props = defineProps<Props>()

// Format date as relative time
const formatRelativeTime = (dateString: string) => {
  const date = new Date(dateString)
  // Check if invalid date
  if (isNaN(date.getTime())) return dateString

  const now = new Date()
  const diffTime = Math.abs(now.getTime() - date.getTime())
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Hari ini'
  if (diffDays === 1) return 'Kemarin'
  if (diffDays < 7) return `${diffDays} hari yang lalu`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} minggu yang lalu`
  if (diffDays < 365) return `${Math.floor(diffDays / 30)} bulan yang lalu`
  return `${Math.floor(diffDays / 365)} tahun yang lalu`
}

// Sort reviews by date (newest first)
const sortedReviews = computed(() => {
  return [...props.reviews].sort((a, b) => {
    const dateA = new Date(a.createdAt).getTime()
    const dateB = new Date(b.createdAt).getTime()
    return dateB - dateA
  })
})
</script>

<template>
  <div class="flex flex-col gap-6 py-6">
    <!-- Section Title and Count -->
    <div class="flex items-center justify-between">
      <h2 class="text-base font-bold text-gray-900 md:text-lg">
        Ulasan ({{ reviews.length }})
      </h2>
    </div>

    <!-- Reviews List -->
    <div v-if="reviews.length > 0" class="flex flex-col gap-6">
      <div
        v-for="review in sortedReviews"
        :key="review.id"
        class="flex flex-col gap-3 border-b border-gray-200 pb-6 last:border-b-0 last:pb-0"
      >
        <!-- Reviewer Info -->
        <div class="flex items-start justify-between gap-4">
          <div class="flex items-center gap-3">
            <!-- Avatar -->
            <div
              v-if="review.authorAvatar"
              class="h-10 w-10 overflow-hidden rounded-full bg-gray-200"
            >
              <img
                :src="review.authorAvatar"
                :alt="review.author"
                class="h-full w-full object-cover"
              />
            </div>
            <div
              v-else
              class="flex h-10 w-10 items-center justify-center rounded-full bg-gray-200"
            >
              <span class="text-sm font-semibold text-gray-600">
                {{ review.author.charAt(0).toUpperCase() }}
              </span>
            </div>

            <!-- Author and Date -->
            <div class="flex flex-col">
              <p class="text-sm font-semibold text-gray-900">{{ review.author }}</p>
              <p class="text-xs text-gray-500">{{ formatRelativeTime(review.createdAt) }}</p>
            </div>
          </div>

          <!-- Rating -->
          <ProductRating
            :rating="review.rating * 5"
            :show-review-count="false"
            size="sm"
          />
        </div>

        <!-- Review Comment -->
        <p class="text-sm leading-relaxed text-gray-700">
          {{ review.comment }}
        </p>

        <!-- Review Images (if any) -->
        <div
          v-if="review.images && review.images.length > 0"
          class="flex gap-2 overflow-x-auto"
        >
          <img
            v-for="(image, index) in review.images"
            :key="index"
            :src="image"
            :alt="`Review image ${index + 1}`"
            class="h-20 w-20 flex-shrink-0 rounded-lg object-cover"
          />
        </div>

        <!-- Helpful Count -->
        <div v-if="review.helpful > 0" class="flex items-center gap-2 text-xs text-gray-500">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
          </svg>
          <span>{{ review.helpful }} orang merasa ini membantu</span>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <svg class="mb-4 h-16 w-16 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
      </svg>
      <h3 class="mb-2 text-base font-semibold text-gray-900">Belum Ada Ulasan</h3>
      <p class="text-sm text-gray-500">Jadilah yang pertama memberikan ulasan untuk produk ini</p>
    </div>
  </div>
</template>
