import { watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import type { ProductFilters, PriceRange } from '@/types/product'

/**
 * Composable to sync product filters with URL query parameters
 * Provides bidirectional sync: URL <-> Store
 */
export function useFilterQuerySync() {
  const router = useRouter()
  const route = useRoute()
  const productsStore = useProductsStore()

  // Parse URL query params to filter state
  const parseQueryToFilters = (): Partial<ProductFilters> => {
    const query = route.query

    const filters: Partial<ProductFilters> = {}

    // Parse categories (comma-separated string)
    if (query.categories && typeof query.categories === 'string') {
      filters.categories = query.categories.split(',').filter(Boolean)
    }



    // Parse price ranges (comma-separated string)
    if (query.priceRanges && typeof query.priceRanges === 'string') {
      filters.priceRanges = query.priceRanges.split(',').filter(Boolean) as PriceRange[]
    }

    return filters
  }

  // Convert filter state to query params
  const filtersToQuery = (filters: ProductFilters) => {
    const query: Record<string, string> = {}

    if (filters.categories.length > 0) {
      query.categories = filters.categories.join(',')
    }



    if (filters.priceRanges.length > 0) {
      query.priceRanges = filters.priceRanges.join(',')
    }

    return query
  }

  // Initialize filters from URL on mount
  onMounted(() => {
    const initialFilters = parseQueryToFilters()
    if (Object.keys(initialFilters).length > 0) {
      productsStore.setFilters(initialFilters)
    }
  })

  // Watch store filters and update URL
  watch(
    () => productsStore.activeFilters,
    (newFilters) => {
      const query = filtersToQuery(newFilters)

      // Only update if query actually changed (avoid infinite loops)
      const currentQueryString = JSON.stringify(route.query)
      const newQueryString = JSON.stringify(query)

      if (currentQueryString !== newQueryString) {
        router.replace({
          path: route.path,
          query
        })
      }
    },
    { deep: true }
  )

  return {
    parseQueryToFilters,
    filtersToQuery
  }
}
