<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAlertStore } from '@/stores/alert'
import type { CheckoutPaymentDetails } from '@/types/checkout'
import PaymentProofUploadModal from '@/components/PaymentProofUploadModal.vue'

interface Props {
  paymentDetails: CheckoutPaymentDetails
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'upload-proof': [fileUrl: string, notes?: string]
  'continue-shopping': []
  'view-order': []
}>()

const bankDetails = computed(() => props.paymentDetails.bank_account_details)
const paymentApproval = computed(() => props.paymentDetails.payment_approval)
const hasUploadedProof = computed(() => paymentApproval.value?.payment_proof)
const showPaymentDeadline = ref(false) // Hidden for now per requirements
const showHowToPay = ref(false) // Hidden for now per requirements
const isUploadModalOpen = ref(false)
const alertStore = useAlertStore()

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    alertStore.success('Copied to clipboard!', 'Success')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const handleUploadClick = () => {
  isUploadModalOpen.value = true
}

const handleUploadSuccess = (fileUrl: string, notes?: string) => {
  // Close modal
  isUploadModalOpen.value = false

  // Emit to parent
  emit('upload-proof', fileUrl, notes)
}

const handleModalClose = () => {
  isUploadModalOpen.value = false
}

const formatPickupType = (type: string | null) => {
  if (!type) return '-'
  return type === 'Ambil di koperasi' ? 'Ambil di Koperasi' : 'Ambil secara online'
}

const formatDateTime = (dateString: string | null) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

const isImageFile = (fileUrl: string | null | undefined) => {
  if (!fileUrl) return false
  const lowerUrl = fileUrl.toLowerCase()
  return lowerUrl.endsWith('.jpg') || lowerUrl.endsWith('.jpeg') || lowerUrl.endsWith('.png')
}

const getApprovalStatusStyle = (status: string) => {
  switch (status) {
    case 'Approved':
      return {
        bg: 'bg-green-100',
        text: 'text-green-800',
        label: 'Disetujui'
      }
    case 'Rejected':
      return {
        bg: 'bg-red-100',
        text: 'text-red-800',
        label: 'Ditolak'
      }
    default: // Pending
      return {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        label: 'Menunggu Persetujuan'
      }
  }
}
</script>

<template>
  <div class="bank-transfer-view max-w-3xl mx-auto px-4">
    <!-- Main Payment Card -->
    <div class="bg-white border border-gray-200 rounded-2xl p-8 md:p-12 shadow-sm">

      <!-- Header Section -->
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-4">
          Pembayaran Transfer Manual
        </h1>
        <p class="text-sm text-gray-500 leading-relaxed">
          Selesaikan pembayaran Anda melalui transfer bank agar pesanan dapat diproses. Setelah melakukan transfer, harap upload bukti pembayaran untuk selanjutnya diverifikasi.
        </p>
      </div>

      <!-- Bank Account Info Box -->
      <div v-if="bankDetails" class="bg-gray-50 border border-gray-200 rounded-xl p-6 flex items-center gap-4 mb-4">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-[#ac208e] rounded-full flex items-center justify-center">
            <!-- Receipt Icon -->
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-gray-500 mb-1">
            Rekening {{ bankDetails.bank_name }} an <strong>{{ bankDetails.account_holder }}</strong>
          </p>
          <p class="text-lg font-bold text-[#ac208e]">
            {{ bankDetails.account_number }}
          </p>
        </div>
        <button @click="copyToClipboard(bankDetails.account_number)"
          class="flex-shrink-0 p-2 hover:bg-gray-200 rounded-lg transition-colors" title="Copy account number">
          <!-- Copy Icon -->
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
      </div>

      <!-- Total Transfer Box -->
      <div class="bg-gray-50 border border-gray-200 rounded-xl p-6 flex items-center gap-4 mb-6">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-[#ac208e] rounded-full flex items-center justify-center">
            <!-- Dollar Sign Icon -->
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm text-gray-500 mb-1">
            Total Transfer
          </p>
          <p class="text-lg font-bold text-[#ac208e]">
            {{ formatCurrency(paymentDetails.sales_order.grand_total) }}
          </p>
        </div>
        <button @click="copyToClipboard(paymentDetails.sales_order.grand_total.toString())"
          class="flex-shrink-0 p-2 hover:bg-gray-200 rounded-lg transition-colors" title="Copy amount">
          <!-- Copy Icon -->
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
      </div>

      <!-- Upload Button -->
      <button @click="handleUploadClick"
        class="w-full bg-[#ac208e] text-white font-bold py-3 px-8 rounded-xl hover:bg-[#8c1a72] transition-colors mb-6">
        {{ hasUploadedProof ? 'Upload Ulang Bukti Transfer' : 'Upload Bukti Transfer' }}
      </button>

      <!-- Payment Approved - Prominent Success Card -->
      <div v-if="paymentApproval?.status === 'Approved'"
        class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-8 mb-6 shadow-lg">
        <!-- Success Header with Large Icon -->
        <div class="flex flex-col items-center text-center mb-6">
          <div class="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mb-4 shadow-lg">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-green-900 mb-2">
            Pembayaran Dikonfirmasi!
          </h3>
          <p class="text-green-700 text-base">
            Bukti transfer Anda telah diverifikasi dan disetujui oleh admin
          </p>
        </div>

        <!-- Payment Confirmation Details -->
        <div class="bg-white rounded-xl p-6 mb-4 border border-green-100">
          <h4 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Detail Konfirmasi Pembayaran
          </h4>
          <div class="space-y-3">
            <div class="flex justify-between items-center py-2 border-b border-gray-100">
              <span class="text-sm text-gray-600">Status Pembayaran</span>
              <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                Lunas
              </span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-gray-100">
              <span class="text-sm text-gray-600">Jumlah Dibayar</span>
              <span class="text-sm font-bold text-green-700">{{ formatCurrency(paymentDetails.sales_order.grand_total)
                }}</span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-gray-100">
              <span class="text-sm text-gray-600">Metode Pembayaran</span>
              <span class="text-sm font-medium text-gray-900">Transfer Bank - {{ bankDetails?.bank_name }}</span>
            </div>
            <div class="flex justify-between items-center py-2">
              <span class="text-sm text-gray-600">Nomor Pesanan</span>
              <span class="text-sm font-medium text-gray-900">{{ paymentDetails.sales_order.name }}</span>
            </div>
          </div>
        </div>

        <!-- Order Processing Status -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-start gap-3">
          <div class="flex-shrink-0 w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div class="flex-1">
            <p class="text-sm font-semibold text-blue-900 mb-1">Pesanan Sedang Diproses</p>
            <p class="text-sm text-blue-700">
              Pesanan Anda akan segera diproses oleh tim kami. Anda dapat melihat status pesanan di halaman riwayat
              pembelian.
            </p>
          </div>
        </div>

        <!-- Admin Remarks (if any) -->
        <div v-if="paymentApproval?.remarks" class="mt-4 bg-white border border-green-100 rounded-lg p-4">
          <p class="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
            Catatan:
          </p>
          <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ paymentApproval.remarks }}</p>
        </div>

        <!-- Uploaded Proof Preview (Collapsed) -->
        <details v-if="hasUploadedProof" class="mt-4 bg-white border border-green-100 rounded-lg">
          <summary
            class="cursor-pointer p-4 font-medium text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
            Lihat Bukti Transfer yang Diupload
          </summary>
          <div class="p-4 pt-0">
            <div v-if="isImageFile(paymentApproval?.payment_proof)"
              class="rounded-lg overflow-hidden border border-gray-200 mt-2">
              <img :src="paymentApproval?.payment_proof || ''" alt="Bukti Transfer"
                class="w-full h-auto max-h-96 object-contain bg-gray-50" />
            </div>
            <a v-else :href="paymentApproval?.payment_proof || ''" target="_blank"
              class="flex items-center gap-3 p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors mt-2">
              <div class="flex-shrink-0 w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-medium text-gray-900">Bukti Transfer (PDF)</p>
                <p class="text-xs text-gray-500">Klik untuk membuka file</p>
              </div>
              <svg class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </details>
      </div>

      <!-- Pending/Rejected Status - Standard Card -->
      <div v-else-if="hasUploadedProof" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-gray-900">
            Bukti Transfer yang Diupload
          </h3>
          <span class="px-3 py-1 rounded-full text-xs font-semibold" :class="[
            getApprovalStatusStyle(paymentApproval?.status || 'Pending').bg,
            getApprovalStatusStyle(paymentApproval?.status || 'Pending').text
          ]">
            {{ getApprovalStatusStyle(paymentApproval?.status || 'Pending').label }}
          </span>
        </div>

        <!-- Image Preview or PDF Link -->
        <div class="mb-4">
          <div v-if="isImageFile(paymentApproval?.payment_proof)"
            class="rounded-lg overflow-hidden border border-gray-200">
            <img :src="paymentApproval?.payment_proof || ''" alt="Bukti Transfer"
              class="w-full h-auto max-h-96 object-contain bg-gray-50" />
          </div>
          <a v-else :href="paymentApproval?.payment_proof || ''" target="_blank"
            class="flex items-center gap-3 p-4 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">
            <div class="flex-shrink-0 w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900">Bukti Transfer (PDF)</p>
              <p class="text-xs text-gray-500">Klik untuk membuka file</p>
            </div>
            <svg class="w-5 h-5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>

        <!-- Notes Section -->
        <div v-if="paymentApproval?.remarks" class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
          <p class="text-xs font-semibold text-gray-700 mb-2">Catatan:</p>
          <p class="text-sm text-gray-600 whitespace-pre-wrap">{{ paymentApproval.remarks }}</p>
        </div>

        <!-- Status Message -->
        <div v-if="paymentApproval?.status === 'Pending'"
          class="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <svg class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-yellow-800">
            Bukti transfer Anda sedang dalam proses verifikasi oleh admin. Anda akan mendapatkan notifikasi setelah
            disetujui.
          </p>
        </div>

        <div v-else-if="paymentApproval?.status === 'Rejected'"
          class="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <svg class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm text-red-800">
            Bukti transfer Anda ditolak. Silakan upload ulang bukti transfer yang valid.
          </p>
        </div>
      </div>

      <!-- Order Details Section -->
      <div class="bg-white border border-gray-200 rounded-t-xl p-6 mb-0">
        <h3 class="text-sm font-bold text-gray-900 mb-6">
          Detail Pesanan
        </h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Nomor Pesanan</span>
            <span class="text-gray-500 text-right">{{ paymentDetails.sales_order.name }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Nama Siswa</span>
            <span class="text-gray-500 text-right">{{ paymentDetails.sales_order.student_name || '-' }}</span>
          </div>
          <div v-if="paymentDetails.sales_order.unit" class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Unit</span>
            <span class="text-gray-500 text-right">{{ paymentDetails.sales_order.unit || '-' }}</span>
          </div>
          <div v-if="paymentDetails.sales_order.pickup_type" class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Jenis Pengambilan</span>
            <span class="text-gray-500 text-right">{{ formatPickupType(paymentDetails.sales_order.pickup_type) }}</span>
          </div>
          <div v-if="paymentDetails.sales_order.delivery_date" class="flex items-center justify-between text-sm">
            <span class="text-gray-500">Jadwal Pengambilan</span>
            <span class="text-gray-500 text-right">{{ formatDateTime(paymentDetails.sales_order.delivery_date) }}</span>
          </div>
        </div>
      </div>

      <!-- Payment Deadline Section (HIDDEN but structure preserved) -->
      <div v-if="showPaymentDeadline" class="bg-white border border-t-0 border-gray-200 rounded-b-xl p-6 mb-6">
        <h3 class="text-sm font-bold text-gray-900 mb-4">
          Batas Waktu Pembayaran
        </h3>
        <p class="text-sm text-gray-500">
          15 Desember 2025, 23:59 WIB
        </p>
      </div>

      <!-- Add bottom border to order details when deadline is hidden -->
      <div v-if="!showPaymentDeadline" class="border-b border-gray-200 rounded-b-xl mb-6"></div>

      <!-- How to Pay Expandable (HIDDEN but structure preserved) -->
      <div v-if="showHowToPay" class="bg-white border border-gray-200 rounded-xl p-6 mb-6">
        <button class="flex items-center justify-between w-full text-left">
          <span class="text-sm text-gray-500">Lihat cara bayar</span>
          <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      <!-- Bottom Action Buttons -->
      <div class="flex flex-col sm:flex-row gap-4">
        <button @click="$emit('continue-shopping')"
          class="flex-1 bg-white border-2 border-[#ac208e] text-[#ac208e] font-bold py-3 px-8 rounded-lg hover:bg-gray-50 transition-colors">
          Lanjut Belanja
        </button>
        <button @click="$emit('view-order')"
          class="flex-1 bg-[#ac208e] text-white font-bold py-3 px-8 rounded-lg hover:bg-[#8c1a72] transition-colors">
          Lihat Pesanan
        </button>
      </div>
    </div>

    <!-- Payment Proof Upload Modal -->
    <PaymentProofUploadModal :is-open="isUploadModalOpen" :sales-order-id="paymentDetails.sales_order.name"
      @close="handleModalClose" @success="handleUploadSuccess" />
  </div>
</template>

<style scoped>
/* Additional custom styles if needed */
</style>
