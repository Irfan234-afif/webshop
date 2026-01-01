<script setup lang="ts">
import { ref, onMounted, onUnmounted, onActivated, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductDetailStore } from '@/stores/productDetail'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useProductDetail } from '@/composables/useProductDetail'
import { useAlertStore } from '@/stores/alert'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import ProductDetailHero from '@/components/features/product-detail/ProductDetailHero.vue'
import ProductTabs from '@/components/features/product-detail/ProductTabs.vue'
import PromotionalBanner from '@/components/features/product-detail/PromotionalBanner.vue'
import RelatedProducts from '@/components/features/product-detail/RelatedProducts.vue'

// Set component name for KeepAlive caching
defineOptions({
  name: 'ProductDetailPage'
})

const route = useRoute()
const router = useRouter()
const productDetailStore = useProductDetailStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const productDetailLogic = useProductDetail()
const alertStore = useAlertStore()


// Get product ID from route params
const productId = computed(() => route.params.id as string)

// Breadcrumb items
const breadcrumbItems = computed(() => {
  const items: Array<{ label: string; to?: string }> = [
    { label: 'Home', to: '/' },
    { label: 'Produk & Layanan', to: '/products' }
  ]

  if (productDetailStore.currentProduct) {
    // Add category if different from "Produk & Layanan"
    if (productDetailStore.currentProduct.category !== 'Produk & Layanan') {
      items.push({ label: productDetailStore.currentProduct.category })
    }
    // Add product title
    items.push({ label: productDetailStore.currentProduct.title })
  } else {
    items.push({ label: 'Loading...' })
  }

  return items
})

// Check if product is in wishlist
const isInWishlist = computed(() => {
  if (!productDetailStore.currentProduct) return false
  return wishlistStore.isInWishlist(productDetailStore.currentProduct.item_code)
})

// Service date selection
const selectedServiceDate = ref<string>('')

const handleSelectDate = (date: string) => {
  selectedServiceDate.value = date
}

// Handlers
const handleAddToCart = async (serviceStartDate?: string) => {
  if (!productDetailStore.currentProduct) return
  if (!productDetailLogic.selectedItemVariant.value) {
    alertStore.warning('Silakan pilih varian terlebih dahulu', 'Peringatan')
    return
  }

  // const hasVariants =
  //   !!productDetailStore.currentProduct.variants &&
  //   productDetailStore.currentProduct.variants.length > 0

  // TODO: Validate variant selection for products with variants  
  // if (hasVariants && !productDetailLogic.selectedVariant.value) {
  //   alert('Silakan pilih varian terlebih dahulu')
  //   return
  // }

  // Validate size selection for products with sizes
  // if (!productDetailLogic.canAddToCart(
  //   productDetailStore.currentProduct.type === 'product' &&
  //   !!productDetailStore.currentProduct.sizes &&
  //   productDetailStore.currentProduct.sizes.length > 0
  // )) {
  //   alert('Silakan pilih ukuran terlebih dahulu')
  //   return
  // }

  // Check if there's an active student selected
  if (!cartStore.activeStudent) {
    alertStore.warning('Silakan pilih siswa terlebih dahulu di menu profil', 'Peringatan')
    return
  }

  // Validate service date for subscription items
  if (productDetailStore.currentProduct.is_subscription_item) {
    if (!selectedServiceDate.value) {
      alertStore.warning('Silakan pilih tanggal layanan terlebih dahulu', 'Peringatan')
      return
    }
    let itemCode = productDetailLogic.selectedItemVariant.value?.item_code || productDetailStore.currentProduct.item_code;
    // Redirect to subscription checkout
    router.push({
      path: `/subscription-checkout/${itemCode}`,
      query: {
        start_date: selectedServiceDate.value
      }
    })
    return
  }

  try {
    let itemCode = productDetailLogic.selectedItemVariant.value!.item_code;

    await cartStore.addToCart({
      item_code: itemCode,
      qty: productDetailLogic.quantity.value,
      student: cartStore.activeStudent,
      service_start_date: serviceStartDate || selectedServiceDate.value || undefined
    })

    // Show success message
    alertStore.success('Produk berhasil ditambahkan ke keranjang!', 'Berhasil')

    // Reset quantity
    productDetailLogic.quantity.value = 1
  } catch (error) {
    console.error('Error adding to cart:', error)
    alertStore.error('Gagal menambahkan ke keranjang. Silakan coba lagi.', 'Gagal')
  }
}

const handleToggleWishlist = async () => {
  if (!productDetailStore.currentProduct) return

  try {
    await wishlistStore.toggleWishlist(
      productDetailStore.currentProduct.item_code,
    )
  } catch (error) {
    console.error('Error toggling wishlist:', error)
    alertStore.error('Gagal mengubah wishlist. Silakan coba lagi.', 'Gagal')
  }
}

const handleCustomizeSize = () => {
  // TODO: Open customize size modal or redirect to custom size page
  console.log('Customize size clicked')
  alertStore.info('Fitur customize size akan segera hadir!', 'Info')
}

// Handler for showing login modal when guest tries to add to cart
const handleShowLoginModal = () => {
  // Navigate to login page
  router.push('/login')
}

interface BannerContent {
  type?: string
  image?: string
  title?: string
  subtitle?: string
  cta_text?: string
  cta_url?: string
  right_image?: string
}

const promotionalBannerContent = ref<BannerContent | undefined>(undefined)

const fetchPromotionalBanner = async () => {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.website.get_banner_content?banner_key=Product Detail Promo')
    const data = await response.json()
    if (data.message) {
      promotionalBannerContent.value = data.message
    }
  } catch (error) {
    console.error('Failed to fetch promotional banner:', error)
  }
}

// Track last loaded product ID to prevent unnecessary refetches
const lastLoadedProductId = ref<string>('')

// Function to load product data
const loadProduct = async (id: string) => {
  try {
    // Only fetch if product ID changed or no product loaded
    if (lastLoadedProductId.value !== id) {
      // Fetch banner in parallel (only once)
      if (!promotionalBannerContent.value) {
        fetchPromotionalBanner()
      }

      await productDetailStore.fetchProductDetail(id)
      lastLoadedProductId.value = id

      // Handle case where product has no variants
      if (!productDetailStore.currentProduct?.variants) {
        productDetailLogic.selectedItemVariant.value = {
          id: productDetailStore.currentProduct!.id,
          price: productDetailStore.currentProduct!.price,
          stockQuantity: productDetailStore.currentProduct!.stockQuantity ?? 0,
          attributes: [],
          inStock: productDetailStore.currentProduct!.inStock,
          item_code: productDetailStore.currentProduct!.item_code
        }
      }
    }
  } catch (error) {
    console.error('Error fetching product:', error)
    // Optionally redirect to products page or show error
  }
}

// Watch for productId changes (when navigating between products while component is cached)
watch(productId, (newId) => {
  if (newId) {
    loadProduct(newId)
  }
}, { immediate: false })

// Lifecycle hooks
onMounted(async () => {
  // Initial load
  await loadProduct(productId.value)
})

// Called when component is re-activated from KeepAlive cache
onActivated(() => {
  // Re-check if we need to load a different product
  if (productId.value && lastLoadedProductId.value !== productId.value) {
    loadProduct(productId.value)
  }
})

// onUnmounted(() => {
//   productDetailStore.clearProductDetail()
//   productDetailLogic.reset()
// })
</script>

<template>
  <DefaultLayout store-name="KoperasiAuliya">
    <div class="min-h-screen bg-white">
      <Container class="py-4 md:py-6 lg:py-8">
        <!-- Breadcrumb -->
        <Breadcrumb :items="breadcrumbItems" class="mb-4 md:mb-6" />

        <!-- Loading State -->
        <div v-if="productDetailStore.isLoading" class="flex min-h-[600px] items-center justify-center">
          <div class="flex flex-col items-center gap-4">
            <svg class="h-12 w-12 animate-spin text-secondary-alt" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            <p class="text-sm font-medium text-gray-600">Memuat produk...</p>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="productDetailStore.error" class="flex min-h-[600px] flex-col items-center justify-center gap-4">
          <svg class="h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 class="text-xl font-bold text-gray-900">Produk Tidak Ditemukan</h2>
          <p class="text-sm text-gray-600">{{ productDetailStore.error.message }}</p>
          <button type="button"
            class="mt-4 rounded-xl bg-secondary-alt px-6 py-3 text-sm font-bold text-white transition-all hover:bg-opacity-90 active:scale-95"
            @click="router.push('/products')">
            Kembali ke Produk
          </button>
        </div>

        <!-- Product Detail Content -->
        <div v-else-if="productDetailStore.currentProduct" class="flex flex-col gap-12">
          <!-- Hero Section: Image Gallery + Product Info -->
          <ProductDetailHero :product="productDetailStore.currentProduct"
            :selected-image-index="productDetailLogic.selectedImageIndex.value"
            :selected-size="productDetailLogic.selectedSize.value"
            :selected-variant="productDetailLogic.selectedItemVariant.value"
            :quantity="productDetailLogic.quantity.value" :is-in-wishlist="isInWishlist"
            :is-adding-to-cart="cartStore.isLoading" :is-toggling-wishlist="wishlistStore.isLoading"
            :some-selected-variant="productDetailLogic.someSelectedVariant"
            :has-variant-stock="productDetailLogic.hasVariantStock" @select-image="productDetailLogic.selectImage"
            @update:quantity="productDetailLogic.setQuantity" @select-size="productDetailLogic.selectSize"
            @select-variant="productDetailLogic.selectVariant" @customize="handleCustomizeSize"
            @add-to-cart="handleAddToCart" @toggle-wishlist="handleToggleWishlist"
            @show-login-modal="handleShowLoginModal" @select-date="handleSelectDate" />

          <!-- Tabs Section: Details, Size Chart, Reviews -->
          <ProductTabs :product="productDetailStore.currentProduct" :active-tab="productDetailLogic.activeTab.value"
            @update:active-tab="productDetailLogic.setActiveTab" />

          <!-- Promotional Banner -->
          <PromotionalBanner :content="promotionalBannerContent" />

          <!-- Related Products -->
          <!-- <RelatedProducts
            :products="productDetailStore.relatedProducts"
            title="Produk Terkait"
          /> -->
        </div>
      </Container>
    </div>
  </DefaultLayout>
</template>
