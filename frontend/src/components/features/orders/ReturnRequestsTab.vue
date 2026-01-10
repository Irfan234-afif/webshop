<template>
    <div class="space-y-6">
        <!-- Loading state -->
        <div v-if="isLoading" class="flex justify-center items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-[#ac208e]"></div>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-700">{{ error }}</p>
        </div>

        <!-- Empty state -->
        <div v-else-if="returnRequests.length === 0"
            class="bg-white border border-gray-200 rounded-xl p-12 text-center">
            <svg class="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Belum Ada Pengajuan Pengembalian</h3>
            <p class="text-gray-600">
                {{ filters.status || filters.student || filters.search
                    ? 'Tidak ada pengajuan yang cocok dengan filter'
                    : 'Anda belum pernah mengajukan pengembalian barang'
                }}
            </p>
        </div>

        <!-- Return requests list -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-6">
            <ReturnRequestCard v-for="request in returnRequests" :key="request.name" :return-request="request"
                @view="viewReturnRequest" @cancel="confirmCancel" />
        </div>

        <ReturnRequestDetailModal :is-open="isDetailModalOpen" :return-request="detailRequest" @close="closeDetailModal"
            @cancel="confirmCancel" />
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useReturnsStore } from '@/stores/returns'
import ReturnRequestCard from './ReturnRequestCard.vue'
import ReturnRequestDetailModal from './ReturnRequestDetailModal.vue'
import type { ReturnRequest } from '@/types/returns'

const props = defineProps<{
    filters: {
        student: string
        status: string
        search: string
    }
}>()

const returnsStore = useReturnsStore()

const isDetailModalOpen = ref(false)
const detailRequest = ref<ReturnRequest | null>(null)

const isLoading = computed(() => returnsStore.isLoading)
const error = computed(() => returnsStore.error)
const returnRequests = computed(() => returnsStore.returnRequests)

watch(() => props.filters, () => {
    loadReturnRequests()
}, { deep: true })

onMounted(async () => {
    await loadReturnRequests()
})

async function loadReturnRequests() {
    try {
        const queryFilters: any = {}

        if (props.filters.status) {
            queryFilters.status = props.filters.status
        }
        if (props.filters.student) {
            queryFilters.student_name = props.filters.student
        }
        if (props.filters.search) {
            queryFilters.name = ['like', `%${props.filters.search}%`]
        }

        await returnsStore.fetchReturnRequests(queryFilters)
    } catch (err) {
        console.error('Error loading return requests:', err)
    }
}

function viewReturnRequest(request: ReturnRequest) {
    detailRequest.value = request
    isDetailModalOpen.value = true
}

function closeDetailModal() {
    isDetailModalOpen.value = false
    detailRequest.value = null
}

function confirmCancel(request: ReturnRequest) {
    // TODO: Implement cancel logic
    if (confirm('Apakah Anda yakin ingin membatalkan pengajuan ini?')) {
        console.log('Cancel return request:', request.name)
    }
}
</script>
