<template>
    <div class="bg-white border text-left border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
        <!-- Header -->
        <div class="flex items-start justify-between mb-6 pb-6 border-b border-gray-100">
            <div class="flex items-center gap-4">
                <div class="bg-[#ac208e] rounded-full w-12 h-12 flex items-center justify-center shrink-0">
                    <ReceiptIcon class="w-6 h-6 text-white" />
                </div>
                <div>
                    <h3 class="font-bold text-gray-900 text-base">
                        Pesanan #{{ returnRequest.sales_order }}
                    </h3>
                    <p class="text-sm text-gray-400 font-semibold mt-1">
                        {{ formatDate(returnRequest.posting_date) }}
                    </p>
                </div>
            </div>
        </div>

        <!-- Status -->
        <div class="bg-gray-50 rounded-lg p-4 flex items-center justify-between mb-6">
            <span class="font-bold text-gray-900 text-sm">Status</span>
            <div class="flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full" :class="getStatusDotClass(returnRequest.status)"></span>
                <span class="text-sm font-bold" :class="getStatusTextClass(returnRequest.status)">
                    {{ getStatusLabel(returnRequest.status) }}
                </span>
            </div>
        </div>

        <!-- Order Info -->
        <div class="mb-6">
            <h4 class="font-bold text-gray-900 text-sm mb-4">Pesanan</h4>
            <div class="space-y-3">
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Nomor Pesanan</span>
                    <span class="text-gray-900 font-medium text-right">#{{ returnRequest.sales_order }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Tanggal</span>
                    <span class="text-gray-900 font-medium text-right">{{ formatDate(returnRequest.transaction_date)
                    }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Nama Siswa</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.student_name || '-' }}</span>
                </div>
                <!-- Assuming Unit/SMA is not readily available, skipping or could parse if needed -->
                <!-- <div class="flex justify-between text-sm">
          <span class="text-gray-500">Unit</span>
          <span class="text-gray-900 font-medium text-right">SMA</span>
        </div> -->
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Jenis Pengambilan</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.pickup_type || '-' }}</span>
                </div>
                <div v-if="returnRequest.pickup_schedule" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Jadwal Pengambilan</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.pickup_schedule }}</span>
                </div>
                <div v-if="returnRequest.virtual_account" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Nomor Virtual Account</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.virtual_account }}</span>
                </div>
                <div v-if="returnRequest.grand_total" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Total Pesanan</span>
                    <span class="text-gray-900 font-medium text-right">{{ formatIDR(returnRequest.grand_total) }}</span>
                </div>
            </div>
        </div>

        <div class="border-t border-gray-100 my-6"></div>

        <!-- Return Info -->
        <div class="mb-8">
            <h4 class="font-bold text-gray-900 text-sm mb-4">Informasi Pengembalian</h4>
            <div class="space-y-3">
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Alasan Pengembalian</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.return_reason }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Metode Pengembalian dana</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.refund_payment_mode }}</span>
                </div>
                <div v-if="returnRequest.bank_name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Bank</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.bank_name }}</span>
                </div>
                <div v-if="returnRequest.account_number" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Nomor Rekening</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.account_number }}</span>
                </div>
                <div v-if="returnRequest.account_holder_name" class="flex justify-between items-center text-sm">
                    <span class="text-gray-500 font-medium">Nama Pemilik Rekening</span>
                    <span class="text-gray-900 font-medium text-right">{{ returnRequest.account_holder_name }}</span>
                </div>
                <!-- <div v-if="!returnRequest.credit_note && !returnRequest.return_delivery_note"
                    class="flex justify-between items-start text-sm">
                    <span class="text-gray-500 font-medium shrink-0">Estimasi Waktu Refund Dana</span>
                    <span class="text-gray-900 font-medium text-right">Maks H+1 Setelah Barang Dikembalikan</span>
                </div> -->
            </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-4">
            <button v-if="['Draft', 'Pending Approval'].includes(returnRequest.status)"
                @click="$emit('cancel', returnRequest)"
                class="flex-1 py-3 px-4 border border-gray-200 rounded-lg text-[#ac208e] font-bold text-sm hover:bg-gray-50 transition-colors">
                Batalkan Pengajuan
            </button>
            <button @click="$emit('view', returnRequest)"
                class="flex-1 py-3 px-4 bg-[#ac208e] text-white rounded-lg font-bold text-sm hover:bg-[#8f1b76] transition-colors w-full">
                Lihat Detail
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ReturnRequest } from '@/types/returns'
import { formatIDR } from '@/utils/formatters'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'

const props = defineProps<{
    returnRequest: ReturnRequest
}>()

const emit = defineEmits(['view', 'cancel'])

function formatDate(dateString?: string): string {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleDateString('id-ID', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
    })
}

function getStatusLabel(status: string): string {
    const map: Record<string, string> = {
        'Draft': 'Menunggu Persetujuan',
        'Pending Approval': 'Menunggu Persetujuan',
        'Approved': 'Disetujui',
        'Processing': 'Diproses',
        'Completed': 'Selesai',
        'Rejected': 'Ditolak'
    }
    return map[status] || status
}

function getStatusDotClass(status: string): string {
    switch (status) {
        case 'Draft':
        case 'Pending Approval':
            return 'bg-yellow-400'
        case 'Approved':
        case 'Processing':
        case 'Completed':
            return 'bg-green-500'
        case 'Rejected':
            return 'bg-red-500'
        default:
            return 'bg-gray-400'
    }
}

function getStatusTextClass(status: string): string {
    switch (status) {
        case 'Draft':
        case 'Pending Approval':
            return 'text-yellow-600'
        case 'Approved':
        case 'Processing':
        case 'Completed':
            return 'text-green-600'
        case 'Rejected':
            return 'text-red-600'
        default:
            return 'text-gray-600'
    }
}
</script>
