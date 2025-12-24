<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
        @click="emit('close')"
      >
        <!-- Modal Content -->
        <Transition name="scale">
          <div
            v-if="isOpen"
            class="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col"
            @click.stop
            role="dialog"
            aria-modal="true"
          >
            <!-- Header -->
            <div class="bg-white rounded-t-xl p-8 border-b border-gray-100">
              <div class="flex items-start gap-6">
                <!-- Receipt Icon -->
                <div class="w-[50px] h-[50px] bg-primary rounded-full flex items-center justify-center flex-shrink-0">
                  <ReceiptIcon :size="25" color="#FFFFFF" />
                </div>

                <!-- Order Info -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-base font-bold text-gray-900 mb-2 capitalize">
                    Pesanan #{{ order.name }}
                  </h3>
                  <p class="text-sm font-semibold text-text-secondary">
                    {{ formatDate(order.transaction_date) }}
                  </p>
                </div>

                <!-- Close Button -->
                <button
                  @click="emit('close')"
                  class="flex-shrink-0 w-[18px] h-[18px] text-text-secondary hover:text-gray-600 transition-colors"
                  aria-label="Close"
                >
                  <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" class="rotate-45">
                    <path
                      d="M9 0L9 18M0 9L18 9"
                      stroke="currentColor"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
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
                      <div :class="['w-[11px] h-[11px] rounded-full', getStatusDotClass(order.status)]" />
                      <p :class="['text-sm font-bold capitalize', getStatusTextClass(order.status)]">
                        {{ getStatusLabel(order.status) }}
                      </p>
                    </div>
                  </div>

                  <!-- Payment Deadline Warning -->
                  <div
                    v-if="order.status === 'Draft' || order.status === 'Pending Payment'"
                    class="bg-white rounded-lg p-4 flex items-start gap-3"
                  >
                    <InfoCircleIcon :size="16" color="#FFBC4F" class="flex-shrink-0 mt-0.5" />
                    <p class="text-sm font-semibold text-text-secondary flex-1">
                      Selesaikan pembayaran sebelum {{ formatPaymentDeadline(order.transaction_date) }}
                    </p>
                  </div>
                </div>

                <!-- Order Details Container -->
                <div class="flex flex-col">
                  <!-- Detail Pesanan -->
                  <div class="bg-white border-[1.5px] border-gray-100 rounded-t-xl p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Detail Pesanan</h4>
                    <div class="space-y-4">
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Nomor Pesanan</span>
                        <span class="text-right">#{{ order.name }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Tanggal</span>
                        <span class="text-right">{{ formatDate(order.transaction_date) }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Nama Siswa</span>
                        <span class="text-right">{{ order.student || 'N/A' }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Unit</span>
                        <span class="text-right">{{ order.school_unit || 'SMA' }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Jenis Pengambilan</span>
                        <span class="text-right">{{ order.pickup_type || 'Ambil di Koperasi' }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Jadwal Pengambilan</span>
                        <span class="text-right">{{ order.delivery_date || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Informasi Produk & Layanan -->
                  <div class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-8 capitalize">Informasi Produk & Layanan</h4>
                    <div class="space-y-4">
                      <div v-for="item in order.items" :key="item.item_code" class="flex gap-2 justify-between">
                        <div class="flex gap-3">
                          <div class="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 border border-gray-100 shrink-0 overflow-hidden">
                              <img v-if="item.image" :src="item.image" :alt="item.item_name" class="w-full h-full object-cover" />
                              <span v-else class="text-[10px]">No Img</span>
                          </div>
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-semibold text-gray-900 line-clamp-1">{{ item.item_name }}</p>
                            <p class="text-xs text-gray-500">{{ item.qty }} barang</p>
                          </div>
                        </div>
                        <div>
                          <p class="text-sm font-semibold text-text-secondary line-clamp-1">{{ formatIDR(item.amount) }}</p>
                        </div>
                      </div>
                      <!-- <div
                        v-for="(item, index) in orderItems"
                        :key="index"
                        class="flex items-center justify-between text-sm font-semibold text-text-secondary"
                      >
                        <span>{{ item.name }}</span>
                        <span class="text-right">{{ formatIDR(item.amount) }}</span>
                      </div>
                      <div v-if="order.voucher_amount" class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Voucher</span>
                        <span class="text-right">{{ order.voucher_amount ? formatIDR(order.voucher_amount) : '0' }}</span>
                      </div> -->
                      <div
                        v-if="order.discount_amount"
                        class="flex items-center justify-between text-sm font-semibold"
                      >
                        <span class="text-text-secondary">Diskon Anggota Koperasi</span>
                        <span class="text-red-500 text-right">- {{ formatIDR(order.discount_amount) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Metode Pembayaran -->
                  <div class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 rounded-b-xl p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Metode Pembayaran</h4>
                    <div class="space-y-4">
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Nomor Virtual Account</span>
                        <span class="text-right">{{ order.virtual_account || 'N/A' }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Payment Gateway</span>
                        <span class="text-right">{{ order.payment_gateway || 'Xendit' }}</span>
                      </div>
                      <div class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Total Pesanan</span>
                        <span class="text-right">{{ formatIDR(order.grand_total) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer Actions -->
            <div class="bg-white border-t-[1.5px] border-gray-100 rounded-b-xl p-8 flex items-center justify-between gap-4">
              <router-link
                v-if="order.per_billed < 100"
                :to="{ name: 'checkout-payment', params: { id: order.name } }"
                class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize text-center"
              >
                Bayar Pesanan - {{ formatIDR(order.grand_total) }}
              </router-link>
              <button
                v-else
                @click="emit('close')"
                class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize"
              >
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
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'
import InfoCircleIcon from '@/components/icons/InfoCircleIcon.vue'

interface OrderItem {
  item_code: string
  item_name: string
  qty: number
  image?: string
  amount: number
  name?: string // Backwards compatibility if needed, but we'll map
}

interface Order {
  name: string
  grand_total: number
  transaction_date: string
  status: string
  student: string
  school_unit?: string
  pickup_type?: string
  delivery_date?: string
  voucher_amount?: number
  discount_amount?: number
  virtual_account?: string
  per_billed: number
  payment_gateway?: string
  items?: OrderItem[]
  payment_method_type?: string
  payment_request_status?: string
}

interface Props {
  isOpen: boolean
  order: Order
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  payOrder: [orderId: string]
  backToPaymentMethod: [orderId: string]
}>()


// Format date to readable format
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Format payment deadline (add 1 day to transaction date)
const formatPaymentDeadline = (dateString: string) => {
  const date = new Date(dateString)
  date.setDate(date.getDate() + 1)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Get status label in Indonesian
const getStatusLabel = (status: string) => {
  const statusMap: Record<string, string> = {
    'To Deliver and Bill': 'Menunggu Pembayaran',
    'Pending Payment': 'Menunggu Pembayaran',
    'To Deliver': 'Pesanan Diproses',
    'Processing': 'Pesanan Diproses',
    'Shipped': 'Pesanan Dikirim',
    'Completed': 'Selesai',
    'Cancelled': 'Dibatalkan',
    'Canceled': 'Dibatalkan'
  }
  return statusMap[status] || status
}

// Get status dot color class
const getStatusDotClass = (status: string) => {
  switch (status) {
    case 'Completed':
      return 'bg-green-500'
    case 'Shipped':
      return 'bg-green-500'
    case 'To Deliver':
    case 'Processing':
      return 'bg-blue-500'
    case 'Cancelled':
    case 'Canceled':
      return 'bg-red-500'
    case 'Draft':
    case 'To Deliver and Bill':
      return 'bg-orange-500'
    default:
      return 'bg-gray-500'
  }
}

// Get status text color class
const getStatusTextClass = (status: string) => {
  switch (status) {
    case 'Completed':
      return 'text-green-700'
    case 'Shipped':
      return 'text-green-700'
    case 'To Deliver':
    case 'Processing':
      return 'text-blue-700'
    case 'Cancelled':
    case 'Canceled':
      return 'text-red-700'
    case 'Draft':
    case 'To Deliver and Bill':
      return 'text-orange-700'
    default:
      return 'text-gray-700'
  }
}

// // Calculate installment amount (example: 1/3 of total)
// const calculateInstallmentAmount = () => {
//   return Math.ceil(props.order.grand_total / 3)
// }

// Handle back to payment method
const handleBackToPaymentMethod = () => {
  emit('backToPaymentMethod', props.order.name)
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
