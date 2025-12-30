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
                                <!-- Icon -->
                                <div
                                    class="w-[50px] h-[50px] bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor"
                                        viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                    </svg>
                                </div>

                                <!-- Info -->
                                <div class="flex-1 min-w-0">
                                    <h3 class="text-base font-bold text-gray-900 mb-2 capitalize">
                                        {{ subscription.type === 'request' ? 'Permintaan Langganan' : 'Langganan Aktif'
                                        }} #{{ subscription.name }}
                                    </h3>
                                    <p class="text-sm font-semibold text-text-secondary">
                                        {{ formatDate(subscription.creation || subscription.start_date) }}
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
                                        <p class="text-sm font-semibold text-text-secondary">Status</p>
                                        <div class="flex items-center gap-2">
                                            <div
                                                :class="['w-[11px] h-[11px] rounded-full', getStatusDotClass(subscription.status)]" />
                                            <p
                                                :class="['text-sm font-bold capitalize', getStatusTextClass(subscription.status)]">
                                                {{ statusLabel }}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Details Container -->
                                <div class="flex flex-col">
                                    <!-- Subscription Details -->
                                    <div class="bg-white border-[1.5px] border-gray-100 rounded-t-xl p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Detail Langganan
                                        </h4>
                                        <div class="space-y-4">
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Nomor {{ subscription.type === 'request' ? 'Permintaan' :
                                                    'Langganan' }}</span>
                                                <span class="text-right">#{{ subscription.name }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Tanggal Dibuat</span>
                                                <span class="text-right">{{ formatDate(subscription.creation ||
                                                    subscription.start_date) }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Paket Langganan</span>
                                                <span class="text-right">{{ subscription.plan_name || 'N/A' }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Tanggal Mulai</span>
                                                <span class="text-right">{{ formatDate(subscription.start_date)
                                                    }}</span>
                                            </div>
                                            <div v-if="subscription.end_date"
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Tanggal Berakhir</span>
                                                <span class="text-right">{{ formatDate(subscription.end_date) }}</span>
                                            </div>
                                            <div v-if="subscription.billing_interval"
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Periode Tagihan</span>
                                                <span class="text-right">Per {{ subscription.billing_interval }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Current Period (for active subscriptions) -->
                                    <div v-if="subscription.type === 'subscription' && subscription.current_invoice_end"
                                        class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-4 capitalize">Periode Saat Ini
                                        </h4>
                                        <div class="space-y-4">
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Dari</span>
                                                <span class="text-right">{{
                                                    formatDate(subscription.current_invoice_start ||
                                                        subscription.start_date) }}</span>
                                            </div>
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Sampai</span>
                                                <span class="text-right">{{ formatDate(subscription.current_invoice_end)
                                                    }}</span>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Item Information -->
                                    <div
                                        class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Informasi Produk
                                        </h4>
                                        <div class="flex gap-3">
                                            <div
                                                class="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 border border-gray-100 shrink-0 overflow-hidden">
                                                <img v-if="subscription.image" :src="subscription.image"
                                                    :alt="subscription.item_name" class="w-full h-full object-cover" />
                                                <svg v-else class="w-6 h-6" fill="none" stroke="currentColor"
                                                    viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round"
                                                        stroke-width="2"
                                                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                </svg>
                                            </div>
                                            <div class="flex-1 min-w-0">
                                                <p class="text-sm font-semibold text-gray-900">{{ subscription.item_name
                                                    || 'N/A' }}</p>
                                                <p class="text-xs text-gray-500">{{ subscription.plan_name }}</p>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Notes (for requests) -->
                                    <div v-if="subscription.type === 'request' && subscription.notes"
                                        class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-4 capitalize">Catatan</h4>
                                        <p class="text-sm text-text-secondary">{{ subscription.notes }}</p>
                                    </div>

                                    <!-- Billing Information -->
                                    <div
                                        class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 rounded-b-xl p-6">
                                        <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Informasi Biaya</h4>
                                        <div class="space-y-4">
                                            <div
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Biaya Langganan</span>
                                                <span class="text-right">{{ subscription.cost ?
                                                    formatIDR(subscription.cost) : 'N/A' }}</span>
                                            </div>
                                            <div v-if="subscription.billing_interval"
                                                class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                                                <span>Periode</span>
                                                <span class="text-right">Per {{ subscription.billing_interval }}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Footer Actions -->
                        <div
                            class="bg-white border-t-[1.5px] border-gray-100 rounded-b-xl p-8 flex items-center justify-between gap-4">
                            <button @click="emit('close')"
                                class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize">
                                Tutup
                            </button>
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
import type { SubscriptionItem } from '@/types/order'

interface Props {
    isOpen: boolean
    subscription: SubscriptionItem
}

const props = defineProps<Props>()

const emit = defineEmits<{
    close: []
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

// Get status label in Indonesian
const statusLabel = computed(() => {
    if (props.subscription.type === 'request') {
        const statusMap: Record<string, string> = {
            'Draft': 'Menunggu Persetujuan',
            'Submitted': 'Diajukan',
            'Active': 'Aktif',
            'Approved': 'Disetujui',
            'Cancelled': 'Dibatalkan'
        }
        return statusMap[props.subscription.status] || props.subscription.status
    } else {
        const statusMap: Record<string, string> = {
            'Active': 'Aktif',
            'Past Due Date': 'Jatuh Tempo',
            'Cancelled': 'Dibatalkan',
            'Unpaid': 'Belum Dibayar'
        }
        return statusMap[props.subscription.status] || props.subscription.status
    }
})

// Get status dot color class
const getStatusDotClass = (status: string) => {
    if (props.subscription.type === 'request') {
        switch (status) {
            case 'Active':
            case 'Approved':
                return 'bg-green-500'
            case 'Submitted':
                return 'bg-blue-500'
            case 'Draft':
                return 'bg-orange-500'
            case 'Cancelled':
                return 'bg-red-500'
            default:
                return 'bg-gray-500'
        }
    } else {
        switch (status) {
            case 'Active':
                return 'bg-green-500'
            case 'Past Due Date':
            case 'Unpaid':
                return 'bg-orange-500'
            case 'Cancelled':
                return 'bg-red-500'
            default:
                return 'bg-blue-500'
        }
    }
}

// Get status text color class
const getStatusTextClass = (status: string) => {
    if (props.subscription.type === 'request') {
        switch (status) {
            case 'Active':
            case 'Approved':
                return 'text-green-700'
            case 'Submitted':
                return 'text-blue-700'
            case 'Draft':
                return 'text-orange-700'
            case 'Cancelled':
                return 'text-red-700'
            default:
                return 'text-gray-700'
        }
    } else {
        switch (status) {
            case 'Active':
                return 'text-green-700'
            case 'Past Due Date':
            case 'Unpaid':
                return 'text-orange-700'
            case 'Cancelled':
                return 'text-red-700'
            default:
                return 'text-blue-700'
        }
    }
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
/* Fade transition for backdrop */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* Scale transition for modal */
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
