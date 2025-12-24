// Wishlist type definitions

/**
 * Wishlist item interface
 * Represents a single item in the user's wishlist
 */
export interface WishlistItem {
  id: string // Unique wishlist item ID
  productId: string // Reference to product or service
  productType: 'product' | 'service'
  addedAt: Date // When the item was added to wishlist
  // Display fields
  title?: string
  image?: string
  itemGroup?: string
  route?: string // For navigation
  // Price details
  price?: number
  formatted_price?: string
  formatted_mrp?: string
  discount?: string | number
}

/**
 * Wishlist state interface
 */
export interface WishlistState {
  items: WishlistItem[]
  isLoading: boolean
  error: Error | null
}
