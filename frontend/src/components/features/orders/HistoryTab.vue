<template>
  <div>
    <!-- Orders Grid -->
    <div v-if="orders.length > 0" class="min-h-[200px] mb-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        <OrderCard
          v-for="order in orders"
          :key="order.name"
          :order="order"
          :is-history="true"
          @view="onViewOrder"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading" class="text-center py-12">
      <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-6">
        <ReceiptIcon class="w-12 h-12 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">Belum ada riwayat pesanan</h3>
      <p class="text-gray-500 mb-6">Pesanan yang sudah selesai akan muncul di sini</p>
      <RouterLink
        to="/products"
        class="inline-block bg-primary hover:bg-primary-dark text-white font-semibold py-3 px-6 rounded-lg transition-colors"
      >
        Mulai Belanja
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Order } from '@/types/order'
import OrderCard from './OrderCard.vue'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'

defineProps<{
  orders: Order[]
  loading: boolean
}>()

const emit = defineEmits(['view-order'])

const onViewOrder = (order: Order) => {
  emit('view-order', order)
}
</script>
