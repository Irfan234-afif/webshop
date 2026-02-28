<template>
  <DefaultLayout>
    <div class="min-h-screen bg-gray-50 py-12">
      <Container>
        <div class="max-w-3xl mx-auto">
          <!-- Back Link -->
          <router-link to="/saving" class="inline-flex items-center text-gray-500 hover:text-gray-700 mb-6 transition-colors">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Kembali ke Simpanan
          </router-link>

          <!-- Loading State -->
          <div v-if="isLoading" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p class="text-gray-500">Memuat detail pembayaran...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-white rounded-2xl shadow-sm border border-red-100 overflow-hidden text-center py-12 px-6">
            <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 class="text-2xl text-gray-900 font-bold mb-2">Gagal Memuat Pembayaran</h2>
            <p class="text-gray-600 mb-6">{{ error }}</p>
            <button @click="fetchPaymentDetails" class="bg-primary text-white font-bold py-2.5 px-6 rounded-lg hover:bg-opacity-90">
              Coba Lagi
            </button>
          </div>

          <!-- Payment Content -->
          <div v-else-if="paymentDetails" class="space-y-6">
            <div class="flex items-center gap-3 mb-6 pl-2">
              <div class="w-12 h-12 rounded-full bg-primary flex items-center justify-center shadow-lg shadow-purple-200">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Pembayaran Simpanan Wajib</h1>
                <p class="text-gray-500">Selesaikan pembayaran simpanan wajib Anda</p>
              </div>
            </div>

            <div v-if="isPaid" class="bg-white rounded-2xl shadow-lg p-8 text-center border border-gray-100 relative overflow-hidden">
                <div class="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-green-50 rounded-full blur-xl"></div>
                <!-- Success Icon -->
                <div class="relative w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 transform transition-transform hover:scale-105">
                    <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path>
                    </svg>
                </div>

                <!-- Success Message -->
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Pembayaran Berhasil!</h2>
                <p class="text-gray-600 mb-6">Tagihan Simpanan Wajib Anda telah dibayar dan diverifikasi.</p>

                <!-- Actions -->
                <div class="flex gap-4">
                    <button @click="router.push('/savings')"
                        class="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                        Kembali ke Simpanan
                    </button>
                    <button @click="router.push('/')"
                        class="flex-1 px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-opacity-90 transition-colors">
                        Kembali ke Beranda
                    </button>
                </div>
            </div>

            <!-- Virtual Account View -->
            <VirtualAccountView 
              v-else-if="isVirtualAccount" 
              :payment-details="paymentDetails"
              @continue-shopping="router.push('/')"
              @view-order="router.push('/savings')"
            />

            <!-- Manual Bank Transfer View -->
            <BankTransferView 
              v-else-if="isManualTransfer" 
              :payment-details="paymentDetails"
              @upload-proof="isUploadModalOpen = true"
              @continue-shopping="router.push('/')"
              @view-order="router.push('/savings')"
            />

            <!-- Unknown Method Warning -->
            <div v-else class="bg-amber-50 rounded-2xl border border-amber-200 p-8 text-center">
              <p class="text-amber-800 font-medium">Metode pembayaran tidak dikenali atau belum diselesaikan pengaturannya.</p>
            </div>
          </div>
        </div>
      </Container>
    </div>

    <!-- Upload Proof Modal -->
    <PaymentProofUploadModal
      v-if="paymentDetails"
      :is-open="isUploadModalOpen"
      :sales-order-id="paymentDetails.sales_order.name"
      @close="isUploadModalOpen = false"
      @success="handleUploadSuccess"
    />
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getSavingPaymentDetails, uploadSavingPaymentProof } from '@/utils/savingPaymentApi'
import { extractErrorMessage } from '@/utils/errorHandler'
import { useAlertStore } from '@/stores/alert'
import type { CheckoutPaymentDetails } from '@/types/checkout'

import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import VirtualAccountView from '@/views/Checkout/components/VirtualAccountView.vue'
import BankTransferView from '@/views/Checkout/components/BankTransferView.vue'
import PaymentProofUploadModal from '@/components/PaymentProofUploadModal.vue'

const router = useRouter()
const route = useRoute()
const alertStore = useAlertStore()

const paymentRequestId = route.params.id as string

const isLoading = ref(true)
const error = ref<string | null>(null)
const paymentDetails = ref<CheckoutPaymentDetails | null>(null)
const isUploadModalOpen = ref(false)

const isPaid = computed(() => {
  return paymentDetails.value?.payment_approval?.status === 'Approved'
})

const isVirtualAccount = computed(() => {
  return paymentDetails.value?.payment_method?.payment_type === 'Payment Gateway'
})

const isManualTransfer = computed(() => {
  return paymentDetails.value?.payment_method?.payment_type === 'Transfer Manual' ||
         paymentDetails.value?.payment_method?.payment_type === 'Transfer Bank'
})

const fetchPaymentDetails = async () => {
  isLoading.value = true
  error.value = null

  try {
    if (!paymentRequestId) {
      throw new Error("ID Pembayaran tidak ditemukan.")
    }

    // Wrap the API fetching the mock CheckPaymentDetails format
    paymentDetails.value = await getSavingPaymentDetails(paymentRequestId)

  } catch (err: any) {
    console.error('Failed to fetch payment details:', err)
    error.value = extractErrorMessage(err) || 'Terjadi kesalahan saat memuat detail pembayaran.'
  } finally {
    isLoading.value = false
  }
}

const handleUploadSuccess = async (fileUrl: string, notes?: string) => {
  isUploadModalOpen.value = false
  
  try {
    await uploadSavingPaymentProof(paymentRequestId, fileUrl, notes)
    alertStore.success('Bukti pembayaran berhasil disimpan.', 'Berhasil')
    
    // Refresh the details to get the updated status
    await fetchPaymentDetails()
  } catch (err: any) {
    console.error('Failed to update payment proof:', err)
    alertStore.error(extractErrorMessage(err) || 'Gagal menyimpan bukti pembayaran')
  }
}

onMounted(() => {
  if (paymentRequestId) {
    fetchPaymentDetails()
  } else {
    error.value = "ID Pembayaran tidak ditemukan."
    isLoading.value = false
  }
})
</script>
