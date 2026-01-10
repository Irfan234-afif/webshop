<template>
  <DefaultLayout>
    <div class="min-h-screen bg-background py-8">
      <Container>
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900">Pengembalian Saya</h1>
          <p class="text-gray-600 mt-2">
            Pantau status pengajuan pengembalian barang Anda
          </p>
        </div>

        <!-- Filter tabs -->
        <div class="bg-white border border-gray-200 rounded-xl p-4 mb-6">
          <div class="flex flex-wrap gap-2">
            <button v-for="status in filterStatuses" :key="status.value ?? status.label"
              @click="selectedStatus = status.value" class="px-4 py-2 rounded-lg font-medium transition-colors" :class="{
                'bg-primary text-white': selectedStatus === status.value,
                'bg-gray-100 text-gray-700 hover:bg-gray-200': selectedStatus !== status.value
              }">
              {{ status.label }}
            </button>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="isLoading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
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
            {{selectedStatus === null
              ? 'Anda belum pernah mengajukan pengembalian barang'
              : `Tidak ada pengajuan dengan status "${filterStatuses.find(s => s.value === selectedStatus)?.label}"`
            }}
          </p>
        </div>

        <!-- Return requests list -->
        <div v-else class="grid grid-cols-1 gap-4">
          <div v-for="request in returnRequests" :key="request.name"
            class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow cursor-pointer"
            @click="viewReturnRequest(request.name)">
            <div class="flex items-start justify-between mb-4">
              <div>
                <h3 class="font-bold text-gray-900 text-lg">{{ request.name }}</h3>
                <p class="text-sm text-gray-500">Pesanan: {{ request.sales_order }}</p>
              </div>
              <span class="px-3 py-1 rounded-full text-sm font-medium" :class="getStatusClass(request.status)">
                {{ getStatusLabel(request.status) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div>
                <p class="text-sm text-gray-500">Tanggal Pengajuan</p>
                <p class="font-medium text-gray-900">{{ formatDate(request.posting_date) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Alasan</p>
                <p class="font-medium text-gray-900">{{ request.return_reason }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Metode Refund</p>
                <p class="font-medium text-gray-900">{{ request.refund_payment_mode }}</p>
              </div>
            </div>

            <div v-if="request.return_delivery_note || request.credit_note"
              class="bg-green-50 border border-green-200 rounded-lg p-3">
              <p class="text-sm text-green-800">
                <span class="font-medium">Dokumen:</span>
                <span v-if="request.return_delivery_note"> DN: {{ request.return_delivery_note }}</span>
                <span v-if="request.credit_note"> | CN: {{ request.credit_note }}</span>
              </p>
            </div>
          </div>
        </div>
      </Container>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useReturnsStore } from '@/stores/returns'
import Container from '@/components/layout/Container.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const router = useRouter()
const returnsStore = useReturnsStore()

const selectedStatus = ref<string | null>(null)

const filterStatuses = [
  { value: null, label: 'Semua' },
  { value: 'Pending Approval', label: 'Menunggu Persetujuan' },
  { value: 'Approved', label: 'Disetujui' },
  { value: 'Processing', label: 'Diproses' },
  { value: 'Completed', label: 'Selesai' },
  { value: 'Rejected', label: 'Ditolak' }
]

const isLoading = computed(() => returnsStore.isLoading)
const error = computed(() => returnsStore.error)
const returnRequests = computed(() => returnsStore.returnRequests)

watch(selectedStatus, () => {
  loadReturnRequests()
})

onMounted(async () => {
  await loadReturnRequests()
})

async function loadReturnRequests() {
  try {
    const filters: any = {}

    if (selectedStatus.value) {
      filters.status = selectedStatus.value
    }

    await returnsStore.fetchReturnRequests(filters)
  } catch (err) {
    console.error('Error loading return requests:', err)
  }
}

function viewReturnRequest(requestId: string) {
  // You can implement a detail modal or navigate to detail page
  console.log('View return request:', requestId)
  // For now, just log. In future, could open a modal or detail page
}

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
  if (status === 'Draft') return 'Menunggu Persetujuan'
  const match = filterStatuses.find(s => s.value === status)
  return match?.label || status
}

function getStatusClass(status: string): string {
  switch (status) {
    case 'Completed':
      return 'bg-green-100 text-green-800'
    case 'Approved':
    case 'Processing':
      return 'bg-blue-100 text-blue-800'
    case 'Pending Approval':
    case 'Draft':
      return 'bg-yellow-100 text-yellow-800'
    case 'Rejected':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script>
