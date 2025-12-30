<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import QuantitySelector from '@/components/common/QuantitySelector.vue'
import WishlistButton from '@/components/common/WishlistButton.vue'
import { useAuthStore } from '@/stores/auth'
import type { ProductVariant } from '@/types/productDetail'

interface Props {
  quantity: number
  isInWishlist: boolean
  isAddingToCart?: boolean
  isTogglingWishlist?: boolean
  canAddToCart?: boolean
  selectedVariant: ProductVariant | null
  maxQuantity?: number
  isOutOfStock?: boolean
  isSubscriptionItem?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isAddingToCart: false,
  isTogglingWishlist: false,
  canAddToCart: true,
  isOutOfStock: false,
  isSubscriptionItem: false
})

const router = useRouter()
const authStore = useAuthStore()

const emit = defineEmits<{
  'update:quantity': [quantity: number]
  'addToCart': []
  'toggleWishlist': []
  'showLoginModal': []
}>()

// Check if user is a guest
const isGuest = computed(() => authStore.isGuest)

// Handle add to cart for guest users
const handleAddToCart = () => {
  if (isGuest.value) {
    // Navigate to login page
    router.push('/login')
  } else {
    // For authenticated users, emit the addToCart event
    emit('addToCart')
  }
}

// Button text based on authentication status
const buttonText = computed(() => {
  if (props.isOutOfStock) return 'Stok Habis'
  if (props.isSubscriptionItem) return 'Langganan Sekarang'
  return isGuest.value ? 'Login untuk Belanja' : 'Masukkan Ke Keranjang'
})
</script>

<template>
  <div class="flex flex-col gap-4 md:flex-row md:items-center">
    <!-- Quantity Selector -->
    <QuantitySelector :model-value="quantity" :max="maxQuantity"
      :disabled="isAddingToCart || isGuest || selectedVariant === null || isOutOfStock"
      @update:model-value="emit('update:quantity', $event)" />

    <!-- Wishlist Button -->
    <WishlistButton :is-in-wishlist="isInWishlist" :is-loading="isTogglingWishlist" @toggle="emit('toggleWishlist')" />

    <!-- Add to Cart Button -->
    <button type="button" :disabled="!canAddToCart || isAddingToCart || (isGuest && !canAddToCart) || isOutOfStock"
      :class="[
        'py-5 flex h-12 flex-1 items-center justify-center gap-2 rounded-xl px-6 text-sm font-bold text-white transition-all',
        isOutOfStock
          ? 'cursor-not-allowed bg-gray-400'
          : canAddToCart && !isAddingToCart && !isGuest
            ? 'bg-primary hover:bg-[#8B1A73] active:scale-95'
            : isGuest
              ? 'bg-[#8B1A73] hover:bg-[#7a1662] active:scale-95' // Different color for guest login button
              : 'cursor-not-allowed bg-gray-300'
      ]" @click="handleAddToCart">
      <!-- Loading Spinner -->
      <svg v-if="isAddingToCart" class="h-5 w-5 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
        </path>
      </svg>

      <!-- Button Text -->
      <span v-if="isAddingToCart">Menambahkan...</span>
      <span v-else>{{ buttonText }}</span>
    </button>
  </div>

  <!-- Validation Error Message -->
  <p v-if="!canAddToCart && !isAddingToCart && !isGuest && !isOutOfStock" class="text-sm text-red-500">
    Silakan pilih ukuran terlebih dahulu sebelum menambahkan ke keranjang
  </p>

  <!-- Guest Message -->
  <p v-if="isGuest" class="text-sm text-gray-600">
    Silakan login terlebih dahulu untuk menambahkan produk ke keranjang
  </p>
</template>
