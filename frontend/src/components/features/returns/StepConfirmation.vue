<template>
  <div class="space-y-6">
    <!-- Order Information Section -->
    <div class="bg-white border border-gray-200 rounded-xl p-6">
      <h3 class="text-lg font-bold text-gray-900 mb-4">Informasi Pesanan</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="space-y-3">
          <div>
            <p class="text-sm text-gray-500">Nomor Pesanan</p>
            <p class="font-semibold text-gray-900">{{ orderSummary?.sales_order || '-' }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500">Tanggal</p>
            <p class="font-semibold text-gray-900">{{ formatDate(orderSummary?.transaction_date) }}</p>
          </div>
          <div v-if="orderSummary?.student_name">
            <p class="text-sm text-gray-500">Nama Siswa</p>
            <p class="font-semibold text-gray-900">{{ orderSummary.student_name }}</p>
          </div>
          <div v-if="orderSummary?.order_type">
            <p class="text-sm text-gray-500">Jenis Pengambilan</p>
            <p class="font-semibold text-gray-900">{{ orderSummary.order_type }}</p>
          </div>
        </div>
        <div class="space-y-3">
          <div>
            <p class="text-sm text-gray-500">Total Pesanan</p>
            <p class="font-bold text-primary text-xl">{{ formatIDR(orderSummary?.grand_total || 0) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Return Information Section -->
    <div class="bg-white border border-gray-200 rounded-xl p-6">
      <h3 class="text-lg font-bold text-gray-900 mb-4">Informasi Pengembalian</h3>
      <div class="space-y-4">
        <div>
          <p class="text-sm text-gray-500">Alasan Pengembalian</p>
          <p class="font-semibold text-gray-900">{{ getReturnReasonName(formData.return_reason) }}</p>
          <p v-if="formData.other_reason" class="text-sm text-gray-600 mt-1">
            {{ formData.other_reason }}
          </p>
        </div>

        <div v-if="formData.supporting_documents && formData.supporting_documents.length > 0">
          <p class="text-sm text-gray-500 mb-2">Bukti Pendukung ({{ formData.supporting_documents.length }} file)</p>
          <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
            <div 
              v-for="(fileUrl, index) in formData.supporting_documents"
              :key="index"
              class="aspect-square rounded-lg overflow-hidden bg-gray-100"
            >
              <img 
                v-if="isImageUrl(fileUrl)"
                :src="fileUrl"
                :alt="`Bukti ${index + 1}`"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <svg class="w-8 h-8 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div>
          <p class="text-sm text-gray-500">Metode Pengembalian dana</p>
          <p class="font-semibold text-gray-900">{{ getPaymentMethodName(formData.refund_payment_mode) }}</p>
        </div>

        <div v-if="isTransferManual">
          <div class="bg-gray-50 rounded-lg p-4 space-y-2">
            <div class="grid grid-cols-2 gap-2">
              <p class="text-sm text-gray-500">Bank</p>
              <p class="text-sm font-semibold text-gray-900">{{ formData.bank_name }}</p>
              
              <p class="text-sm text-gray-500">Nomor Rekening</p>
              <p class="text-sm font-semibold text-gray-900">{{ formData.account_number }}</p>
              
              <p class="text-sm text-gray-500">Nama Pemilik Rekening</p>
              <p class="text-sm font-semibold text-gray-900">{{ formData.account_holder_name }}</p>
            </div>
          </div>
        </div>

        <!-- <div>
          <p class="text-sm text-gray-500">Estimasi Waktu Refund Dana</p>
          <p class="font-semibold text-gray-900">Maks H+1 Setelah Barang Dikembalikan</p>
        </div> -->
      </div>
    </div>

    <!-- Important Notice -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-yellow-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
        </svg>
        <div class="text-sm text-yellow-800">
          <p class="font-medium mb-1">Perhatian:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li>Pastikan semua informasi yang Anda masukkan sudah benar</li>
            <li>Pengajuan pengembalian akan ditinjau oleh admin dalam 1-2 hari kerja</li>
            <li>Anda akan dihubungi untuk instruksi pengembalian barang setelah disetujui</li>
            <li>Dana akan dikembalikan setelah barang diterima dan diverifikasi</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Submission error -->
    <div v-if="submissionError" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
        </svg>
        <div>
          <p class="font-medium text-red-800">Gagal membuat pengajuan pengembalian</p>
          <p class="text-sm text-red-700 mt-1">{{ submissionError }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useReturnsStore } from '@/stores/returns'
import { formatIDR } from '@/utils/formatters'
import type { ReturnRequestFormData, EligibleOrder } from '@/types/returns'

interface Props {
  formData: ReturnRequestFormData
  orderSummary: EligibleOrder | null
}

const props = defineProps<Props>()

const returnsStore = useReturnsStore()
const submissionError = ref<string | null>(null)

const isTransferManual = computed(() => {
  const method = returnsStore.refundPaymentMethods.find(
    m => m.name === props.formData.refund_payment_mode
  )
  return method?.payment_type === 'Transfer Manual'
})

function getReturnReasonName(reasonId: string): string {
  const reason = returnsStore.returnReasons.find(r => r.name === reasonId)
  return reason?.reason_name || reasonId
}

function getPaymentMethodName(methodId: string): string {
  const method = returnsStore.refundPaymentMethods.find(m => m.name === methodId)
  return method?.title || methodId
}

function formatDate(dateString?: string): string {
  if (!dateString) return '-'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function isImageUrl(url: string): boolean {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
  const lowerUrl = url.toLowerCase()
  return imageExtensions.some(ext => lowerUrl.includes(ext))
}

function setSubmissionError(error: string | null) {
  submissionError.value = error
}

// Expose methods for parent component
defineExpose({
  setSubmissionError
})
</script>
