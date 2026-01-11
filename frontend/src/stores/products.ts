
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { Product, ProductFilters, FilterOption } from '@/types/product'
import { frappeRequest } from 'frappe-ui'


export const useProductsStore = defineStore('products', () => {
  // State
  const allProducts = ref<Product[]>([])
  const categories = ref<{name: string, item_group_name: string}[]>([])
  const schoolUnits = ref<{name: string}[]>([])
  const grades = ref<{name: string, grade_name: string, school_unit: string}[]>([])
  const isLoading = ref(false)
  const isLoadingMore = ref(false)
  const error = ref<Error | null>(null)
  
  // Pagination State
  const hasMore = ref(true)
  const nextStart = ref(0)
  const pageLength = ref(12)

  const activeFilters = ref<ProductFilters>({
    categories: [],
    priceRanges: [],
    schoolUnits: [],
    grades: []
  })

  // Watchers
  watch(
    activeFilters,
    () => {
      fetchProducts()
    },
    { deep: true }
  )

  // Clear grade filters when school unit selection changes
  watch(
    () => activeFilters.value.schoolUnits,
    (newUnits, oldUnits) => {
      // Only clear if school units actually changed
      if (JSON.stringify(newUnits) !== JSON.stringify(oldUnits)) {
        // Remove any selected grades that don't belong to the new school unit selection
        activeFilters.value.grades = activeFilters.value.grades.filter((gradeName) => {
          const grade = grades.value.find((g) => g.name === gradeName)
          return grade && newUnits.includes(grade.school_unit)
        })
      }
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

  const availableSchoolUnits = computed((): FilterOption[] => {
    return schoolUnits.value.map((s) => ({
      value: s.name,
      label: s.name,
      count: undefined
    }))
  })

  const availableGrades = computed((): FilterOption[] => {
    // Only show grades if a school unit is selected
    if (activeFilters.value.schoolUnits.length === 0) {
      return []
    }
    
    // Filter grades that belong to selected school units
    return grades.value
      .filter((g) => activeFilters.value.schoolUnits.includes(g.school_unit))
      .map((g) => ({
        value: g.name,
        label: g.grade_name,
        count: undefined
      }))
  })

  const hasActiveFilters = computed(() => {
    return (
      activeFilters.value.categories.length > 0 ||
      activeFilters.value.priceRanges.length > 0 ||
      activeFilters.value.schoolUnits.length > 0 ||
      activeFilters.value.grades.length > 0
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

  const fetchSchoolUnits = async () => {
    try {
      const response = await frappeRequest({
        url: 'webshop.webshop.api.products.get_school_units',
        method: 'GET'
      })
      schoolUnits.value = response || []
    } catch (e) {
      console.error('Failed to fetch school units:', e)
    }
  }

  const fetchGrades = async () => {
    try {
      const response = await frappeRequest({
        url: 'webshop.webshop.api.products.get_grades',
        method: 'GET'
      })
      grades.value = response || []
    } catch (e) {
      console.error('Failed to fetch grades:', e)
    }
  }

  const fetchProducts = async ({ loadMore = false } = {}) => {
    if (isLoading.value || isLoadingMore.value) return

    // Set appropriate loading state based on action
    if (loadMore) {
      isLoadingMore.value = true
    } else {
      isLoading.value = true
    }
    error.value = null
    
    // Ensure categories and school units are loaded
    if (categories.value.length === 0) {
       fetchCategories()
    }
    if (schoolUnits.value.length === 0) {
       fetchSchoolUnits()
    }
    if (grades.value.length === 0) {
       fetchGrades()
    }

    try {
      // Reset if not loading more
      if (!loadMore) {
        nextStart.value = 0
        hasMore.value = true
        // temporary clear provided we aren't appending
        // allProducts.value = [] // Optional: clear immediately or wait for response to avoid flicker
      }

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
           start: nextStart.value,
           page_length: pageLength.value
      }

      if (activeFilters.value.categories.length > 0) {
          params.item_group = JSON.stringify(activeFilters.value.categories)
      }

      if (activeFilters.value.schoolUnits.length > 0) {
          // Backend expects simple list or single value, but handled mostly as list if implemented generic
          // But our loop implementation expected single string if not adapted
          // Wait, backend logic for item_group handled list serialization.
          // For school_unit, I implemented generic check in products.py
          // products.py passes school_unit directly. Query logic handles it.
          // If query logic expects single value?
          // "params['school_unit'] = school_unit" in query.py
          // "i.school_unit = %(school_unit)s"
          // This implies single value equality.
          // If we want multiple, we need "IN".
          // I implemented "=" in query.py: conditions.append("i.school_unit = %(school_unit)s")
          // This is single value match.
          // I should probably restrict frontend to single selection OR update backend to IN.
          // Given the FilterGroup usually allows multiple, I should probably have used IN.
          // But for now, let's just pass one if multiple selected, or better pass it properly if backend supports list.
          // Backend just does condition.append.
          // I will pass the first one for now to be safe with current backend implementation.
          // Or even better, pass it and if it fails, it fails (but it will fail if list is passed to %s and expected string in DB driver? no, frappe handles it?)
          // No, usually in raw sql with %(name)s, it expects value.
          
          // Let's pass the list now that backend supports it
          if (activeFilters.value.schoolUnits.length > 0) {
             params.school_unit = JSON.stringify(activeFilters.value.schoolUnits)
          }
      }

       // Grade filter
       if (activeFilters.value.grades.length > 0) {
          params.grade = JSON.stringify(activeFilters.value.grades)
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
      
      const newItems = response.items || []
      const pagination = response.pagination || {}

      if (loadMore) {
        allProducts.value = [...allProducts.value, ...newItems]
      } else {
        allProducts.value = newItems
      }

      // Update pagination state
      if (pagination.next_start !== undefined) {
          nextStart.value = pagination.next_start
          hasMore.value = pagination.has_more
      } else {
          // Fallback if backend doesn't return standard pagination object
          hasMore.value = newItems.length === pageLength.value
          nextStart.value += newItems.length
      }
      
    } catch (e) {
      error.value = e as Error
      console.error('Failed to fetch products:', e)
    } finally {
      isLoading.value = false
      isLoadingMore.value = false
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

  const toggleSchoolUnit = (unit: string) => {
    const index = activeFilters.value.schoolUnits.indexOf(unit)
    if (index > -1) {
      activeFilters.value.schoolUnits.splice(index, 1)
    } else {
      activeFilters.value.schoolUnits.push(unit)
    }
  }

  const toggleGrade = (grade: string) => {
    const index = activeFilters.value.grades.indexOf(grade)
    if (index > -1) {
      activeFilters.value.grades.splice(index, 1)
    } else {
      activeFilters.value.grades.push(grade)
    }
  }

  const clearFilters = () => {
    activeFilters.value = {
      categories: [],
      priceRanges: [],
      schoolUnits: [],
      grades: []
    }
  }

  return {
    // State
    allProducts,
    isLoading,
    isLoadingMore,
    error,
    activeFilters,
    // Getters
    filteredProducts,
    availableCategories,

    availablePriceRanges,
    availableSchoolUnits,
    availableGrades,
    hasActiveFilters,
    hasMore,
    nextStart,
    // Actions
    fetchProducts,
    setFilters,
    toggleCategory,
    toggleSchoolUnit,
    toggleGrade,
    togglePriceRange,
    clearFilters
  }
})
