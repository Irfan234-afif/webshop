<script setup lang="ts">
import { computed } from 'vue'
import type { CartItem } from '@/types/cart'

interface Props {
  quotation_name: string
  item: CartItem
}

const props = defineProps<Props>()

const emit = defineEmits<{
  updateQuantity: [itemCode: string, quantity: number, quotationName: string]
  remove: [itemCode: string, quotationName: string]
}>()

const formattedPrice = computed(() => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(props.item.price)
})

const handleDecrement = () => {
  if (props.item.quantity > 1) {
    emit('updateQuantity', props.item.item_code, props.item.quantity - 1, props.quotation_name)
  }
}

const handleIncrement = () => {
  emit('updateQuantity', props.item.item_code, props.item.quantity + 1, props.quotation_name)
}

const handleRemove = () => {
  emit('remove', props.item.item_code, props.quotation_name)
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}
</script>

<template>
  <div class="flex gap-4 p-4 bg-white rounded-lg border border-gray-200">
    <!-- Product Image -->
    <div class="flex-shrink-0 w-20 h-20 bg-gray-100 rounded-lg overflow-hidden">
      <img
        v-if="item.image"
        :src="item.image"
        :alt="item.title"
        class="w-full h-full object-cover"
      />
      <div
        v-else
        class="w-full h-full flex items-center justify-center text-gray-400"
      >
        <svg
          class="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
      </div>
    </div>

    <!-- Product Details -->
    <div class="flex-1 flex justify-between gap-2">
      <div class="flex flex-col justify-between items-start gap-1">
        <div class="flex-1 flex flex-col gap-1">
          <h3 class="text-sm font-semibold text-gray-900 line-clamp-2">
            {{ item.title }}
          </h3>
          <!-- <p v-if="item.stockQuantity !== undefined" class="text-xs text-gray-500 mt-1">
            Stok: {{ item.stockQuantity }}
          </p> -->
          <p v-for="variant in item.variant_attributes" class="text-xs font-bold text-gray-500">
            {{ variant.attribute }}: {{ variant.value }}
          </p>
          <p v-if="item.isSubscription && item.service_start_date" class="text-xs text-purple-600 font-medium mt-1">
             Periode: {{ formatDate(item.service_start_date) }} - {{ formatDate(item.service_end_date) }}
          </p>
        </div>
        <div class="flex flex-col items-start mt-1">
          <p v-if="item.net_price && item.net_price < item.price" class="text-xs text-gray-500 line-through color-red-500">
            {{ formattedPrice }}
          </p>
          <p class="text-base font-bold text-primary">
            {{ formatCurrency(item.net_price || item.price) }}
          </p>
        </div>
      </div>

      <!-- Price and Quantity Controls -->
      <div class="flex flex-col justify-between items-end">
        <!-- Delete Button -->
        <button
          @click="handleRemove"
          class="ml-2 p-1 text-gray-400 hover:text-red-500 transition-colors"
          aria-label="Remove item"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>

        <!-- Quantity Controls -->
        <div class="flex items-center gap-2">
          <button
            @click="handleDecrement"
            :disabled="item.quantity <= 1"
            class="w-8 h-8 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-label="Decrease quantity"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
            </svg>
          </button>

          <span class="w-8 text-center font-semibold text-sm">
            {{ item.quantity }}
          </span>

          <button
            @click="handleIncrement"
            class="w-8 h-8 flex items-center justify-center rounded-full border border-primary text-primary hover:bg-primary hover:text-white transition-colors"
            aria-label="Increase quantity"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
