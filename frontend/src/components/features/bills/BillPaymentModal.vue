<template>
    <Teleport to="body">
        <Transition name="modal">
            <div v-if="isOpen" class="modal-overlay" @click="handleClose">
                <div class="modal-container" @click.stop>
                    <!-- Header -->
                    <div class="modal-header">
                        <h2 class="text-xl font-bold text-gray-900">Pilih Metode Pembayaran</h2>
                        <button @click="handleClose" class="close-button">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <!-- Bill Summary -->
                    <div class="bill-summary">
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <p class="text-sm text-gray-500">Nomor Tagihan</p>
                                <p class="font-semibold text-gray-900">{{ bill.name }}</p>
                            </div>
                            <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                Belum Lunas
                            </span>
                        </div>
                        <div class="flex justify-between items-center mt-4">
                            <span class="text-sm text-gray-500">Total Tagihan</span>
                            <span class="text-2xl font-bold text-primary">{{ formatPrice(bill.outstanding_amount)
                                }}</span>
                        </div>
                        <div class="text-xs text-gray-400 mt-2">
                            Jatuh Tempo: {{ formatDate(bill.due_date) }}
                        </div>
                    </div>

                    <!-- Payment Method Selector -->
                    <div class="modal-body">
                        <PaymentMethodSelector ref="paymentSelector" />
                    </div>

                    <!-- Actions -->
                    <div class="modal-footer">
                        <PrimaryButton variant="outline" @click="handleClose" class="flex-1">
                            Batal
                        </PrimaryButton>
                        <PrimaryButton variant="primary" @click="handleConfirm" class="flex-1">
                            Bayar Sekarang
                        </PrimaryButton>
                        <!-- <button @click="handleClose" class="btn-secondary">
                            Batal
                        </button>
                        <button @click="handleConfirm" :disabled="!canProceed || isProcessing" class="btn-primary">
                            <span v-if="isProcessing" class="flex items-center gap-2">
                                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                    </path>
                                </svg>
                                Processing...
                            </span>
                            <span v-else>Bayar Sekarang</span>
                        </button> -->
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import PaymentMethodSelector from '@/views/Checkout/components/PaymentMethodSelector.vue'
import { initiateBillPayment } from '@/utils/billPaymentApi'
import { useCheckoutStore } from '@/stores/checkout'
import { useAlertStore } from '@/stores/alert'
import { formatIDR } from '@/utils/formatters'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

interface Props {
    isOpen: boolean
    bill: {
        name: string
        outstanding_amount: number
        due_date: string
        posting_date: string
    }
}

const props = defineProps<Props>()
const emit = defineEmits<{
    'close': []
    'payment-initiated': [invoiceName: string]
}>()

const router = useRouter()
const checkoutStore = useCheckoutStore()
const alertStore = useAlertStore()

const paymentSelector = ref<InstanceType<typeof PaymentMethodSelector> | null>(null)
const isProcessing = ref(false)

const canProceed = computed(() => {
    return checkoutStore.paymentMethodType !== ''
})

const formatPrice = (amount: number) => {
    return formatIDR(amount)
}

const formatDate = (dateStr: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

const handleClose = () => {
    if (!isProcessing.value) {
        emit('close')
    }
}

const handleConfirm = async () => {
    if (!canProceed.value || isProcessing.value) return

    try {
        isProcessing.value = true

        const paymentMethodType = checkoutStore.paymentMethodType
        const paymentChannel = checkoutStore.paymentChannel

        console.log('🔄 Initiating bill payment:', {
            invoice: props.bill.name,
            method: paymentMethodType,
            channel: paymentChannel
        })

        const response = await initiateBillPayment(
            props.bill.name,
            paymentMethodType,
            paymentChannel || undefined
        )

        console.log('✅ Payment initiated:', response)

        emit('payment-initiated', props.bill.name)

        // Redirect based on redirect_type
        if (response.payment_url) {
            if (response.redirect_type === 'gateway') {
                // External gateway redirect
                window.location.href = response.payment_url
            } else {
                // Internal page redirect (manual/virtual_account)
                router.push(response.payment_url)
            }
        } else {
            // Fallback to bill payment page
            router.push(`/bills/${props.bill.name}/payment`)
        }
    } catch (error: any) {
        console.error('❌ Failed to initiate payment:', error)
        alertStore.error(error.message || 'Gagal memproses pembayaran', 'Error')
    } finally {
        isProcessing.value = false
    }
}
</script>

<style scoped>
.modal-overlay {
    @apply fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4;
}

.modal-container {
    @apply bg-white rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-auto;
}

.modal-header {
    @apply flex items-center justify-between p-6 border-b border-gray-200 sticky top-0 bg-white z-10;
}

.close-button {
    @apply text-gray-400 hover:text-gray-600 transition-colors;
}

.bill-summary {
    @apply bg-gradient-to-br from-purple-50 to-pink-50 p-6 mx-6 mt-6 rounded-xl border border-purple-100;
}

.modal-body {
    @apply p-6;
}

.modal-footer {
    @apply flex gap-3 p-6 border-t border-gray-200 sticky bottom-0 bg-white;
}

.btn-secondary {
    @apply flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors;
}

.btn-primary {
    @apply flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}


.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
    transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
    transform: scale(0.9);
}
</style>
