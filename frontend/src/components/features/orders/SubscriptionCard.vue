<template>
    <div
        class="relative bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all border group border-gray-200">
        <div class="p-5 flex flex-col h-full">
            <!-- Header: Icon, Date and ID -->
            <div class="flex gap-4 items-center mb-4">
                <div class="bg-primary/10 rounded-full w-12 h-12 flex items-center justify-center shrink-0">
                    <svg class="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>
                <div class="flex-1 min-w-0 flex justify-between items-start">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-bold text-gray-900 text-base">
                                {{ subscription.type === 'request' ? 'Permintaan' : 'Langganan' }} #{{ subscription.name
                                }}
                            </h3>
                        </div>
                        <p class="text-xs text-gray-500 font-semibold mt-1">{{ formatDate(subscription.creation ||
                            subscription.start_date) }}</p>
                    </div>
                    <!-- Status Badge -->
                    <div
                        :class="['px-3 py-1 rounded-full flex items-center justify-center text-xs font-bold', statusBadgeClass]">
                        {{ statusLabel }}
                    </div>
                </div>
            </div>

            <!-- Item Section -->
            <div class="mb-4">
                <div class="flex gap-3 mb-3">
                    <div
                        class="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 border border-gray-100 shrink-0 overflow-hidden">
                        <img v-if="subscription.image" :src="subscription.image" :alt="subscription.item_name"
                            class="w-full h-full object-cover" />
                        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-semibold text-gray-900 line-clamp-1">{{ subscription.item_name ||
                            subscription.plan_name }}</p>
                        <p class="text-xs text-gray-500">{{ subscription.plan_name }}</p>
                    </div>
                </div>

                <!-- Subscription Details -->
                <div class="text-xs text-gray-500 space-y-1">
                    <div class="flex items-center justify-between">
                        <span>Mulai:</span>
                        <span class="font-semibold">{{ formatDate(subscription.start_date) }}</span>
                    </div>
                    <div v-if="subscription.end_date" class="flex items-center justify-between">
                        <span>Berakhir:</span>
                        <span class="font-semibold">{{ formatDate(subscription.end_date) }}</span>
                    </div>
                    <div v-if="subscription.billing_interval" class="flex items-center justify-between">
                        <span>Periode:</span>
                        <span class="font-semibold">Per {{ subscription.billing_interval }}</span>
                    </div>
                </div>
            </div>

            <!-- Divider -->
            <div class="h-px bg-gray-100 w-full mb-4"></div>

            <!-- Footer: Total and Action -->
            <div class="flex justify-between items-center gap-3">
                <div>
                    <p class="text-xs text-gray-500 mb-1">
                        {{ subscription.type === 'request' ? 'Estimasi Biaya' : 'Biaya Langganan' }}
                    </p>
                    <p class="text-base font-bold text-gray-900">
                        {{ subscription.cost ? formatIDR(subscription.cost) : 'N/A' }}
                        <span v-if="subscription.billing_interval" class="text-xs font-normal text-gray-500">/ {{
                            subscription.billing_interval }}</span>
                    </p>
                </div>

                <!-- Action Button -->
                <button @click="$emit('view', subscription)"
                    class="px-5 py-2.5 rounded-lg text-sm font-bold transition-colors bg-primary text-white hover:bg-primary-dark">
                    Lihat Detail
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SubscriptionItem } from '@/types/order'
import { formatIDR } from '@/utils/formatters'

const props = defineProps<{
    subscription: SubscriptionItem
}>()

defineEmits(['view'])

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

// Get status badge class (matching OrderCard design)
const statusBadgeClass = computed(() => {
    if (props.subscription.type === 'request') {
        switch (props.subscription.status) {
            case 'Active':
            case 'Approved':
                return 'bg-[#e6fffa] text-[#007f62]' // Green like OrderCard
            case 'Submitted':
                return 'bg-[#e6f7ff] text-[#1890ff]' // Blue
            case 'Draft':
                return 'bg-[#fff7e6] text-[#faad14]' // Orange
            case 'Cancelled':
                return 'bg-red-50 text-red-600'
            default:
                return 'bg-blue-50 text-blue-600'
        }
    } else {
        switch (props.subscription.status) {
            case 'Active':
                return 'bg-[#e6fffa] text-[#007f62]' // Green
            case 'Past Due Date':
            case 'Unpaid':
                return 'bg-[#fff7e6] text-[#faad14]' // Orange
            case 'Cancelled':
                return 'bg-red-50 text-red-600'
            default:
                return 'bg-blue-50 text-blue-600'
        }
    }
})
</script>
