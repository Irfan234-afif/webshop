<script setup lang="ts">
import type { ProductSpecification } from '@/types/productDetail'

interface Props {
  description: string
  specifications?: ProductSpecification[]
}

defineProps<Props>()
</script>

<template>
  <div class="flex flex-col gap-6 py-6">
    <!-- Section Title -->
    <h2 class="text-base font-bold text-gray-900 md:text-lg">Detail Produk</h2>

    <!-- Description -->
    <p class="text-sm font-normal leading-relaxed text-gray-700" v-html="description">
    </p>

    <!-- Specifications Table (if available) -->
    <div v-if="specifications && specifications.length > 0" class="flex flex-col gap-4">
      <h3 class="text-sm font-semibold text-gray-900">Spesifikasi</h3>

      <dl class="divide-y divide-gray-200 border-t border-b border-gray-200">
        <div
          v-for="spec in specifications"
          :key="spec.label"
          class="flex flex-col gap-2 py-3 sm:flex-row sm:gap-4"
        >
          <dt class="text-sm font-semibold text-gray-700 sm:w-1/3">
            {{ spec.label }}
          </dt>
          <dd class="text-sm text-gray-600 sm:w-2/3">
            {{ spec.value }}
          </dd>
        </div>
      </dl>
    </div>
  </div>
</template>
