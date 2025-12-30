<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCheckoutPaymentDetails, uploadPaymentProof } from '@/utils/checkoutApi'
import { useAlertStore } from '@/stores/alert'
import BankTransferView from './components/BankTransferView.vue'
import VirtualAccountView from './components/VirtualAccountView.vue'
import PaymentSuccessView from './components/PaymentSuccessView.vue'
import type { CheckoutPaymentDetails } from '@/types/checkout'
import Container from '@/components/layout/Container.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const route = useRoute()
const router = useRouter()
const salesOrderId = route.params.id as string
const alertStore = useAlertStore()

const loading = ref(true)
const error = ref<string | null>(null)
const paymentDetails = ref<CheckoutPaymentDetails | null>(null)

onMounted(async () => {
  try {
    console.log('Fetching payment details for order:', salesOrderId)
    paymentDetails.value = await getCheckoutPaymentDetails(salesOrderId)
    console.log('Payment details loaded:', paymentDetails.value)
  } catch (e: any) {
    console.error('Failed to load payment details:', e)
    error.value = e.message || 'Failed to load payment details'
  } finally {
    loading.value = false
  }
})

const handleUploadProof = async (fileUrl: string, notes?: string) => {
  try {
    console.log('Uploading payment proof:', { fileUrl, notes })
    const result = await uploadPaymentProof(salesOrderId, fileUrl, notes)
    console.log('Payment proof uploaded:', result)

    // Show success message to user
    alertStore.success('Bukti transfer berhasil diupload!', 'Berhasil')

    // Refresh payment details to show the uploaded proof
    console.log('Refreshing payment details...')
    paymentDetails.value = await getCheckoutPaymentDetails(salesOrderId)
    console.log('Payment details refreshed')
  } catch (e: any) {
    console.error('Failed to upload payment proof:', e)
    alertStore.error(e.message || 'Gagal mengupload bukti transfer. Silakan coba lagi.', 'Gagal')
  }
}

const handleContinueShopping = () => {
  router.push('/')
}

const handleViewOrder = () => {
  router.push(`/orders`)
}
</script>

<template>
  <DefaultLayout>
    <Container class="checkout-payment-page min-h-screen py-12">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center min-h-[400px]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ac208e] mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading payment details...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex items-center justify-center min-h-[400px]">
        <div class="text-center">
          <p class="text-red-600 font-semibold">{{ error }}</p>
          <button @click="router.push('/')"
            class="mt-4 px-6 py-2 bg-[#ac208e] text-white rounded-lg hover:bg-[#8c1a72]">
            Back to Home
          </button>
        </div>
      </div>

      <!-- Main Content -->
      <template v-else-if="paymentDetails">
        <!-- Success View -->
        <PaymentSuccessView v-if="paymentDetails.payment_status === 'Paid'" :payment-details="paymentDetails"
          @continue-shopping="handleContinueShopping" @view-order="handleViewOrder" />

        <!-- Auto-detect payment type and show appropriate component -->
        <BankTransferView v-else-if="paymentDetails.payment_method.payment_type === 'Transfer Manual'"
          :payment-details="paymentDetails" @upload-proof="handleUploadProof"
          @continue-shopping="handleContinueShopping" @view-order="handleViewOrder" />
        <!-- Virtual Account View (Xendit) -->
        <VirtualAccountView v-else-if="paymentDetails.virtual_account && paymentDetails.virtual_account.number"
          :payment-details="paymentDetails" @continue-shopping="handleContinueShopping" @view-order="handleViewOrder" />

        <!-- Unsupported Payment Type -->
        <div v-else class="flex items-center justify-center min-h-[400px]">
          <div class="text-center">
            <p class="text-gray-600 font-semibold">Payment type not supported</p>
            <p class="text-gray-500 mt-2">{{ paymentDetails.payment_method.payment_type }}</p>
            <button @click="handleViewOrder"
              class="mt-4 px-6 py-2 bg-[#ac208e] text-white rounded-lg hover:bg-[#8c1a72]">
              View Order
            </button>
          </div>
        </div>
      </template>
    </Container>
  </DefaultLayout>
</template>

<style scoped>
/* Additional scoped styles if needed */
</style>
