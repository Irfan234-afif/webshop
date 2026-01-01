<template>
  <DefaultLayout>
    <Container class="py-6">
      <Breadcrumb :items="[
        { label: 'Home', to: '/' },
        { label: 'Tagihan Berjalan' }
      ]" class="mb-6" />

      <h1 class="text-xl font-bold text-gray-900 mb-2">Tagihan Berjalan</h1>
      <p class="text-gray-500 mb-8">Daftar tagihan berlangganan yang belum dibayar.</p>

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
        <h3 class="text-lg font-bold text-gray-900 mb-2">Tidak Ada Tagihan</h3>
        <p class="text-gray-500">Selamat! Seluruh tagihan Anda telah lunas.</p>
        <RouterLink to="/" class="inline-block mt-4 text-primary font-medium hover:underline">
          Kembali ke Beranda
        </RouterLink>
      </div>

      <div v-else class="space-y-4">
        <div v-for="bill in bills" :key="bill.name"
          class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <!-- Left Info -->
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <span class="text-sm font-medium text-gray-900">{{ bill.name }}</span>
                <span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                  Belum Lunas
                </span>
              </div>

              <div class="text-sm text-gray-500 mb-1">
                Jatuh Tempo: <span class="font-medium text-gray-900">{{ formatDate(bill.due_date) }}</span>
              </div>
              <div class="text-xs text-gray-400">
                Tanggal Terbit: {{ formatDate(bill.posting_date) }}
              </div>
            </div>

            <!-- Right Info & Action -->
            <div class="flex flex-col md:items-end gap-2">
              <div class="text-right">
                <span class="block text-xs text-gray-500">Total Tagihan</span>
                <span class="text-lg font-bold text-primary">{{ formatPrice(bill.outstanding_amount) }}</span>
              </div>
              <button @click="payBill(bill)"
                class="bg-primary hover:bg-primary-dark text-white font-medium px-6 py-2 rounded-lg transition-colors text-sm w-full md:w-auto">
                {{ bill.has_payment_request ? 'Lanjutkan Pembayaran' : 'Bayar Sekarang' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Payment Modal -->
      <BillPaymentModal v-if="selectedBill" :is-open="isPaymentModalOpen" :bill="selectedBill"
        @close="closePaymentModal" @payment-initiated="handlePaymentInitiated" />

    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { useRouter } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import BillPaymentModal from '@/components/features/bills/BillPaymentModal.vue'
import { formatIDR } from '@/utils/formatters'

const router = useRouter()
const bills = ref<any[]>([])

// Payment Modal State
const isPaymentModalOpen = ref(false)
const selectedBill = ref<any | null>(null)

const billsResource = createResource({
  url: 'webshop.webshop.api.billing.get_unpaid_bills',
  auto: true,
  onSuccess: (data: any) => {
    bills.value = data.bills || []
  }
})

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
