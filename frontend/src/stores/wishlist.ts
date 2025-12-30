import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'
import type { WishlistItem } from '@/types/wishlist'

export const useWishlistStore = defineStore('wishlist', () => {
  // State
  const items = ref<WishlistItem[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Getters
  const isInWishlist = (productId: string) => {
    // Check if item_code (productId) is in the wishlist items
    // We assume productId passed here is item_code
    return items.value.some(item => item.productId === productId)
  }

  const itemCount = computed(() => items.value.length)

  // Actions
  const fetchWishlist = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await call('webshop.webshop.doctype.wishlist.wishlist.get_wishlist_items')
      if (Array.isArray(response)) {
        items.value = response.map((item: any) => ({
          id: item.name || item.website_item || item.item_code, // Use available ID
          productId: item.item_code,
          productType: 'product',
          addedAt: new Date(),
          title: item.title || item.web_item_name || item.item_name,
          image: item.image || item.website_image,
          itemGroup: item.item_group,
          route: item.route,
          price: item.price,
          formatted_price: item.formatted_price,
          formatted_mrp: item.formatted_mrp,
          discount: item.discount
        }))
      }
    } catch (e) {
      console.error('Failed to fetch wishlist:', e)
      error.value = e as Error
    } finally {
      isLoading.value = false
    }
  }

  const toggleWishlist = async (productId: string) => {
    isLoading.value = true
    error.value = null

    try {
      const isWished = isInWishlist(productId)
      let response
      
      if (isWished) {
        response = await call('webshop.webshop.doctype.wishlist.wishlist.remove_from_wishlist', {
            item_code: productId
        })
      } else {
        response = await call('webshop.webshop.doctype.wishlist.wishlist.add_to_wishlist', {
            item_code: productId
        })
      }

      // Update state with response from backend (which is the full list)
      if (Array.isArray(response)) {
        items.value = response.map((item: any) => ({
            id: item.name || item.website_item || item.item_code,
            productId: item.item_code,
            addedAt: new Date(),
            title: item.title || item.web_item_name || item.item_name,
            image: item.image || item.website_image,
            itemGroup: item.item_group,
            route: item.route,
            price: item.price,
            formatted_price: item.formatted_price,
            formatted_mrp: item.formatted_mrp,
            discount: item.discount
        }))
      }

    } catch (e) {
      error.value = e as Error
      console.error('Failed to toggle wishlist:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  const removeFromWishlist = async (productId: string) => {
     await toggleWishlist(productId)
  }

  const clearWishlist = () => {
    items.value = []
  }
    
  // Initialize
  // fetchWishlist()

  return {
    // State
    items,
    isLoading,
    error,
    // Getters
    itemCount,
    isInWishlist,
    // Actions
    fetchWishlist,
    toggleWishlist,
    removeFromWishlist,
    clearWishlist
  }
})
