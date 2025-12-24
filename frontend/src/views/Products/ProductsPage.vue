<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import Modal from '@/components/common/Modal.vue'
import FilterSidebar from '@/components/features/products/FilterSidebar.vue'
import ProductGrid from '@/components/features/products/ProductGrid.vue'
import { useProductsStore } from '@/stores/products'
import { useFilterQuerySync } from '@/composables/useFilterQuerySync'

const productsStore = useProductsStore()

// Initialize URL query sync
useFilterQuerySync()

// Filter modal state
const isFilterModalOpen = ref(false)

const breadcrumbItems = [
  { label: 'Home', to: '/' },
  { label: 'Produk & Layanan' }
]

// Count active filters
const activeFilterCount = computed(() => {
  const filters = productsStore.activeFilters
  return filters.categories.length + filters.priceRanges.length
})

onMounted(async () => {
  // Fetch products on mount
  await productsStore.fetchProducts()
})
</script>

<template>
  <DefaultLayout store-name="KoperasiAuliya">
    <div class="min-h-screen bg-white">
      <Container class="py-4 md:py-6 lg:py-8">
        <!-- Breadcrumb -->
        <Breadcrumb :items="breadcrumbItems" class="mb-4 md:mb-6" />

        <!-- Page Title -->
        <h1 class="mb-6 text-xl font-bold capitalize text-gray-900 md:mb-8">
          Semua produk & Layanan
        </h1>

        <!-- Main Content Layout -->
        <div class="flex flex-col gap-8 lg:flex-row">
          <!-- Desktop Sidebar - Hidden on mobile -->
          <div class="hidden lg:block">
            <FilterSidebar />
          </div>

          <!-- Product Grid -->
          <div class="flex-1">
            <ProductGrid
              :products="productsStore.allProducts"
              :is-loading="productsStore.isLoading"
            />
          </div>
        </div>
      </Container>
    </div>

    <!-- Mobile Filter Button - Fixed at bottom -->
    <div class="fixed bottom-6 left-1/2 z-40 -translate-x-1/2 lg:hidden">
      <button
        @click="isFilterModalOpen = true"
        class="flex items-center gap-3 rounded-full bg-gray-900 px-6 py-3 text-white shadow-lg transition-transform hover:scale-105 active:scale-95"
      >
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        <span class="font-semibold">Filter</span>
        <span
          v-if="activeFilterCount > 0"
          class="flex h-6 min-w-[1.5rem] items-center justify-center rounded-full bg-secondary-alt px-2 text-xs font-bold"
        >
          {{ activeFilterCount }}
        </span>
      </button>
    </div>

    <!-- Mobile Filter Modal -->
    <Modal :is-open="isFilterModalOpen" title="Filter" @close="isFilterModalOpen = false">
      <FilterSidebar variant="modal" @apply="isFilterModalOpen = false" />
    </Modal>
  </DefaultLayout>
</template>

<style scoped>
/* Additional styles if needed */
</style>
