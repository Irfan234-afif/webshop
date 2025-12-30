<script setup lang="ts">
import type { ProductOrService } from '@/types/product'
import ProductGrid from '@/components/features/products/ProductGrid.vue'

interface Props {
  products: ProductOrService[]
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Produk Terkait'
})
</script>

<template>
  <div v-if="products.length > 0" class="flex flex-col gap-6">
    <!-- Section Heading -->
    <h2 class="text-xl font-bold text-gray-900 md:text-2xl">
      {{ title }}
    </h2>

    <!-- Products Grid -->
    <ProductGrid
      :products="products"
      :is-loading="false"
    />
  </div>
</template>
