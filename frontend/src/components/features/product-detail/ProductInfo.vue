<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useProductDetailStore } from '@/stores/productDetail'
import type { ProductDetail, ProductVariant, VariantAttribute } from '@/types/productDetail'
import ProductRating from '@/components/common/ProductRating.vue'
import ProductPricing from './ProductPricing.vue'
import ServiceField from './ServiceField.vue'
import VariantSelector from './VariantSelector.vue'
import AddToCartSection from './AddToCartSection.vue'
import { formatIDR } from '@/utils/formatters'

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

const productDetailStore = useProductDetailStore()


const emit = defineEmits<{
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

// Calculate price to display (multiplied by quantity)
const displayPrice = computed(() => {
  let unitPrice = 0
  
  // If variant selected
  if (props.selectedVariant) {
    // Use fetched price from store if available
    if (productDetailStore.selectedVariantPrice?.price) {
      unitPrice = productDetailStore.selectedVariantPrice.price
    }
    // Fallback to variant price on prop (if exists)
    else if (props.selectedVariant.price) {
      unitPrice = props.selectedVariant.price
    }
  } 
  
  // If lazy loading mode and no variant selected, show range (return undefined to ProductPricing)
  else if (isLazyLoadingPrice.value) {
    return undefined
  }

  // Fallback to product base price
  else {
    unitPrice = props.product.price || 0
  }
  
  if (unitPrice > 0) {
    return unitPrice * props.quantity
  }
  
  return undefined
})

const displayDiscount = computed(() => {
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.discountPercent) {
    return productDetailStore.selectedVariantPrice.discountPercent
  }
  return props.product.discountPercent
})

const displayOriginalPrice = computed(() => {
  // If we have a calculated current price (total) and discount, derive expected original total
  // original = current / ((100 - discount) / 100)
  const currentTotal = displayPrice.value
  const discount = displayDiscount.value

  if (currentTotal !== undefined && discount && discount > 0) {
    const originalTotal = currentTotal * 100 / (100 - discount)
    return formatIDR(Math.round(originalTotal))
  }

  // Fallback if no calculation possible (e.g. qty 1, or no discount found to use for calc)
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.originalPrice) {
    return productDetailStore.selectedVariantPrice.originalPrice
  }
  return props.product.originalPrice
})

const displayHasDiscount = computed(() => {
  if (props.selectedVariant && productDetailStore.selectedVariantPrice?.discountPercent) {
    return productDetailStore.selectedVariantPrice.discountPercent > 0
  }
  return props.product.hasDiscount
})

// Check if product is globally out of stock
const isOutOfStock = computed(() => {
  // When allow_items_not_in_stock is enabled, never consider items as out of stock
  if (props.product.allowItemsNotInStock) return false

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


    <!-- Survey Section -->
    <template v-if="product.can_survey">
      <!-- Status Survey Display -->
      <div v-if="lastSurveyStatus?.has_survey" class="rounded-lg bg-blue-50 p-4 border border-blue-100">
        <div class="flex items-center justify-between mb-2">
          <h3 class="font-bold text-blue-900">Status Survey Terakhir</h3>
          <span 
            class="px-3 py-1 rounded-full text-sm font-bold capitalize"
            :class="{
              'bg-yellow-100 text-yellow-800': lastSurveyStatus.status === 'Pending',
              'bg-green-100 text-green-800': lastSurveyStatus.status === 'Approved',
              'bg-red-100 text-red-800': lastSurveyStatus.status === 'Reject'
            }"
          >
            {{ lastSurveyStatus.status }}
          </span>
        </div>
        <p v-if="lastSurveyStatus.admin_notes" class="text-sm text-blue-800 mt-2">
          <span class="font-bold">Catatan Admin:</span> {{ lastSurveyStatus.admin_notes }}
        </p>
        <p class="text-xs text-blue-600 mt-2">
          Diajukan pada: {{ new Date(lastSurveyStatus.request_date!).toLocaleDateString('id-ID') }}
        </p>
      </div>

      <!-- Ajukan Survey Button -->
      <button
        @click="emit('startSurvey')"
        class="w-full rounded-xl border-2 border-primary bg-white px-6 py-3 font-bold text-primary transition-all hover:bg-primary hover:text-white"
      >
        Ajukan Survey
      </button>
    </template>

    <!-- Variant Selector (Only for products with variants) -->
    <VariantSelector v-if="product.attributes && product.attributes.length > 0" :variants="product.attributes"
      :is-service="product.is_subscription_item" :selected-variant="selectedVariant"
      :has-variant-stock="hasVariantStock" :some-selected-variant="someSelectedVariant"
      @select-variant="emit('selectVariant', $event)" />

    <!-- Add to Cart Section -->
    <AddToCartSection :quantity="quantity" :is-in-wishlist="isInWishlist" :is-adding-to-cart="isAddingToCart"
      :is-toggling-wishlist="isTogglingWishlist" :can-add-to-cart="canAddToCart" :max-quantity="product.allowItemsNotInStock ? undefined : product.stockQuantity"
      :selected-variant="selectedVariant" :is-out-of-stock="isOutOfStock"
      :is-subscription-item="!!product.is_subscription_item" @update:quantity="emit('update:quantity', $event)"
      @add-to-cart="emit('addToCart')" @toggle-wishlist="emit('toggleWishlist')"
      @show-login-modal="emit('showLoginModal')" />
  </div>
</template>
