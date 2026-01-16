<template>
  <div class="order-confirmation">
    <div class="space-y-6">
      <!-- Informasi Produk & Layanan -->
      <div class="section">
        <h3 class="section-title">Informasi Produk & Layanan</h3>
        <div class="section-content">
          <div v-for="item in items" :key="item.item_code" class="flex justify-between py-2">
            <span class="text-gray-700">{{ item.item_name }}</span>
            <span class="font-medium">{{ formatIDR(item.amount) }}</span>
          </div>

          <!-- Voucher -->
          <div class="flex justify-between py-2">
            <span class="text-gray-700">Voucher</span>
            <span class="font-medium">{{ voucherDiscount > 0 ? '-' + formatIDR(voucherDiscount) : '0' }}</span>
          </div>
        </div>
      </div>

      <!-- Metode Pembayaran -->
      <div class="section">
        <h3 class="section-title">Metode Pembayaran</h3>
        <div class="section-content">
          <div class="flex justify-between py-2">
            <span class="text-gray-700">Metode</span>
            <span class="font-medium">{{ paymentMethodType || '-' }}</span>
          </div>

          <!-- Service Charges -->
          <div v-for="(charge, index) in serviceCharges" :key="index" class="flex justify-between py-2">
            <span class="text-gray-700">{{ charge.description }}</span>
            <span class="font-medium">{{ formatIDR(charge.tax_amount || 0) }}</span>
          </div>
        </div>
      </div>

      <!-- Informasi Pengambilan -->
      <div class="section">
        <h3 class="section-title">Informasi Pengambilan</h3>
        <div class="section-content">
          <div class="flex justify-between py-2">
            <span class="text-gray-700">Jenis Pengambilan</span>
            <span class="font-medium">{{ pickupType || '-' }}</span>
          </div>
          <div v-if="deliveryDate" class="flex justify-between py-2">
            <span class="text-gray-700">Tanggal Pengiriman</span>
            <span class="font-medium">{{ formatDate(deliveryDate) }}</span>
          </div>
        </div>
      </div>

      <!-- Total Pembayaran Pesanan -->
      <div class="total-section">
        <div class="flex justify-between items-center">
          <span class="text-lg font-semibold">Total Pembayaran Pesanan</span>
          <span class="text-2xl font-bold text-primary">{{ formatIDR(total) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'

const checkoutStore = useCheckoutStore()
const {
  items,
  total,
  voucherDiscount,
  memberDiscount,
  pickupType,
  paymentMethodType,
  deliveryDate,
  serviceCharges
} = storeToRefs(checkoutStore)

function formatIDR(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}

function formatDate(dateString: string): string {
  if (!dateString) return '-'

  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('id-ID', {
      weekday: 'long',
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    }).format(date)
  } catch (e) {
    return dateString
  }
}
</script>

<style scoped>
.section {
  @apply bg-white border border-gray-200 rounded-lg overflow-hidden;
}

.section-title {
  @apply font-semibold text-lg px-6 py-4 bg-gray-50 border-b border-gray-200;
}

.section-content {
  @apply px-6 py-2;
}

.total-section {
  @apply bg-gray-50 border border-gray-200 rounded-lg p-6;
}
</style>
