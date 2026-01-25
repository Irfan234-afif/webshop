<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBillPaymentDetails, uploadBillPaymentProof } from '@/utils/billPaymentApi'
import { useAlertStore } from '@/stores/alert'
import BankTransferView from '@/views/Checkout/components/BankTransferView.vue'
import VirtualAccountView from '@/views/Checkout/components/VirtualAccountView.vue'
import type { BillPaymentDetails } from '@/utils/billPaymentApi'
import Container from '@/components/layout/Container.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const route = useRoute()
const router = useRouter()
const invoiceId = route.params.id as string
const alertStore = useAlertStore()

const loading = ref(true)
const error = ref<string | null>(null)
const paymentDetails = ref<BillPaymentDetails | null>(null)

onMounted(async () => {
    try {
        console.log('Fetching bill payment details for invoice:', invoiceId)
        paymentDetails.value = await getBillPaymentDetails(invoiceId)
        console.log('Bill payment details loaded:', paymentDetails.value)
    } catch (e: any) {
        console.error('Failed to load bill payment details:', e)
        error.value = e.message || 'Failed to load payment details'
    } finally {
        loading.value = false
    }
})

const handleUploadProof = async (fileUrl: string, notes?: string) => {
    try {
        console.log('Uploading payment proof:', { fileUrl, notes })

        // Use bill payment upload API for Sales Invoice
        const result = await uploadBillPaymentProof(invoiceId, fileUrl, notes)
        console.log('Payment proof uploaded:', result)

        alertStore.success('Bukti transfer berhasil diupload!', 'Berhasil')

        // Refresh payment details
        console.log('Refreshing payment details...')
        paymentDetails.value = await getBillPaymentDetails(invoiceId)
        console.log('Payment details refreshed')
    } catch (e: any) {
        console.error('Failed to upload payment proof:', e)
        alertStore.error(e.message || 'Gagal mengupload bukti transfer. Silakan coba lagi.', 'Gagal')
    }
}

const handleContinueShopping = () => {
    router.push('/')
}

const handleViewBills = () => {
    router.push('/bills')
}

// Adapt CheckoutPaymentDetails to BillPaymentDetails for component compatibility
const adaptedPaymentDetails = ref<any>(null)

// Watch for paymentDetails changes and adapt the structure
import { watch, computed } from 'vue'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

// Check if invoice is already paid
const isPaid = computed(() => {
    return paymentDetails.value?.sales_invoice?.outstanding_amount === 0 ||
        paymentDetails.value?.payment_request?.status === 'Paid'
})

watch(paymentDetails, (details) => {
    if (details) {
        adaptedPaymentDetails.value = {
            sales_order: {
                name: details.sales_invoice.name,
                customer: details.sales_invoice.customer,
                grand_total: details.sales_invoice.grand_total,
                delivery_date: null,
                student_name: details.sales_invoice.student_name,
                pickup_type: null,
                unit: null
            },
            payment_method: details.payment_method,
            bank_account_details: details.bank_account_details,
            payment_approval: details.payment_request,
            virtual_account: details.virtual_account
        }
    }
})
</script>

<template>
    <DefaultLayout>
        <Container class="bill-payment-page min-h-screen py-12">
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
                    <button @click="router.push('/bills')"
                        class="mt-4 px-6 py-2 bg-[#ac208e] text-white rounded-lg hover:bg-[#8c1a72]">
                        Back to Bills
                    </button>
                </div>
            </div>

            <!-- Main Content -->
            <template v-else-if="adaptedPaymentDetails">
                <!-- Payment Already Completed -->
                <div v-if="isPaid" class="max-w-2xl mx-auto">
                    <div class="bg-white rounded-2xl shadow-lg p-8 text-center">
                        <!-- Success Icon -->
                        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>

                        <!-- Success Message -->
                        <h2 class="text-2xl font-bold text-gray-900 mb-2">Pembayaran Berhasil!</h2>
                        <p class="text-gray-600 mb-6">Tagihan Anda telah dibayar dan diverifikasi</p>

                        <!-- Invoice Details -->
                        <div class="bg-gray-50 rounded-xl p-6 mb-6">
                            <div class="flex justify-between items-center mb-3">
                                <span class="text-sm text-gray-500">Nomor Invoice</span>
                                <span class="font-semibold text-gray-900">{{ paymentDetails?.sales_invoice?.name
                                }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-sm text-gray-500">Total Dibayar</span>
                                <span class="text-xl font-bold text-green-600">
                                    {{ new Intl.NumberFormat('id-ID', {
                                        style: 'currency', currency: 'IDR'
                                    }).format(paymentDetails?.sales_invoice?.grand_total || 0) }}
                                </span>
                            </div>
                        </div>

                        <!-- Actions -->
                        <div class="flex gap-4">
                            <PrimaryButton class="flex-1" variant="outline" @click="handleViewBills">Lihat Tagihan Lain
                            </PrimaryButton>
                            <PrimaryButton class="flex-1" @click="handleContinueShopping">Kembali ke Beranda
                            </PrimaryButton>
                            <!-- <button @click="handleViewBills"
                                class="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                                Lihat Tagihan Lain
                            </button>
                            <button @click="handleContinueShopping"
                                class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
                                Kembali ke Beranda
                            </button> -->
                        </div>
                    </div>
                </div>

                <!-- Bank Transfer View (if unpaid) -->
                <BankTransferView v-else-if="adaptedPaymentDetails.payment_method?.payment_type === 'Transfer Manual'"
                    :payment-details="adaptedPaymentDetails" @upload-proof="handleUploadProof"
                    @continue-shopping="handleContinueShopping" @view-order="handleViewBills" />

                <!-- Virtual Account View -->
                <VirtualAccountView
                    v-else-if="adaptedPaymentDetails.virtual_account && adaptedPaymentDetails.virtual_account.number"
                    :payment-details="adaptedPaymentDetails" @continue-shopping="handleContinueShopping"
                    @view-order="handleViewBills" />

                <!-- No Payment Method Selected Yet -->
                <div v-else class="flex items-center justify-center min-h-[400px]">
                    <div class="text-center">
                        <p class="text-gray-600 font-semibold">Payment method not selected</p>
                        <p class="text-gray-500 mt-2">Please return to bills page and select payment method</p>
                        <button @click="handleViewBills"
                            class="mt-4 px-6 py-2 bg-[#ac208e] text-white rounded-lg hover:bg-[#8c1a72]">
                            Back to Bills
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
