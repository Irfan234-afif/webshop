<template>
    <div
        class="relative bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all border group border-gray-200">
        <div class="p-5 flex flex-col h-full">
            <!-- Header: Icon, Date and ID -->
            <div class="flex gap-4 items-center mb-4">
                <div class="bg-primary/10 rounded-full w-12 h-12 flex items-center justify-center shrink-0">
                    <ReceiptIcon class="w-6 h-6 text-primary" />
                </div>
                <div class="flex-1 min-w-0 flex justify-between items-start">
                    <div>
                        <div class="flex items-center gap-2">
                            <h3 class="font-bold text-gray-900 text-base">Invoice #{{ bill.name }}</h3>
                        </div>
                        <p class="text-xs text-gray-500 font-semibold mt-1">
                            {{ isPaid ? 'Dibayar' : 'Jatuh Tempo' }}: {{ formatDate(isPaid ? bill.posting_date :
                            bill.due_date) }}
                        </p>
                    </div>
                    <!-- Status Badge -->
                    <div
                        :class="['px-3 py-1 rounded-full flex items-center justify-center text-xs font-bold whitespace-nowrap', statusBadgeClass]">
                        {{ statusLabel }}
                    </div>
                </div>
            </div>

            <!-- Bill Info Section -->
            <div class="mb-4 space-y-2">
                <div class="flex justify-between text-sm">
                    <span class="text-gray-500">Tanggal Terbit</span>
                    <span class="text-gray-900 font-medium">{{ formatDate(bill.posting_date) }}</span>
                </div>
                <div v-if="!isPaid" class="flex justify-between text-sm">
                    <span class="text-gray-500">Jatuh Tempo</span>
                    <span class="text-gray-900 font-medium">{{ formatDate(bill.due_date) }}</span>
                </div>
                <div v-if="bill.subscription" class="flex justify-between text-sm">
                    <span class="text-gray-500">Langganan</span>
                    <span class="text-gray-900 font-medium">{{ bill.subscription }}</span>
                </div>
            </div>

            <!-- Divider -->
            <div class="flex-1"></div>
            <div class="h-px bg-gray-100 w-full mb-4"></div>

            <!-- Footer: Total and Action -->
            <div class="flex justify-between items-center gap-3">
                <div>
                    <p class="text-xs text-gray-500 mb-1">{{ isPaid ? 'Total Dibayar' : 'Total Tagihan' }}</p>
                    <p class="text-base font-bold text-gray-900">
                        {{ formatIDR(isPaid ? bill.grand_total : bill.outstanding_amount) }}
                    </p>
                </div>

                <!-- Action Button based on Status -->
                <button v-if="!isPaid" @click="$emit('pay', bill)"
                    class="px-5 py-2.5 rounded-lg text-sm font-bold transition-colors bg-primary text-white hover:bg-primary-dark">
                    {{ bill.has_payment_request ? 'Lanjutkan' : 'Bayar' }}
                </button>
                <button v-else @click="$emit('view', bill)"
                    class="px-5 py-2.5 rounded-lg text-sm font-bold transition-colors bg-gray-100 text-gray-700 hover:bg-gray-200">
                    Lihat Detail
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatIDR } from '@/utils/formatters'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'

const props = defineProps<{
    bill: any
    isPaid?: boolean
}>()

defineEmits(['pay', 'view'])

const formatDate = (dateString: string) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

// Status Badge Logic
const statusLabel = computed(() => {
    if (props.isPaid) {
        return 'Lunas'
    }
    return 'Belum Lunas'
})

const statusBadgeClass = computed(() => {
    if (props.isPaid) {
        return 'bg-[#e6fffa] text-[#007f62]' // Green - Lunas
    }
    return 'bg-[#fff7e6] text-[#faad14]' // Orange - Belum Lunas
})
</script>
