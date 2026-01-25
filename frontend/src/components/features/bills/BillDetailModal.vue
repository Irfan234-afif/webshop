<template>
    <Teleport to="body">
        <!-- Backdrop -->
        <Transition name="fade">
            <div v-if="isOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
                @click="emit('close')">
                <!-- Modal Content -->
                <Transition name="scale">
                    <div v-if="isOpen"
                        class="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col"
                        @click.stop role="dialog" aria-modal="true">
                        <!-- Header -->
                        <div class="bg-white rounded-t-xl p-8 border-b border-gray-100">
                            <div class="flex items-start gap-6">
                                <!-- Receipt Icon -->
                                <div
                                    class="w-[50px] h-[50px] bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                                    <ReceiptIcon :size="25" color="#FFFFFF" />
                                </div>

                                <!-- Invoice Info -->
                                <div class="flex-1 min-w-0">
                                    <h3 class="text-base font-bold text-gray-900 mb-2 capitalize">
                                        Invoice #{{ bill.name }}
                                    </h3>
                                    <p class="text-sm font-semibold text-text-secondary">
                                        {{ formatDate(bill.posting_date) }}
                                    </p>
                                </div>

                                <!-- Close Button -->
                                <button @click="emit('close')"
                                    class="flex-shrink-0 w-[18px] h-[18px] text-text-secondary hover:text-gray-600 transition-colors"
                                    aria-label="Close">
                                    <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg"
                                        class="rotate-45">
                                        <path d="M9 0L9 18M0 9L18 9" stroke="currentColor" stroke-width="2"
                                            stroke-linecap="round" />
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <!-- Content (Scrollable) -->
                        <div class="flex-1 overflow-y-auto px-8 pb-8 py-4">
                            <!-- Status Section -->
                            <div class="flex flex-col gap-4 mt-0 mb-4">
                                <div class="bg-gray-50/80 border-[1.5px] border-gray-100 rounded-xl p-6 gap-4">
                                    <!-- Status Badge -->
                                    <div class="flex items-center justify-between">
                                        <p class="text-sm font-semibold text-text-secondary">Status Pembayaran</p>
                                        <div class="flex items-center gap-2">
                                            <div :class="['w-[11px] h-[11px] rounded-full', statusDotClass]" />
                                            <p :class="['text-sm font-bold capitalize', statusTextClass]">
                                                {{ statusLabel }}
                                            </p>
                                        </div>
                                    </div>

                                    <!-- Payment Info for Unpaid -->
                                    <div v-if="!isPaid" class="bg-white rounded-lg p-4 flex items-start gap-3 mt-4">
                                        <InfoCircleIcon :size="16" color="#FFBC4F" class="flex-shrink-0 mt-0.5" />
                                        <div class="flex-1">
                                            <p class="text-sm font-semibold text-text-secondary">
                                                Jatuh Tempo: {{ formatDate(bill.due_date) }}
                                            </p>
                                            <p v-if="isOverdue" class="text-xs font-medium text-red-600 mt-1">
                                                Tagihan sudah melewati jatuh tempo
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Invoice Details Container -->
                                <div class="flex flex-col">
                                    <!-- Detail Invoice -->
                                    <div class="bg-white border-[1.5px] border-gray-100 rounded-t-xl p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Detail Invoice</h4>
                                        <div class="space-y-4">
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Nomor Invoice</span>
                                                <span class="text-right">#{{ bill.name }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Tanggal Terbit</span>
                                                <span class="text-right">{{ formatDate(bill.posting_date) }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Jatuh Tempo</span>
                                                <span class="text-right">{{ formatDate(bill.due_date) }}</span>
                                            </div>
                                            <div v-if="bill.subscription"
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Langganan</span>
                                                <span class="text-right">{{ bill.subscription }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Status</span>
                                                <span class="text-right">{{ bill.status }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Rincian Tagihan -->
                                    <div
                                        class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 rounded-b-xl p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Rincian Tagihan</h4>
                                        <div class="space-y-4">
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Subtotal</span>
                                                <span class="text-right">{{ formatIDR(bill.grand_total) }}</span>
                                            </div>

                                            <div v-if="isPaid"
                                                class="flex items-center justify-between text-sm font-semibold text-green-600">
                                                <span>Terbayar</span>
                                                <span class="text-right">{{ formatIDR(bill.grand_total) }}</span>
                                            </div>

                                            <div v-if="!isPaid"
                                                class="flex items-center justify-between text-sm font-semibold text-red-600">
                                                <span>Sisa Tagihan</span>
                                                <span class="text-right">{{ formatIDR(bill.outstanding_amount) }}</span>
                                            </div>

                                            <div class="h-px bg-gray-200 my-2"></div>

                                            <div
                                                class="flex items-center justify-between text-base font-bold text-gray-900">
                                                <span>Total {{ isPaid ? 'Dibayar' : 'Tagihan' }}</span>
                                                <span class="text-right">{{ formatIDR(isPaid ? bill.grand_total :
                                                    bill.outstanding_amount) }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Footer Actions -->
                        <div class="bg-white border-t-[1.5px] border-gray-100 rounded-b-xl p-8 flex flex-col gap-4">
                            <!-- Primary action buttons -->
                            <div class="flex items-center gap-4">
                                <button v-if="!isPaid" @click="handlePayBill"
                                    class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize">
                                    {{ bill.has_payment_request ? 'Lanjutkan Pembayaran' : 'Bayar Sekarang' }} - {{
                                    formatIDR(bill.outstanding_amount) }}
                                </button>
                                <button v-else @click="emit('close')"
                                    class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize">
                                    Tutup
                                </button>
                            </div>
                        </div>
                    </div>
                </Transition>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { formatIDR } from '@/utils/formatters'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'
import InfoCircleIcon from '@/components/icons/InfoCircleIcon.vue'

interface Props {
    isOpen: boolean
    bill: any
    isPaid?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
    close: []
    pay: [bill: any]
}>()

// Format date to readable format
const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

// Check if bill is overdue
const isOverdue = computed(() => {
    if (props.isPaid || !props.bill?.due_date) return false
    const dueDate = new Date(props.bill.due_date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return dueDate < today
})

// Status Badge Logic
const statusLabel = computed(() => {
    if (props.isPaid) {
        return 'Lunas'
    }
    if (isOverdue.value) {
        return 'Jatuh Tempo Terlewat'
    }
    return 'Belum Lunas'
})

const statusDotClass = computed(() => {
    if (props.isPaid) {
        return 'bg-[#007f62]' // Green
    }
    if (isOverdue.value) {
        return 'bg-red-600'
    }
    return 'bg-[#faad14]' // Orange
})

const statusTextClass = computed(() => {
    if (props.isPaid) {
        return 'text-[#007f62]' // Green
    }
    if (isOverdue.value) {
        return 'text-red-600'
    }
    return 'text-[#faad14]' // Orange
})

// Handle pay bill
const handlePayBill = () => {
    emit('pay', props.bill)
    emit('close')
}

// Prevent body scroll when modal is open
watch(
    () => props.isOpen,
    (isOpen) => {
        if (isOpen) {
            document.body.style.overflow = 'hidden'
        } else {
            document.body.style.overflow = ''
        }
    }
)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
    transition: all 0.3s ease;
}

.scale-enter-from,
.scale-leave-to {
    opacity: 0;
    transform: scale(0.95);
}
</style>
