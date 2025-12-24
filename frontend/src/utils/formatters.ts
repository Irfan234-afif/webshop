import type { PriceRange } from '@/types/product'

/**
 * Format number as Indonesian Rupiah currency
 * @param amount - The amount to format
 * @returns Formatted currency string (e.g., "Rp 150.000")
 */
export function formatIDR(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

/**
 * Calculate price range category based on price
 * @param price - The price to categorize
 * @returns Price range category
 */
export function calculatePriceRange(price: number): PriceRange {
  if (price < 50000) return 'under-50k'
  if (price < 100000) return '50k-100k'
  if (price < 200000) return '100k-200k'
  return 'over-200k'
}

/**
 * Format price label for services (e.g., "Mulai dari Rp 150.000/bulan")
 * @param pricePerMonth - Monthly price for the service
 * @returns Formatted service price label
 */
export function formatServicePrice(pricePerMonth: number): string {
  return `Mulai dari ${formatIDR(pricePerMonth)}/bulan`
}
