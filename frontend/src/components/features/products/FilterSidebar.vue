<script setup lang="ts">
import { useProductsStore } from '@/stores/products'
import FilterGroup from './FilterGroup.vue'
import PrimaryButton from '@/components/common/PrimaryButton.vue';

interface Props {
  variant?: 'default' | 'modal'
}

withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const emit = defineEmits<{
  apply: []
}>()

const productsStore = useProductsStore()

const handleToggleCategory = (value: string | number) => {
  productsStore.toggleCategory(value as string)
}



const handleTogglePriceRange = (value: string | number) => {
  productsStore.togglePriceRange(value as string)
}

const handleToggleSchoolUnit = (value: string | number) => {
  productsStore.toggleSchoolUnit(value as string)
}

const handleToggleGrade = (value: string | number) => {
  productsStore.toggleGrade(value as string)
}

const handleClearFilters = () => {
  productsStore.clearFilters()
}
</script>

<template>
  <aside :class="[
    'w-full shrink-0 self-start sticky top-20 sm:top-24 lg:top-28',
    variant === 'default'
      ? 'rounded-xl bg-mute p-6 lg:w-72 lg:p-8'
      : 'p-0'
  ]" :style="variant === 'default' ? 'border: 1.5px solid rgba(30, 30, 30, 0.1)' : ''">
    <!-- Header -->
    <div v-if="variant === 'default' || productsStore.hasActiveFilters"
      :class="['flex items-center justify-between', variant === 'default' ? 'mb-8 lg:mb-12' : 'mb-6']">
      <h3 v-if="variant === 'default'" class="text-base !font-bold capitalize text-gray-900 md:text-lg">
        Filters
      </h3>
      <button v-if="productsStore.hasActiveFilters" @click="handleClearFilters" :class="[
        'font-semibold text-danger transition-opacity hover:opacity-80',
        variant === 'default' ? 'text-xs md:text-sm' : 'text-sm',
        variant === 'modal' ? 'ml-auto' : ''
      ]">
        Hapus Filter
      </button>
    </div>

    <!-- Filter Groups -->
    <div class="flex flex-col gap-6 lg:gap-8">
      <!-- Category Filter -->
      <FilterGroup title="Kategori" :options="productsStore.availableCategories"
        :selected="productsStore.activeFilters.categories" @toggle="handleToggleCategory" />



      <FilterGroup title="Unit" :options="productsStore.availableSchoolUnits"
        :selected="productsStore.activeFilters.schoolUnits" @toggle="handleToggleSchoolUnit" />

      <!-- Grade Filter - Only show when a Unit is selected -->
      <FilterGroup v-if="productsStore.activeFilters.schoolUnits.length > 0" title="Kelas"
        :options="productsStore.availableGrades" :selected="productsStore.activeFilters.grades"
        @toggle="handleToggleGrade" />

      <!-- Price Range Filter -->
      <FilterGroup title="Harga" :options="productsStore.availablePriceRanges"
        :selected="productsStore.activeFilters.priceRanges" @toggle="handleTogglePriceRange" />
    </div>

    <!-- Apply Button (Modal variant only) -->
    <div v-if="variant === 'modal'" class="mt-8">
      <PrimaryButton @click="emit('apply')" variant="primary" size="medium" class="w-full">
        Tampilkan {{ productsStore.filteredProducts.length }} Produk
      </PrimaryButton>
    </div>
  </aside>
</template>

<style scoped>
/* Additional styles if needed */
</style>
