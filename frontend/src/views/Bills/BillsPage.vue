<template>
  <DefaultLayout>
    <Container class="py-6">
      <Breadcrumb :items="[
        { label: 'Home', to: '/' },
        { label: activeTab === 'bills' ? 'Tagihan Berjalan' : 'Riwayat Pembayaran' }
      ]" class="mb-6" />

      <h1 class="text-xl font-bold text-gray-900 mb-10">Tagihan & Pembayaran</h1>

      <!-- Tab Navigation -->
      <div class="flex gap-6 mb-8 border-b border-gray-200">
        <button @click="changeTab('bills')" :class="[
          'pb-3 text-lg font-medium transition-colors relative',
          activeTab === 'bills'
            ? 'text-gray-900'
            : 'text-gray-500 hover:text-gray-700'
        ]">
          Tagihan Berjalan
          <div v-if="activeTab === 'bills'"
            class="absolute bottom-0 left-0 right-0 h-[3px] bg-primary rounded-t-full" />
        </button>
        <button @click="changeTab('history')" :class="[
          'pb-3 text-lg font-medium transition-colors relative',
          activeTab === 'history'
            ? 'text-gray-900'
            : 'text-gray-500 hover:text-gray-700'
        ]">
          Riwayat Pembayaran
          <div v-if="activeTab === 'history'"
            class="absolute bottom-0 left-0 right-0 h-[3px] bg-primary rounded-t-full" />
        </button>
      </div>

      <div v-if="billsResource.loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>

      <div v-else-if="bills.length === 0" class="text-center py-12 bg-gray-50 rounded-xl">
        <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M5 13L9 17L19 7" stroke="#10B981" stroke-width="2" stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
        </div>
        <h3 class="text-lg font-bold text-gray-900 mb-2">
          {{ activeTab === 'bills' ? 'Tidak Ada Tagihan' : 'Belum Ada Riwayat' }}
        </h3>
        <p class="text-gray-500">
          {{ activeTab === 'bills'
            ? 'Selamat! Seluruh tagihan Anda telah lunas.'
            : 'Belum ada riwayat pembayaran yang tersedia.' }}
        </p>
        <RouterLink to="/" class="inline-block mt-4 text-primary font-medium hover:underline">
          Kembali ke Beranda
        </RouterLink>
      </div>

      <!-- Bills Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <BillCard v-for="bill in bills" :key="bill.name" :bill="bill" :is-paid="activeTab === 'history'" @pay="payBill"
          @view="viewBill" />
      </div>

      <!-- Payment Modal -->
      <BillPaymentModal v-if="selectedBill" :is-open="isPaymentModalOpen" :bill="selectedBill"
        @close="closePaymentModal" @payment-initiated="handlePaymentInitiated" />

      <!-- Detail Modal -->
      <BillDetailModal v-if="selectedBillForDetail" :is-open="isDetailModalOpen" :bill="selectedBillForDetail"
        :is-paid="activeTab === 'history'" @close="closeDetailModal" @pay="handlePayFromDetail" />

    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import BillPaymentModal from '@/components/features/bills/BillPaymentModal.vue'
import BillCard from '@/components/features/bills/BillCard.vue'
import BillDetailModal from '@/components/features/bills/BillDetailModal.vue'
import { formatIDR } from '@/utils/formatters'

const router = useRouter()
const route = useRoute()
const bills = ref<any[]>([])

// Tab state
const activeTab = ref<'bills' | 'history'>(
  (route.query.tab as 'bills' | 'history') || 'bills'
)

// Payment Modal State
const isPaymentModalOpen = ref(false)
const selectedBill = ref<any | null>(null)

// Detail Modal State
const isDetailModalOpen = ref(false)
const selectedBillForDetail = ref<any | null>(null)

const billsResource = createResource({
  url: 'webshop.webshop.api.billing.get_unpaid_bills',
  auto: false,
  params: {
    tab: activeTab.value
  },
  onSuccess: (data: any) => {
    bills.value = data.bills || []
  }
})

// Change tab and update URL
const changeTab = (tab: 'bills' | 'history') => {
  router.push({ query: { ...route.query, tab } })
}

// Watch route changes to sync activeTab
watch(() => route.query.tab, (newTab) => {
  const validTab = (newTab as 'bills' | 'history') || 'bills'
  if (activeTab.value !== validTab) {
    activeTab.value = validTab
  }
}, { immediate: true })

// Watch activeTab changes and fetch data
watch(activeTab, () => {
  billsResource.update({
    params: {
      tab: activeTab.value
    }
  })
  billsResource.fetch()
}, { immediate: true })

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const formatPrice = (amount: number) => {
  return formatIDR(amount)
}

const payBill = (bill: any) => {
  console.log('Initiating payment for bill:', bill.name)

  // Check if Payment Request already exists (from backend flag)
  if (bill.has_payment_request) {
    // Direct redirect to payment page if PR exists
    console.log('Existing Payment Request found, redirecting to payment page')
    router.push(`/bills/${bill.name}/payment`)
    return
  }

  // Open modal to select payment method for new payment
  selectedBill.value = bill
  isPaymentModalOpen.value = true
}

const viewBill = (bill: any) => {
  console.log('Viewing bill details:', bill.name)
  selectedBillForDetail.value = bill
  isDetailModalOpen.value = true
}

const closeDetailModal = () => {
  isDetailModalOpen.value = false
  selectedBillForDetail.value = null
}

const handlePayFromDetail = (bill: any) => {
  // Close detail modal and open payment flow
  closeDetailModal()
  payBill(bill)
}

const closePaymentModal = () => {
  isPaymentModalOpen.value = false
  selectedBill.value = null
}

const handlePaymentInitiated = (invoiceName: string) => {
  console.log('Payment initiated for invoice:', invoiceName)
  closePaymentModal()
  // Refresh bills list
  billsResource.reload()
}
</script>
