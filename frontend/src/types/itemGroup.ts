/**
 * API Product Response
 * Represents a product item as returned from the Frappe API
 */
export interface ApiProduct {
  name: string
  web_item_name: string
  item_name: string
  item_code: string
  website_image: string
  variant_of: string | null
  has_variants: number
  item_group: string
  web_long_description: string | null
  short_description: string | null
  route: string
  website_warehouse: string | null
  ranking: number
  on_backorder: number
  formatted_mrp: string | null
  formatted_price: string
  price_list_rate: number
  in_stock: boolean
  in_cart: boolean
  wished: boolean
}

/**
 * Product Interface
 * Represents a product item displayed in the item group section
 */
export interface Product {
  id: number
  route: string
  image: string
  category: string
  rating: number
  title: string
  description: string
  price: number
  originalPriceRange?: string
  discount?: number
  hasDiscount: boolean
  itemCode: string // Added for wishlist operations
}

/**
 * Promotional Card Interface
 * Represents the promotional/CTA card shown at the end of product carousel
 */
export interface PromotionalCard {
  icon: string // SVG string
  gradientFrom: string // Starting color of gradient (e.g., '#AC208E')
  gradientTo: string // Ending color of gradient (e.g., '#C263AD')
  title: string // Main heading text
  description: string // Description text
  ctaText: string // Call-to-action button text
}

/**
 * Item Group Section Props
 * Props for the ItemGroupSection component
 */
export interface ItemGroupSectionProps {
  title: string
  products: Product[]
  promotionalCard: PromotionalCard
}
