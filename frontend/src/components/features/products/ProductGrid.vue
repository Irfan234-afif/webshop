<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Product } from '@/types/product'
import ProductCard from '@/components/common/ProductCard.vue'
import ProductServiceCard from '@/components/common/ProductServiceCard.vue'
import { onMounted } from 'vue'

interface Props {
  products: Product[]
  isLoading?: boolean
}

interface Emits {
  (e: 'viewDetail', id: string): void
  (e: 'toggleWishlist', id: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()

const handleViewDetail = (id: string) => {
  emit('viewDetail', id)
  // Navigate to product detail page
  router.push({ name: 'product-detail', params: { id } })
}

const handleToggleWishlist = (id: string) => {
  emit('toggleWishlist', id)
  // TODO: Add to wishlist
  console.log('Toggle wishlist:', id)
}

onMounted(() => {
  console.log(props.products)
})
</script>

<template>
  <div class="w-full">
    <!-- Loading State -->
    <div
      v-if="isLoading"
      class="grid grid-cols-2 gap-4 md:grid-cols-2 md:gap-6 lg:grid-cols-3"
      aria-label="Loading products"
    >
      <div v-for="i in 6" :key="i" class="animate-pulse">
        <div class="flex h-full flex-col overflow-hidden rounded-xl bg-gray-200">
          <div class="h-[200px] md:h-[294px] bg-gray-300"></div>
          <div class="flex-1 space-y-4 p-6">
            <div class="h-4 rounded bg-gray-300"></div>
            <div class="h-6 rounded bg-gray-300"></div>
            <div class="h-4 rounded bg-gray-300"></div>
            <div class="h-10 rounded bg-gray-300"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="products.length === 0"
      class="flex flex-col items-center justify-center py-12 text-center md:py-20"
    >
      <svg
        class="mb-3 h-12 w-12 text-gray-400 md:mb-4 md:h-16 md:w-16"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
        />
      </svg>
      <h3 class="mb-2 text-base font-semibold text-gray-900 md:text-lg">Tidak ada produk ditemukan</h3>
      <p class="text-xs text-gray-500 md:text-sm">Coba ubah filter pencarian Anda</p>
    </div>

    <!-- Product Grid -->
    <div v-else class="grid grid-cols-2 gap-4 md:grid-cols-2 md:gap-6 lg:grid-cols-3">
      <template v-for="item in products" :key="item.name">
        <!-- Regular Product Card -->
        <ProductCard
          :image="item.website_image"
          :category="item.item_group"
          :rating="item.ranking"
          :route="item.route"
          :title="item.web_item_name"
          :description="item.short_description"
          :price="item.price_list_rate"
          :original-price-range="item.min_price ? `${item.min_price} - ${item.max_price}` : undefined"
          :discount="item.discount_percent"
          :has-discount="(item.discount_percent ?? 0) > 0"
          @view-detail="handleViewDetail(item.name)"
          @toggle-wishlist="handleToggleWishlist(item.name)"
        />

        <!-- Service Card -->
        <!-- <ProductServiceCard
          v-else-if="item.type === 'service'"
          :icon="item.icon"
          :icon-color="item.iconColor"
          :bg-gradient="item.bgGradient"
          :category="item.category"
          :rating="item.rating"
          :title="item.title"
          :description="item.description"
          :price-label="item.priceLabel"
          :info-notes="item.infoNotes"
          @view-detail="handleViewDetail(item.id)"
        /> -->
      </template>
    </div>
  </div>
</template>

<style scoped>
/* Additional styles if needed */
</style>
