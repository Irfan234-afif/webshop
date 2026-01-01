<script setup lang="ts">
import type { ProductAttribute, ProductVariant, VariantAttribute } from '@/types/productDetail'
import { useProductDetail } from '../../../composables/useProductDetail'
import { computed, onMounted } from 'vue'

interface Props {
  variants: ProductAttribute[]
  selectedVariant: ProductVariant | null
  hasVariantStock: (variant: VariantAttribute) => boolean
  someSelectedVariant: (variant: VariantAttribute) => boolean
  isService?: boolean | number
}

const emit = defineEmits(['select-variant'])

const props = defineProps<Props>()

const selectVariant = (variant: VariantAttribute) => {
  // Always emit the variant - the parent will handle toggle logic
  emit('select-variant', variant)
}
// const { hasVariantStock, someSelectedVariant, selectedVariant } = useProductDetail()

</script>

<template>
  <div class="mb-6" v-for="variant in variants">
    <h3 class="mb-4 text-sm font-semibold text-gray-900">{{ variant.attribute }}</h3>
    <div class="flex flex-wrap gap-3">
      <button v-for="value in variant.values" type="button"
        class="rounded-lg px-4 py-2.5 text-sm font-semibold transition-all" :class="[
          hasVariantStock({ attribute: variant.attribute, attribute_value: value })
            ? 'border-2 border-gray-200 bg-white text-gray-900 hover:border-secondary-alt'
            : 'cursor-not-allowed border-2 border-gray-100 bg-gray-50 text-gray-400',
          {
            '!border-secondary !bg-secondary-surface text-secondary-alt': someSelectedVariant({ attribute: variant.attribute, attribute_value: value })
          }
        ]" :disabled="!hasVariantStock({ attribute: variant.attribute, attribute_value: value })"
        @click="selectVariant({ attribute: variant.attribute, attribute_value: value })">
        {{ value }}
      </button>
    </div>
  </div>
</template>
