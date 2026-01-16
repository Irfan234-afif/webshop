<template>
  <div class="virtual-account-view max-w-2xl mx-auto">
    <!-- Success Header -->
    <div class="text-center mb-8">
      <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24"
          stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-bold text-gray-900">Pesanan Berhasil Dibuat!</h1>
      <p class="text-gray-600 mt-2">Silakan selesaikan pembayaran Anda sebelum batas waktu berakhir.</p>
    </div>

    <!-- VA Details Card -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
      <div class="p-6">
        <!-- Bank Info -->
        <div class="flex items-center justify-between mb-6 pb-6 border-b border-gray-100">
          <div>
            <p class="text-sm text-gray-500 mb-1">Metode Pembayaran</p>
            <h3 class="font-bold text-lg flex items-center gap-2">
              Virtual Account {{ paymentDetails.virtual_account?.bank }}
            </h3>
          </div>
          <!-- Placeholder for Bank Logo if available -->
          <!-- <img v-if="bankLogo" :src="bankLogo" class="h-8 object-contain" /> -->
        </div>

        <!-- VA Number -->
        <div class="mb-6">
          <p class="text-sm text-gray-500 mb-2">Nomor Virtual Account</p>
          <div class="flex items-center gap-3 bg-gray-50 p-4 rounded-lg border border-gray-200">
            <span class="text-2xl font-mono font-bold text-gray-900 tracking-wide">
              {{ paymentDetails.virtual_account?.number }}
            </span>
            <button @click="copyToClipboard(paymentDetails.virtual_account?.number || '')"
              class="ml-auto p-2 text-primary hover:bg-white rounded-md transition-colors" title="Salin Nomor VA">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Amount & Expiry -->
        <div class="grid grid-cols-2 gap-6">
          <div>
            <p class="text-sm text-gray-500 mb-1">Total Pembayaran</p>
            <p class="text-xl font-bold text-gray-900">
              {{ formatCurrency(paymentDetails.sales_order.grand_total) }}
            </p>
          </div>
          <div>
            <p class="text-sm text-gray-500 mb-1">Batas Waktu</p>
            <p class="text-sm font-medium text-red-600">
              {{ formatDate(paymentDetails.virtual_account?.expiry) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="bg-gray-50 px-6 py-4 flex gap-3">
        <button @click="$emit('view-order')"
          class="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 font-medium">
          Lihat Pesanan
        </button>
        <button @click="$emit('continue-shopping')"
          class="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark font-medium">
          Lanjut Belanja
        </button>
      </div>
    </div>

    <!-- Instructions -->
    <!-- <div v-html="paymentDetails.payment_method.additional_section"></div> -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 class="font-bold text-lg mb-4">Cara Pembayaran</h3>
      <div class="space-y-4">
        <details class="group">
          <summary class="flex justify-between items-center font-medium cursor-pointer list-none">
            <span>ATM {{ paymentDetails.virtual_account?.bank }}</span>
            <span class="transition group-open:rotate-180">
              <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor"
                stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24">
                <path d="M6 9l6 6 6-6"></path>
              </svg>
            </span>
          </summary>
          <div class="text-gray-600 mt-3 group-open:animate-fadeIn text-sm pl-4 border-l-2 border-gray-100">
            <ol class="list-decimal pl-4 space-y-2">
              <li>Masukkan kartu ATM dan PIN Anda using.</li>
              <li>Pilih menu Transaksi Lainnya > Transfer > Ke Rekening Virtual Account.</li>
              <li>Masukkan nomor Virtual Account: <span class="font-mono font-bold">{{
                paymentDetails.virtual_account?.number }}</span></li>
              <li>Pastikan detail pembayaran sudah benar.</li>
              <li>Ikuti instruksi selanjutnya untuk menyelesaikan pembayaran.</li>
            </ol>
          </div>
        </details>

        <details class="group">
          <summary class="flex justify-between items-center font-medium cursor-pointer list-none">
            <span>Mobile Banking</span>
            <span class="transition group-open:rotate-180">
              <svg fill="none" height="24" shape-rendering="geometricPrecision" stroke="currentColor"
                stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" viewBox="0 0 24 24" width="24">
                <path d="M6 9l6 6 6-6"></path>
              </svg>
            </span>
          </summary>
          <div class="text-gray-600 mt-3 group-open:animate-fadeIn text-sm pl-4 border-l-2 border-gray-100">
            <ol class="list-decimal pl-4 space-y-2">
              <li>Login ke aplikasi Mobile Banking Anda.</li>
              <li>Pilih menu m-Transfer > {{ paymentDetails.virtual_account?.bank }} Virtual Account.</li>
              <li>Masukkan nomor Virtual Account: <span class="font-mono font-bold">{{
                paymentDetails.virtual_account?.number }}</span></li>
              <li>Pastikan detail pembayaran sudah benar.</li>
            </ol>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CheckoutPaymentDetails } from '@/types/checkout'
import { useAlertStore } from '@/stores/alert'

const props = defineProps<{
  paymentDetails: CheckoutPaymentDetails
}>()

const emit = defineEmits(['continue-shopping', 'view-order'])
const alertStore = useAlertStore()

function formatCurrency(value: number) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(value)
}

function formatDate(dateString?: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('id-ID', {
    dateStyle: 'full',
    timeStyle: 'short'
  })
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    alertStore.success('Nomor Virtual Account berhasil disalin!', 'Disalin')
  } catch (err) {
    console.error('Failed to copy:', err)
    alertStore.error('Gagal menyalin nomor', 'Error')
  }
}
</script>

<style scoped>
details>summary {
  list-style: none;
}

details>summary::-webkit-details-marker {
  display: none;
}
</style>
