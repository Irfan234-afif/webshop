
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { Product, ProductFilters, FilterOption } from '@/types/product'
import { frappeRequest } from 'frappe-ui'


export const useProductsStore = defineStore('products', () => {
  // State
  const allProducts = ref<Product[]>([])
  const categories = ref<{name: string, item_group_name: string}[]>([])
  const isLoading = ref(false)
  const error = ref<Error | null>(null)

  // Active Filters (synced with URL query params)
  const activeFilters = ref<ProductFilters>({
    categories: [],
    priceRanges: []
  })

  // Watchers
  watch(
    activeFilters,
    () => {
      fetchProducts()
    },
    { deep: true }
  )

  // Getters - Filtered Products
  const filteredProducts = computed(() => {
    let products = allProducts.value
    // Client-side filtering can still happen if we fetched all products,
    // but typically we rely on server side.
    // However, since we fetch 1000 items, we can rely on server filtering mostly.
    return products
  })

  // Getters - Available Filter Options with Counts
  const availableCategories = computed((): FilterOption[] => {
    return categories.value.map((c) => ({
      value: c.name,
      label: c.item_group_name || c.name,
      count: undefined // We don't have counts from this simple API yet
    }))
  })

  const availablePriceRanges = computed((): FilterOption[] => {
    const ranges = [
      { value: 'under-50k', label: '< Rp 50.000' },
      { value: '50k-100k', label: 'Rp 50.000 – Rp 100.000' },
      { value: '100k-200k', label: 'Rp 100.000 – Rp 200.000' },
      { value: 'over-200k', label: '> Rp 200.000' }
    ]
    return ranges.map((range) => ({
      ...range,
      count: undefined // We don't have counts from this simple API yet
    }))
  })

  const hasActiveFilters = computed(() => {
    return (
      activeFilters.value.categories.length > 0 ||
      activeFilters.value.priceRanges.length > 0
    )
  })

  // Actions
  const fetchCategories = async () => {
    try {
      const response = await frappeRequest({
        url: 'webshop.webshop.api.products.get_item_groups',
        method: 'GET'
      })
      categories.value = response || []
    } catch (e) {
      console.error('Failed to fetch categories:', e)
    }
  }

  const fetchProducts = async () => {
    isLoading.value = true
    error.value = null
    
    // Ensure categories are loaded
    if (categories.value.length === 0) {
       fetchCategories()
    }

    try {
      // Calculate price params
      let priceMin: number | undefined
      let priceMax: number | undefined
      
      if (activeFilters.value.priceRanges.length > 0) {
        let min = Infinity
        let max = -Infinity
        
        activeFilters.value.priceRanges.forEach(range => {
           if (range === 'under-50k') {
             min = Math.min(min, 0)
             max = Math.max(max, 50000)
           } else if (range === '50k-100k') {
             min = Math.min(min, 50000)
             max = Math.max(max, 100000)
           } else if (range === '100k-200k') {
             min = Math.min(min, 100000)
             max = Math.max(max, 200000)
           } else if (range === 'over-200k') {
             min = Math.min(min, 200000)
             max = Infinity
           }
        })
        
        if (min !== Infinity) priceMin = min
        if (max !== -Infinity && max !== Infinity) priceMax = max
      }

      const params: any = {
           page_length: 1000
      }

      if (activeFilters.value.categories.length > 0) {
          params.item_group = JSON.stringify(activeFilters.value.categories)
      }
      
      if (priceMin !== undefined) {
          params.price_min = priceMin
      }
      
      if (priceMax !== undefined) {
          params.price_max = priceMax
      }

      const response = await frappeRequest({
        url: 'webshop.webshop.api.products.get_products',
        method: 'GET',
        params
      })
      
      allProducts.value = response.items
      
    } catch (e) {
      error.value = e as Error
      console.error('Failed to fetch products:', e)
    } finally {
      isLoading.value = false
    }
  }

  const setFilters = (filters: Partial<ProductFilters>) => {
    activeFilters.value = {
      ...activeFilters.value,
      ...filters
    }
  }

  const toggleCategory = (category: string) => {
    const index = activeFilters.value.categories.indexOf(category)
    if (index > -1) {
      activeFilters.value.categories.splice(index, 1)
    } else {
      activeFilters.value.categories.push(category)
    }
  }



  const togglePriceRange = (range: string) => {
    const index = activeFilters.value.priceRanges.indexOf(range as any)
    if (index > -1) {
      activeFilters.value.priceRanges.splice(index, 1)
    } else {
      activeFilters.value.priceRanges.push(range as any)
    }
  }

  const clearFilters = () => {
    activeFilters.value = {
      categories: [],

      priceRanges: []
    }
  }

  return {
    // State
    allProducts,
    isLoading,
    error,
    activeFilters,
    // Getters
    filteredProducts,
    availableCategories,

    availablePriceRanges,
    hasActiveFilters,
    // Actions
    fetchProducts,
    setFilters,
    toggleCategory,

    togglePriceRange,
    clearFilters
  }
})
