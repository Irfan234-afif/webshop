<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useProductDetailStore } from '@/stores/productDetail'
import type { ProductDetail, ProductVariant, VariantAttribute } from '@/types/productDetail'
import ProductRating from '@/components/common/ProductRating.vue'
import ProductPricing from './ProductPricing.vue'
import ServiceField from './ServiceField.vue'
import VariantSelector from './VariantSelector.vue'
import AddToCartSection from './AddToCartSection.vue'

interface Props {
  product: ProductDetail
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

const productDetailStore = useProductDetailStore()

onMounted(() => {
  console.log("ProductInfo mounted with product: ", props.product);
})

const emit = defineEmits<{
  'update:quantity': [quantity: number]
  'selectSize': [size: string]
  'selectVariant': [variant: VariantAttribute]
  'customize': []
  'addToCart': [serviceStartDate?: string]
  'toggleWishlist': []
  'showLoginModal': []
  'selectDate': [date: string]
}>()

// Check if size selection is required and valid
const canAddToCart = computed(() => {
  if (props.product.variants && props.product.variants.length > 0) {
    return props.selectedVariant !== null
  }
  return true
})

// Verify if variant prices are lazy loaded (checking if priceRange exists and no explicit price on variant)
const isLazyLoadingPrice = computed(() => {
  return props.product.variants && props.product.variants.length > 0 && props.product.priceRange
})

// Watch selected variant to fetch price
watch(() => props.selectedVariant, async (newVariant) => {
  if (newVariant && newVariant.item_code) {
    // Only fetch if we are in lazy loading mode or if price is missing
    if (isLazyLoadingPrice.value || !newVariant.price) {
      await productDetailStore.fetchVariantPrice(newVariant.item_code)
    }
  } else {
    productDetailStore.clearVariantPrice()
  }
})

// Calculate price to display
const displayPrice = computed(() => {
  // If variant selected
  if (props.selectedVariant) {
    // Use fetched price from store if available
    if (productDetailStore.selectedVariantPrice?.price) {
      return productDetailStore.selectedVariantPrice.price
    }
    // Fallback to variant price on prop (if exists)
    if (props.selectedVariant.price) {
      return props.selectedVariant.price
    }
    // If loading or error, return undefined to handle in template
    return undefined
  }

  // If lazy loading mode and no variant selected, show range (return undefined to ProductPricing)
  if (isLazyLoadingPrice.value) {
    return undefined
  }

  // Fallback to product base price
  return props.product.price
})

const displayOriginalPrice = computed(() => {
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.originalPrice) {
    return productDetailStore.selectedVariantPrice.originalPrice
  }
  return props.product.originalPrice
})

const displayDiscount = computed(() => {
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.discountPercent) {
    return productDetailStore.selectedVariantPrice.discountPercent
  }
  return props.product.discountPercent
})

const displayHasDiscount = computed(() => {
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.discountPercent) {
    return productDetailStore.selectedVariantPrice.discountPercent > 0
  }
  return props.product.hasDiscount
})

// Check if product is globally out of stock
const isOutOfStock = computed(() => {
  if (props.product.variants && props.product.variants.length > 0) {
    return props.product.variants.every(variant => !variant.inStock)
  }
  return !props.product.inStock
})

// Info notes for discounts
const infoNotes = computed(() => {
  const notes: string[] = []
  if (displayHasDiscount.value) {
    notes.push('Diskon 15% Khusus untuk siswa baru tahun ini')
    notes.push('Diskon Gratis Ongkos kirim')
  }
  return notes.length > 0 ? notes : undefined
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Category Badge -->
    <div class="inline-flex w-fit items-center gap-2">
      <span class="rounded-full bg-gray-100 px-3 py-1 text-sm font-semibold capitalize text-gray-500">
        {{ product.category }}
      </span>
      <!-- Separator Dot -->
      <div class="h-1.5 w-1.5 rounded-full bg-gray-300" />
    </div>

    <!-- Rating -->
    <ProductRating :rating="product.rating" :review-count="product.reviewCount" size="md" />

    <!-- Title and Description -->
    <div class="flex flex-col gap-5">
      <h1 class="text-xl !font-bold capitalize leading-tight text-gray-900 md:text-2xl">
        {{ product.title }}
      </h1>
      <p class="text-sm font-medium leading-relaxed text-gray-500">
        {{ product.short_description }}
      </p>
    </div>

    <!-- Pricing Section -->
    <div v-if="productDetailStore.selectedVariantPrice?.loading" class="animate-pulse">
      <div class="h-8 w-48 rounded bg-gray-200"></div>
    </div>
    <ProductPricing v-else :price="displayPrice" :price-range="product.priceRange"
      :original-price="displayOriginalPrice" :discount="displayDiscount" :has-discount="displayHasDiscount"
      :offers="product.offers" />

    <!-- Service Field -->
    <ServiceField v-if="product.is_subscription_item" @select-date="emit('selectDate', $event)" />
    <!-- <div v-else-if="product.type === 'service'" class="flex flex-col gap-4">
      <p class="text-xl font-bold capitalize text-primary">
        {{ product.priceLabel }}
      </p>
      Service Info Notes
      <div v-if="product.infoNotes && product.infoNotes.length > 0" class="flex flex-col gap-2">
        <div
          v-for="(note, index) in product.infoNotes"
          :key="index"
          class="flex items-center gap-2"
        >
          <svg class="h-4 w-4 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-xs font-medium capitalize text-gray-600">
            {{ note }}
          </span>
        </div>
      </div>
    </div> -->

    <!-- Variant Selector (Only for products with variants) -->
    <VariantSelector v-if="product.attributes && product.attributes.length > 0" :variants="product.attributes"
      :is-service="product.is_subscription_item" :selected-variant="selectedVariant"
      :has-variant-stock="hasVariantStock" :some-selected-variant="someSelectedVariant"
      @select-variant="emit('selectVariant', $event)" />

    <!-- Size Selector (Only for products with sizes and no variants) -->
    <!-- <SizeSelector
      v-if="
        product.type === 'product' &&
        (!product.variants || product.variants.length === 0) &&
        product.sizes &&
        product.sizes.length > 0
      "
      :sizes="product.sizes"
      :selected-size="selectedSize"
      :disabled="isAddingToCart"
      @select="emit('selectSize', $event)"
      @customize="emit('customize')"
    /> -->


    <!-- Add to Cart Section -->
    <AddToCartSection :quantity="quantity" :is-in-wishlist="isInWishlist" :is-adding-to-cart="isAddingToCart"
      :is-toggling-wishlist="isTogglingWishlist" :can-add-to-cart="canAddToCart" :max-quantity="product.stockQuantity"
      :selected-variant="selectedVariant" :is-out-of-stock="isOutOfStock"
      :is-subscription-item="!!product.is_subscription_item" @update:quantity="emit('update:quantity', $event)"
      @add-to-cart="emit('addToCart')" @toggle-wishlist="emit('toggleWishlist')"
      @show-login-modal="emit('showLoginModal')" />
  </div>
</template>
