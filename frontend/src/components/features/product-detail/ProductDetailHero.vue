<script setup lang="ts">
import type { ProductDetail, ProductVariant, VariantAttribute } from '@/types/productDetail'
import ProductImageGallery from './ProductImageGallery.vue'
import ProductInfo from './ProductInfo.vue'

interface Props {
  product: ProductDetail
  selectedImageIndex: number
  selectedSize: string | null
  selectedVariant: ProductVariant | null
  quantity: number
  isInWishlist: boolean
  isAddingToCart?: boolean
  isTogglingWishlist?: boolean
  hasVariantStock: (variant: VariantAttribute) => boolean
  someSelectedVariant: (variant: VariantAttribute) => boolean
}

const props = withDefaults(defineProps<Props>(), {
  isAddingToCart: false,
  isTogglingWishlist: false
})

const emit = defineEmits<{
  'selectImage': [index: number]
  'update:quantity': [quantity: number]
  'selectSize': [size: string]
  'selectVariant': [variant: VariantAttribute]
  'customize': []
  'addToCart': [serviceStartDate?: string]
  'toggleWishlist': []
  'showLoginModal': []
  'selectDate': [date: string]
}>()
</script>

<template>
  <div class="grid grid-cols-1 gap-8 lg:grid-cols-2 lg:gap-12">
    <!-- Left: Image Gallery -->
    <div v-if="product.images && product.images.length > 0">
      <ProductImageGallery :images="product.images" :selected-index="selectedImageIndex"
        @select-image="emit('selectImage', $event)" />
    </div>

    <!-- Service Icon Display (for services without image gallery) -->
    <!-- <div
      v-else-if="product.type === 'service'"
      class="flex items-center justify-center rounded-xl p-12"
      :style="{ background: product.bgGradient }"
    >
      Service icon placeholder
      <div class="flex h-32 w-32 items-center justify-center rounded-full bg-white/20">
        <span class="text-6xl" :style="{ color: product.iconColor }">
          {{ product.icon }}
        </span>
      </div>
    </div> -->

    <!-- Right: Product Info -->
    <ProductInfo :product="product" :selected-size="selectedSize" :selected-variant="selectedVariant"
      :quantity="quantity" :is-in-wishlist="isInWishlist" :is-adding-to-cart="isAddingToCart"
      :is-toggling-wishlist="isTogglingWishlist" :has-variant-stock="hasVariantStock"
      :some-selected-variant="someSelectedVariant" @update:quantity="emit('update:quantity', $event)"
      @select-size="emit('selectSize', $event)" @select-variant="emit('selectVariant', $event)"
      @customize="emit('customize')" @add-to-cart="emit('addToCart', $event)" @toggle-wishlist="emit('toggleWishlist')"
      @show-login-modal="emit('showLoginModal')" @select-date="emit('selectDate', $event)" />
  </div>
</template>
