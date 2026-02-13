// Product Detail type definitions for the product detail page

import type { PriceRange } from './product'

/**
 * Comprehensive product detail interface
 * Extends the basic product information with additional detail fields
 */
export interface ProductDetail {
  id: string
  item_code: string
  route: string
  is_subscription_item: boolean
  can_survey?: number | boolean


  // Basic info (shared between products and services)
  title: string
  category: string
  short_description: string
  description: string
  rating: number
  reviewCount: number

  // Product-specific fields
  images?: string[] // Array of image URLs for gallery
  website_item_images?: WebsiteItemImage[] // Array of images with variant info
  price?: number
  originalPrice?: string // For displaying strikethrough price
  discountPercent?: number // Discount percentage (e.g., 15)
  hasDiscount?: boolean

  // Service-specific fields
  icon?: string
  iconColor?: string
  bgGradient?: string
  pricePerMonth?: number
  priceLabel?: string
  infoNotes?: string[] // Info notes for services

  // Variants and sizes (for products)
  variants?: ProductVariant[]
  attributes?: ProductAttribute[]

  // Additional product details
  specifications?: ProductSpecification[]
  sizeChart?: SizeChartData
  offers?: Offer[]
  reviews?: Review[]
  relatedProductIds?: string[]

  // Stock and availability
  inStock: boolean
  stockQuantity?: number
  allowItemsNotInStock?: boolean

  // Metadata
  classGrade?: number[]
  priceRange?: ProductPriceRange
}

export interface ProductPriceRange {
  min_price: number
  max_price: number
}

/**
 * Product variant (size/color combinations)
 */
export interface ProductVariant {
  id: string
  item_code: string
  price?: number // Price override for this variant
  inStock: boolean
  stockQuantity: number
  attributes: VariantAttribute[]
}

/** 
 * Product attribute key-value pair
 */
export interface VariantAttribute {
  attribute: string // e.g., "Warna", "Bahan"
  attribute_value: string
}

export interface ProductAttribute {
  attribute: string // e.g., "Warna", "Bahan"
  values: string[] // e.g., ["Merah", "Biru", "Hijau"]
}

/**
 * Product specification item
 * Displayed in the "Detail Produk" tab
 */
export interface ProductSpecification {
  label: string // e.g., "Bahan", "Warna", "Ukuran Tersedia"
  value: string // e.g., "Katun Premium", "Putih Abu-abu", "S - 7XL"
}

/**
 * Size chart data structure
 * Displayed in the "Ukuran (Size Chart)" tab
 */
export interface SizeChartData {
  headers: string[] // e.g., ['Ukuran', 'Lingkar Dada (cm)', 'Panjang (cm)']
  rows: SizeChartRow[]
}

/**
 * Size chart row with dynamic columns
 */
export interface SizeChartRow {
  [key: string]: string // Dynamic columns based on headers
}

/**
 * Customer review interface
 */
export interface Review {
  id: string
  productId: string
  author: string
  authorAvatar?: string
  rating: number // 0-1 (normalized)
  comment: string
  createdAt: string
  helpful: number // Number of "helpful" votes
  images?: string[] // Review images (optional)
}

/**
 * Product detail store state
 */
export interface ProductDetailState {
  currentProduct: ProductDetail | null
  relatedProducts: ProductDetail[]
  isLoading: boolean
  error: Error | null
}

/**
 * Info badge for displaying discount conditions
 */
export interface InfoBadge {
  icon: string // Icon name or component
  text: string // Badge text
}

export interface Offer {
    offer_title:    string;
    offer_subtitle: string;
}

export interface WebsiteItemImage {
    image: string
    for_variant?: string | null
}