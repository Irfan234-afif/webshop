import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ProductDetail } from '@/types/productDetail'
import type { Product } from '@/types/product'
import { productsMockData } from '@/data/products'

export const useProductDetailStore = defineStore('productDetail', () => {
  // State
  const currentProduct = ref<ProductDetail | null>(null)
  const relatedProducts = ref<Product[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Getters
  const hasImages = computed(() =>
    currentProduct.value?.images && currentProduct.value.images.length > 0
  )

  const hasReviews = computed(() =>
    currentProduct.value?.reviews && currentProduct.value.reviews.length > 0
  )

  const averageRating = computed(() => {
    if (!currentProduct.value?.reviews || currentProduct.value.reviews.length === 0) {
      return currentProduct.value?.rating || 0
    }
    const sum = currentProduct.value.reviews.reduce((acc, r) => acc + r.rating, 0)
    return Number((sum / currentProduct.value.reviews.length).toFixed(1))
  })

  const hasSizeChart = computed(() =>
    currentProduct.value?.sizeChart !== undefined
  )

  const hasSpecifications = computed(() =>
    currentProduct.value?.specifications && currentProduct.value.specifications.length > 0
  )

  // Actions
  const fetchProductDetail = async (route: string) => {
    isLoading.value = true
    error.value = null

    try {
      // Call the real API endpoint using route
      const response = await fetch(`/api/method/webshop.webshop.api.products.get_product_detail?route=${encodeURIComponent(route)}`)

      if (!response.ok) {
        throw new Error('Product not found')
      }

      const data = await response.json()

      if (data.message) {
        currentProduct.value = data.message as ProductDetail
        console.log("is_subscription_item", currentProduct.value.is_subscription_item)
      } else {
        throw new Error('Invalid response from server')
      }

      // Fetch related products (same category, exclude current)
      if (currentProduct.value) {
        await fetchRelatedProducts(currentProduct.value.category, route)
      }

    } catch (e) {
      error.value = e as Error
      console.error('Failed to fetch product detail:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const fetchRelatedProducts = async (category: string, excludeId: string) => {
    try {
      // TODO: Replace with actual API call
      // const response = await frappeRequest({
      //   url: `/api/method/webshop.api.get_related_products`,
      //   params: { category, exclude: excludeId, limit: 6 }
      // })
      // relatedProducts.value = response.message

      // Mock implementation: filter by same category, limit to 6 products
      relatedProducts.value = productsMockData
        .filter(p => p.category === category && p.id !== excludeId)
        .slice(0, 6)
    } catch (e) {
      console.error('Failed to fetch related products:', e)
      // Don't throw - related products are not critical
    }
  }

  const clearProductDetail = () => {
    currentProduct.value = null
    relatedProducts.value = []
    error.value = null
  }

  return {
    // State
    currentProduct,
    relatedProducts,
    isLoading,
    error,
    // Getters
    hasImages,
    hasReviews,
    hasSizeChart,
    hasSpecifications,
    averageRating,
    // Actions
    fetchProductDetail,
    fetchRelatedProducts,
    clearProductDetail
  }
})
