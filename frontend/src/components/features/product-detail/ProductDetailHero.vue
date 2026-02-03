<script setup lang="ts">
import { computed, watch } from 'vue'
import type { ProductDetail, ProductVariant, VariantAttribute } from '@/types/productDetail'
import ProductImageGallery from './ProductImageGallery.vue'
import ProductInfo from './ProductInfo.vue'
import NoProductIcon from '@/components/icons/NoProductIcon.vue'

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
  lastSurveyStatus?: {
    has_survey: boolean
    status?: string
    admin_notes?: string
    request_date?: string
  }
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
  'startSurvey': []
}>()

const displayImages = computed(() => {
  if (props.selectedVariant && props.product.website_item_images && props.product.website_item_images.length > 0) {
    const variantImages = props.product.website_item_images
      .filter(img => img.for_variant === props.selectedVariant!.id)
      .map(img => img.image)

    if (variantImages.length > 0) {
      return variantImages
    }
  }
  return props.product.images || []
})

watch(displayImages, () => {
  emit('selectImage', 0)
})
</script>

<template>
  <div class="grid grid-cols-1 gap-8 md:grid-cols-2 md:gap-12">
    <!-- Left: Image Gallery -->
    <div v-if="displayImages && displayImages.length > 0">
      <ProductImageGallery :images="displayImages" :selected-index="selectedImageIndex"
        @select-image="emit('selectImage', $event)" />
    </div>
    <NoProductIcon v-else />
    <!-- Right: Product Info -->
    <ProductInfo :product="product" :selected-size="selectedSize" :selected-variant="selectedVariant"
      :quantity="quantity" :is-in-wishlist="isInWishlist" :is-adding-to-cart="isAddingToCart"
      :is-toggling-wishlist="isTogglingWishlist" :has-variant-stock="hasVariantStock"
      :some-selected-variant="someSelectedVariant" :last-survey-status="lastSurveyStatus"
      @update:quantity="emit('update:quantity', $event)"
      @select-size="emit('selectSize', $event)" @select-variant="emit('selectVariant', $event)"
      @customize="emit('customize')" @add-to-cart="emit('addToCart', $event)" @toggle-wishlist="emit('toggleWishlist')"
      @show-login-modal="emit('showLoginModal')" @select-date="emit('selectDate', $event)" 
      @start-survey="emit('startSurvey')" />
  </div>
</template>
