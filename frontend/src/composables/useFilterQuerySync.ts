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

    // Parse school units (comma-separated string)
    if (query.schoolUnits && typeof query.schoolUnits === 'string') {
      filters.schoolUnits = query.schoolUnits.split(',').filter(Boolean)
    }

    // Parse search
    if (query.search && typeof query.search === 'string') {
      productsStore.setSearchTerm(query.search)
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

    if (filters.schoolUnits.length > 0) {
      query.schoolUnits = filters.schoolUnits.join(',')
    }

    if (productsStore.searchTerm) {
      query.search = productsStore.searchTerm
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

  // Watch search term
  watch(
    () => productsStore.searchTerm,
    (newTerm) => {
      const query = filtersToQuery(productsStore.activeFilters)
      if (newTerm) {
        query.search = newTerm
      }

      router.replace({
        path: route.path,
        query
      })
    }
  )

  // Watch route query to sync back to store (URL -> Store)
  watch(
    () => route.query.search,
    (newSearch) => {
      if (typeof newSearch === 'string') {
        if (newSearch !== productsStore.searchTerm) {
          productsStore.setSearchTerm(newSearch)
        }
      } else if (!newSearch && productsStore.searchTerm) {
        // If search param removed, clear store
        productsStore.setSearchTerm('')
      }
    }
  )

  return {
    parseQueryToFilters,
    filtersToQuery
  }
}
