import type { ApiProduct, Product } from '@/types/itemGroup'

/**
 * Transform API product to UI product format
 * Converts the Frappe API product structure to the format expected by ProductCard
 */
export function transformApiProduct(apiProduct: ApiProduct): Product {
  return {
    id: parseInt(apiProduct.name.replace('WEB-ITM-', '')) || 0,
    route: apiProduct.route,
    image: apiProduct.website_image,
    category: apiProduct.item_group,
    rating: 0, // TODO: Add rating field to API or calculate from reviews
    title: apiProduct.web_item_name,
    description: apiProduct.short_description || apiProduct.web_long_description || '',
    price: apiProduct.price_list_rate,
    originalPriceRange: apiProduct.formatted_mrp || undefined,
    discount: apiProduct.formatted_mrp
      ? calculateDiscount(apiProduct.price_list_rate, apiProduct.formatted_mrp)
      : undefined,
    hasDiscount: !!apiProduct.formatted_mrp,
    itemCode: apiProduct.item_code
  }
}

/**
 * Calculate discount percentage
 */
function calculateDiscount(currentPrice: number, formattedMrp: string): number {
  // Extract numeric value from formatted price (e.g., "Rp 1.000,00" -> 1000)
  const mrp = parseFloat(formattedMrp.replace(/[^\d,]/g, '').replace(',', '.'))
  if (isNaN(mrp) || mrp === 0) return 0

  const discountPercentage = ((mrp - currentPrice) / mrp) * 100
  return Math.round(discountPercentage)
}

/**
 * Transform array of API products
 */
export function transformApiProducts(apiProducts: ApiProduct[]): Product[] {
  return apiProducts.map(transformApiProduct)
}
