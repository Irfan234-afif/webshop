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
                                <p class="text-sm text-gray-500">
                                    {{ paymentType === 'voluntary_deposit' ? 'Setoran' : (isBulk ? `Kumulatif ${selectedRows.length} Bulan` : `Periode ${selectedRows[0].month_name}`) }}
                                </p>
                                <p class="font-semibold text-gray-900">{{ paymentType === 'voluntary_deposit' ? 'Simpanan Sukarela' : 'Simpanan Wajib' }}</p>
                            </div>
                            <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                                Menunggu Pembayaran
                            </span>
                        </div>
                        <div class="flex flex-col mt-4">
                            <template v-if="isBulk">
                                <ul class="text-sm text-gray-600 mb-3 space-y-1">
                                    <li v-for="row in selectedRows" :key="row.name" class="flex justify-between">
                                        <span>{{ row.month_name }}</span>
                                        <span>{{ formatPrice(row.amount) }}</span>
                                    </li>
                                </ul>
                                <div class="border-t border-purple-200 pt-2 flex justify-between items-center">
                                    <span class="text-sm font-semibold text-gray-700">Total Tagihan</span>
                                    <span class="text-xl font-bold text-primary">{{ formatPrice(totalAmount) }}</span>
                                </div>
                            </template>
                            <template v-else>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-500">Total Tagihan</span>
                                    <span class="text-2xl font-bold text-primary">{{ formatPrice(totalAmount) }}</span>
                                </div>
                            </template>
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
import { createSavingPayment, createVoluntarySavingPayment } from '@/utils/savingPaymentApi'
import { useCheckoutStore } from '@/stores/checkout'
import { useAlertStore } from '@/stores/alert'
import { formatIDR } from '@/utils/formatters'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

interface Props {
    isOpen: boolean
    savingName: string
    selectedRows: any[]
    paymentType?: 'mandatory' | 'voluntary_deposit'
}

const props = withDefaults(defineProps<Props>(), {
    paymentType: 'mandatory'
})
const emit = defineEmits<{
    'close': []
    'payment-initiated': [prName: string]
}>()

const router = useRouter()
const checkoutStore = useCheckoutStore()
const alertStore = useAlertStore()

const paymentSelector = ref<InstanceType<typeof PaymentMethodSelector> | null>(null)
const isProcessing = ref(false)

const isBulk = computed(() => props.selectedRows && props.selectedRows.length > 1)

const totalAmount = computed(() => {
    if (!props.selectedRows || props.selectedRows.length === 0) return 0
    return props.selectedRows.reduce((sum, row) => sum + row.amount, 0)
})

const canProceed = computed(() => {
    return checkoutStore.paymentMethodType !== ''
})

const formatPrice = (amount: number) => {
    return formatIDR(amount)
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

        const rowIds = props.selectedRows.map(row => row.name)

        console.log(`🔄 Initiating ${props.paymentType} payment:`, {
            savingName: props.savingName,
            rows: rowIds,
            method: paymentMethodType,
            channel: paymentChannel
        })

        let response: { payment_request: string };
        
        if (props.paymentType === 'voluntary_deposit') {
            const amount = props.selectedRows[0].amount;
            response = await createVoluntarySavingPayment(
                amount,
                paymentMethodType,
                paymentChannel || undefined
            )
        } else {
            response = await createSavingPayment(
                props.savingName,
                rowIds,
                paymentMethodType,
                paymentChannel || undefined
            )
        }

        console.log('✅ Payment initiated:', response)

        emit('payment-initiated', response.payment_request)

        router.push(`/savings/payment/${response.payment_request}`)
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
