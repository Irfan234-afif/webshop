<script setup lang="ts">
import NoProductIcon from '../icons/NoProductIcon.vue'

interface Props {
  image: string
  route: string
  category: string
  rating: number
  title: string
  description: string
  price: number
  originalPriceRange?: string
  discount?: number
  hasDiscount?: boolean
  isInWishlist?: boolean
  isSubscription?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  viewDetail: []
  toggleWishlist: []
}>()

const formattedPrice = (price: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price)
}
</script>

<template>
  <div class="bg-white flex flex-col w-full h-full">
    <!-- Image Container -->
    <div class="bg-gray-100 relative rounded-xl aspect-square w-full overflow-hidden">
      <img v-if="image" :src="image" :alt="title" class="w-full h-full object-contain" />
      <no-product-icon v-else />

      <!-- Subscription Badge -->
      <div v-if="isSubscription"
        class="absolute top-3 left-3 bg-purple-100 text-purple-600 px-2 py-1 rounded-md text-xs font-bold z-10 shadow-sm border border-purple-200">
        Berlangganan
      </div>

      <!-- Wishlist Button -->
      <button
        class="absolute top-6 right-6 rounded-full w-12 h-12 flex items-center justify-center transition-colors shadow-sm"
        :class="isInWishlist ? 'bg-red-50 text-red-500' : 'bg-white text-gray-400 hover:text-red-500'"
        @click="emit('toggleWishlist')" aria-label="Add to wishlist">
        <svg class="w-5 h-5" viewBox="0 0 24 24" :fill="isInWishlist ? 'currentColor' : 'none'" stroke="currentColor"
          stroke-width="2">
          <path
            d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>
      </button>
    </div>

    <!-- Content Container -->
    <div class="flex flex-col flex-1 gap-8 p-3 rounded-xl">
      <!-- Category and Rating -->
      <div class="flex items-center justify-between">
        <p class="text-sm font-semibold text-gray-500 capitalize">
          {{ category }}
        </p>
        <div class="flex items-center gap-1">
          <!-- Star Rating -->
          <div class="flex gap-0.5">
            <svg v-for="star in 5" :key="star" class="w-3 h-3"
              :class="star <= Math.floor(rating) ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor"
              viewBox="0 0 20 20">
              <path
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </div>
          <span class="text-sm font-semibold text-gray-500">({{ rating }})</span>
        </div>
      </div>

      <!-- Title and Description -->
      <div class="flex flex-col gap-5 capitalize">
        <router-link :to="`/products/${route}`">
          <h3 class="font-bold text-lg leading-tight text-gray-900 hover:underline cursor-pointer transition-all">
            {{ title }}
          </h3>
        </router-link>
        <p class="text-sm font-medium text-gray-500 leading-relaxed line-clamp-2">
          {{ description }}
        </p>
      </div>

      <!-- Pricing Section -->
      <div v-if="hasDiscount" class="flex flex-col gap-4">
        <!-- Discount and Price -->
        <div class="flex items-center gap-4">
          <div class="bg-danger rounded-lg px-2 py-2">
            <span class="text-sm font-semibold text-white capitalize">
              {{ discount }}%
            </span>
          </div>
          <p class="text-lg font-bold text-primary capitalize">
            {{ formattedPrice(price) }}
          </p>
        </div>

        <!-- Original Price Range with Strikethrough -->
        <div class="relative w-fit">
          <p class="text-sm font-semibold text-gray-500 capitalize">
            {{ originalPriceRange }}
          </p>
          <div class="absolute left-0 top-1/2 w-full h-0.5 bg-danger -translate-y-1/2" />
        </div>
      </div>

      <!-- Price without Discount -->
      <p v-else class="text-lg font-bold text-primary capitalize">
        {{ formattedPrice(price) }}
      </p>

      <!-- View Detail Button -->
      <router-link :to="`/products/${route}`" class="mt-auto w-full">
        <button
          class="w-full border border-gray-300 rounded-xl h-12 flex items-center justify-center hover:border-gray-400 transition-colors">
          <span class="text-sm font-bold text-gray-900 capitalize">
            Lihat Detail
          </span>
        </button>
      </router-link>
    </div>
  </div>
</template>
