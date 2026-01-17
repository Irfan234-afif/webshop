<template>
  <div class="order-confirmation">
    <div class="space-y-6">
      <!-- Informasi Produk & Layanan -->
      <div class="section">
        <h3 class="section-title">Informasi Produk & Layanan</h3>
        <div class="section-content">
          <div v-for="item in items" :key="item.item_code" class="flex justify-between py-2">
            <span class="font-semibold text-sm text-text-secondary">{{ item.item_name }} ({{ item.qty }}x)</span>
            <span class="font-semibold text-sm text-text-secondary">{{ formatIDR(item.price_list_rate * item.qty)
              }}</span>
          </div>

          <!-- Coupon Discount (only if applied) -->
          <div v-if="voucherDiscount > 0" class="flex justify-between py-2 text-red-600">
            <span class="font-semibold text-sm">Diskon Voucher</span>
            <span class="font-semibold text-sm">- {{ formatIDR(voucherDiscount) }}</span>
          </div>
        </div>
      </div>

      <!-- Metode Pembayaran -->
      <div class="section">
        <h3 class="section-title">Metode Pembayaran</h3>
        <div class="section-content">
          <div class="flex justify-between py-2">
            <span class="font-semibold text-sm text-text-secondary">Metode</span>
            <span class="font-semibold text-sm text-text-secondary">{{ paymentMethodType || '-' }}</span>
          </div>

          <!-- Service Charges -->
          <div v-for="(charge, index) in serviceCharges" :key="index" class="flex justify-between py-2">
            <span class="font-semibold text-sm text-text-secondary">{{ charge.description }}</span>
            <span class="font-semibold text-sm text-text-secondary">{{ formatIDR(charge.tax_amount || 0) }}</span>
          </div>
        </div>
      </div>

      <!-- Informasi Pengambilan -->
      <div class="section">
        <h3 class="section-title">Informasi Pengambilan</h3>
        <div class="section-content">
          <div class="flex justify-between py-2">
            <span class="font-semibold text-sm text-text-secondary">Jenis Pengambilan</span>
            <span class="font-semibold text-sm text-text-secondary">{{ pickupType || '-' }}</span>
          </div>
          <div v-if="deliveryDate" class="flex justify-between py-2">
            <span class="font-semibold text-sm text-text-secondary">Tanggal Pengiriman</span>
            <span class="font-semibold text-sm text-text-secondary">{{ formatDate(deliveryDate) }}</span>
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
  @apply flex flex-col bg-white border border-gray-200 rounded-lg overflow-hidden gap-4 py-4;
}

.section-title {
  @apply font-bold text-lg px-6;
}

.section-content {
  @apply px-6;
}

.total-section {
  @apply bg-gray-50 border border-gray-200 rounded-lg p-6;
}
</style>
