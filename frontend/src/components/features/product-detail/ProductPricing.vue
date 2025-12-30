<script setup lang="ts">
import { formatIDR } from '@/utils/formatters'
import { computed } from 'vue'
import type { Offer, ProductPriceRange } from '@/types/productDetail'

interface Props {
  price?: number
  priceRange?: ProductPriceRange
  originalPrice?: string
  discount?: number
  hasDiscount?: boolean
  offers?: Offer[]
}

const props = defineProps<Props>()

const hasPriceRange = computed(
  () => props.priceRange && !props.price
)
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Discount & Price Section -->
    <div v-if="hasDiscount && discount && price" class="flex flex-col gap-4">
      <!-- Discount Badge and Current Price -->
      <div class="flex items-center gap-4">
        <!-- Discount Badge -->
        <div class="rounded-lg bg-red-500 px-3 py-2">
          <span class="text-sm font-semibold capitalize text-white">
            {{ discount }}%
          </span>
        </div>

        <!-- Current Price -->
        <p class="text-xl font-bold capitalize text-primary">
          {{ formatIDR(price || 0) }}
        </p>
      </div>

      <!-- Original Price with Strikethrough -->
      <div v-if="originalPrice" class="relative w-fit">
        <p class="text-sm font-semibold capitalize text-gray-500">
          {{ originalPrice }}
        </p>
        <!-- Strikethrough line -->
        <div class="absolute left-0 top-1/2 h-0.5 w-full -translate-y-1/2 bg-red-500" />
      </div>
    </div>

    <p v-else-if="hasPriceRange && priceRange" class="text-xl font-bold capitalize text-primary">
      {{ formatIDR(priceRange.min_price) }} - {{ formatIDR(priceRange.max_price) }}
    </p>

    <!-- Price without Discount -->
    <p v-else class="text-xl font-bold capitalize text-primary">
      {{ formatIDR(price || 0) }}
    </p>

    <!-- Info Badges (Discount conditions) -->
    <div v-if="offers && offers.length > 0" class="flex flex-col gap-3">
      <div
        v-for="(offer, index) in offers"
        :key="index"
        class="flex items-center gap-3"
      >
        <!-- Sale Icon -->
        <svg class="h-6 w-6 flex-shrink-0 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="flex gap-1">
          <span class="text-xs !font-bold capitalize text-gray-700">
            {{ offer.offer_title }}
          </span>
          <span class="text-xs font-medium capitalize text-gray-700">
            {{ offer.offer_subtitle }}
          </span>
        </p>
      </div>
    </div>
  </div>
</template>
