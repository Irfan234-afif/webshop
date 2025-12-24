<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWishlistStore } from '@/stores/wishlist'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import ProductCard from '@/components/common/ProductCard.vue'
import type { Product } from '@/types/itemGroup'

const router = useRouter()
const wishlistStore = useWishlistStore()

const breadcrumbItems = [
  { label: 'Home', to: '/' },
  { label: 'Wishlist' }
]

// Transform wishlist items to Product format for ProductCard
const wishlistProducts = computed<Product[]>(() => {
  return wishlistStore.items.map(item => {
    const hasDiscount = !!item.formatted_mrp
    const discount = hasDiscount && item.formatted_mrp && item.price
      ? calculateDiscount(item.price, item.formatted_mrp)
      : 0

    return {
      id: 0, // Not used for display
      route: item.route || '',
      image: item.image || '',
      category: item.itemGroup || 'Product',
      rating: 0,
      title: item.title || 'Untitled Product',
      description: '',
      price: item.price || 0,
      originalPriceRange: item.formatted_mrp,
      discount: discount,
      hasDiscount: hasDiscount,
      itemCode: item.productId
    }
  })
})

function calculateDiscount(currentPrice: number, formattedMrp: string): number {
  // Extract numeric value from formatted price (e.g., "Rp 1.000,00" -> 1000)
  const mrp = parseFloat(formattedMrp.replace(/[^\d,]/g, '').replace(',', '.'))
  if (isNaN(mrp) || mrp === 0) return 0

  const discountPercentage = ((mrp - currentPrice) / mrp) * 100
  return Math.round(discountPercentage)
}

const handleToggleWishlist = async (itemCode: string) => {
  await wishlistStore.toggleWishlist(itemCode)
}

const handleViewDetail = (route: string) => {
  router.push(`/products/${route}`)
}
</script>

<template>
  <DefaultLayout store-name="KoperasiAuliya">
    <div class="min-h-screen bg-white">
      <Container class="py-4 md:py-6 lg:py-8">
        <!-- Breadcrumb -->
        <Breadcrumb :items="breadcrumbItems" class="mb-4 md:mb-6" />

        <div class="flex flex-col gap-6">
          <h1 class="text-2xl font-bold text-gray-900">Wishlist Saya</h1>

          <!-- Loading State -->
          <div v-if="wishlistStore.isLoading && wishlistStore.items.length === 0" class="flex min-h-[400px] items-center justify-center">
            <div class="flex flex-col items-center gap-4">
               <svg class="h-10 w-10 animate-spin text-secondary-alt" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
               <p class="text-gray-500">Memuat wishlist...</p>
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="wishlistProducts.length === 0" class="flex min-h-[400px] flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-gray-200 bg-gray-50 py-12">
            <div class="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
               <svg class="h-8 w-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
               </svg>
            </div>
            <h3 class="text-lg font-medium text-gray-900">Wishlist Masih Kosong</h3>
            <p class="text-sm text-gray-500">Simpan produk favoritmu disini.</p>
            <router-link to="/products" class="mt-2 rounded-lg bg-primary px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-secondary-alt">
              Cari Produk
            </router-link>
          </div>

          <!-- Product Grid -->
          <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
             <div v-for="product in wishlistProducts" :key="product.itemCode" class="h-full">
                <ProductCard
                   :image="product.image"
                   :route="product.route"
                   :category="product.category"
                   :rating="product.rating"
                   :title="product.title"
                   :description="product.description"
                   :price="product.price"
                   :has-discount="false"
                   :is-in-wishlist="true"
                   @toggle-wishlist="handleToggleWishlist(product.itemCode)"
                   @view-detail="handleViewDetail(product.route)"
                />
             </div>
          </div>

        </div>
      </Container>
    </div>
  </DefaultLayout>
</template>
