<template>
    <Teleport to="body">
        <!-- Backdrop -->
        <Transition name="fade">
            <div v-if="isOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
                @click="$emit('close')">
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
                                    class="w-[50px] h-[50px] bg-[#ac208e] rounded-full flex items-center justify-center flex-shrink-0">
                                    <ReceiptIcon :size="25" color="#FFFFFF" />
                                </div>

                                <!-- Info -->
                                <div class="flex-1 min-w-0">
                                    <h3 class="text-base font-bold text-gray-900 mb-2 capitalize">
                                        Pengajuan #{{ returnRequest?.sales_order }}
                                    </h3>
                                    <p class="text-sm font-semibold text-gray-500">
                                        {{ formatDate(returnRequest?.posting_date) }}
                                    </p>
                                </div>

                                <!-- Close Button -->
                                <button @click="$emit('close')"
                                    class="flex-shrink-0 w-[18px] h-[18px] text-gray-400 hover:text-gray-600 transition-colors"
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
                            <div v-if="loading" class="flex justify-center py-12">
                                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-[#ac208e]"></div>
                            </div>

                            <div v-else-if="detail" class="flex flex-col gap-6">
                                <!-- Status Section -->
                                <div class="bg-gray-50/80 border-[1.5px] border-gray-100 rounded-xl p-6">
                                    <div class="flex items-center justify-between">
                                        <p class="text-sm font-semibold text-gray-500">Status</p>
                                        <div class="flex items-center gap-2">
                                            <div
                                                :class="['w-[11px] h-[11px] rounded-full', getStatusDotClass(detail.status)]" />
                                            <p
                                                :class="['text-sm font-bold capitalize', getStatusTextClass(detail.status)]">
                                                {{ getStatusLabel(detail.status) }}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <!-- Return Items -->
                                <div class="bg-white border-[1.5px] border-gray-100 rounded-xl p-6">
                                    <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Barang yang Dikembalikan
                                    </h4>
                                    <div class="space-y-4">
                                        <div v-for="item in detail.items" :key="item.item_code"
                                            class="flex gap-4 justify-between items-start">
                                            <div class="flex-1">
                                                <p class="text-sm font-semibold text-gray-900 line-clamp-2">{{
                                                    item.item_name }}</p>
                                                <p class="text-xs text-gray-500">{{ item.item_code }}</p>
                                            </div>
                                            <div class="text-right shrink-0">
                                                <p class="text-sm font-bold text-gray-900">{{ item.qty }} x {{
                                                    formatIDR(item.rate) }}</p>
                                                <p class="text-sm font-semibold text-[#ac208e]">{{
                                                    formatIDR(item.amount) }}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Return Info -->
                                <div class="bg-white border-[1.5px] border-gray-100 rounded-xl p-6">
                                    <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Informasi Pengembalian
                                    </h4>
                                    <div class="space-y-4">
                                        <div class="flex justify-between items-center text-sm">
                                            <span class="text-gray-500 font-medium">Alasan</span>
                                            <span class="text-gray-900 font-medium text-right">{{ detail.return_reason
                                                }}</span>
                                        </div>
                                        <div v-if="detail.other_reason"
                                            class="flex justify-between items-start text-sm">
                                            <span class="text-gray-500 font-medium shrink-0">Keterangan Lain</span>
                                            <span class="text-gray-900 font-medium text-right max-w-[60%]">{{
                                                detail.other_reason }}</span>
                                        </div>
                                        <div class="border-t border-gray-100 my-2"></div>
                                        <div class="flex justify-between items-center text-sm">
                                            <span class="text-gray-500 font-medium">Metode Refund</span>
                                            <span class="text-gray-900 font-medium text-right">{{
                                                detail.refund_payment_mode }}</span>
                                        </div>

                                        <template v-if="detail.bank_name">
                                            <div class="flex justify-between items-center text-sm">
                                                <span class="text-gray-500 font-medium">Bank</span>
                                                <span class="text-gray-900 font-medium text-right">{{ detail.bank_name
                                                    }}</span>
                                            </div>
                                            <div class="flex justify-between items-center text-sm">
                                                <span class="text-gray-500 font-medium">No. Rekening</span>
                                                <span class="text-gray-900 font-medium text-right">{{
                                                    detail.account_number }}</span>
                                            </div>
                                            <div class="flex justify-between items-center text-sm">
                                                <span class="text-gray-500 font-medium">Nama Pemilik</span>
                                                <span class="text-gray-900 font-medium text-right">{{
                                                    detail.account_holder_name }}</span>
                                            </div>
                                        </template>
                                    </div>
                                </div>

                                <!-- Proof Images -->
                                <div v-if="documents.length > 0"
                                    class="bg-white border-[1.5px] border-gray-100 rounded-xl p-6">
                                    <h4 class="text-sm font-bold text-gray-900 mb-4 capitalize">Bukti Foto / Video</h4>
                                    <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                                        <div v-for="(doc, idx) in documents" :key="idx"
                                            class="aspect-square rounded-lg overflow-hidden border border-gray-200 cursor-pointer group relative"
                                            @click="openImage(doc)">
                                            <img :src="doc"
                                                class="w-full h-full object-cover transition-transform group-hover:scale-105" />
                                            <div
                                                class="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors">
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>
                            <div v-else class="text-center py-8 text-gray-500">
                                Gagal memuat detail pengembalian
                            </div>
                        </div>

                        <!-- Footer -->
                        <div class="bg-white border-t-[1.5px] border-gray-100 rounded-b-xl p-8 flex flex-col gap-4"
                            v-if="detail">
                            <button v-if="['Draft', 'Pending Approval'].includes(detail.status)"
                                @click="$emit('cancel', detail)"
                                class="w-full py-4 px-8 border border-gray-200 text-red-600 font-bold text-sm rounded-lg hover:bg-red-50 transition-colors capitalize">
                                Batalkan Pengajuan
                            </button>
                            <button @click="$emit('close')"
                                class="w-full py-4 px-8 bg-gray-100 text-gray-700 font-bold text-sm rounded-lg hover:bg-gray-200 transition-colors capitalize">
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
import { ref, computed, watch } from 'vue'
import { useReturnsStore } from '@/stores/returns'
import type { ReturnRequest } from '@/types/returns'
import { formatIDR } from '@/utils/formatters'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'

const props = defineProps<{
    isOpen: boolean
    returnRequest: ReturnRequest | null
}>()

const emit = defineEmits(['close', 'cancel'])

const returnsStore = useReturnsStore()
const loading = ref(false)
const detail = ref<any>(null)

watch(() => props.isOpen, async (newVal) => {
    if (newVal && props.returnRequest?.name) {
        document.body.style.overflow = 'hidden'
        await fetchDetail(props.returnRequest.name)
    } else {
        document.body.style.overflow = ''
        detail.value = null
    }
})

async function fetchDetail(name: string) {
    loading.value = true
    try {
        detail.value = await returnsStore.fetchReturnRequestDetail(name)
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const documents = computed(() => {
    if (!detail.value?.supporting_documents) return []
    // supporting_documents can be a string (single url) or stringified array (if multiple, though usually comma separated in simple file fields)
    // or array if backend returns pre-processed.
    // Assuming backend returns string (from `returns.py` which returns doc.supporting_documents)
    // If it's a Text/Code field storing JSON array of strings
    let docs = detail.value.supporting_documents
    if (typeof docs === 'string') {
        if (docs.startsWith('[')) {
            try {
                return JSON.parse(docs)
            } catch {
                return [docs]
            }
        }
        // Comma separated?
        if (docs.includes(',')) return docs.split(',')
        return [docs]
    }
    return Array.isArray(docs) ? docs : []
})

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

const openImage = (url: string) => {
    window.open(url, '_blank')
}
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
