<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div v-if="isOpen" class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
        @click="emit('close')">
        <!-- Modal Content -->
        <Transition name="scale">
          <div v-if="isOpen" class="bg-white rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col"
            @click.stop role="dialog" aria-modal="true">
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
                <button @click="emit('close')"
                  class="flex-shrink-0 w-[18px] h-[18px] text-text-secondary hover:text-gray-600 transition-colors"
                  aria-label="Close">
                  <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg" class="rotate-45">
                    <path d="M9 0L9 18M0 9L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
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
                      <div :class="['w-[11px] h-[11px] rounded-full', getStatusDotClass(getDisplayStatus(order))]" />
                      <p :class="['text-sm font-bold capitalize', getStatusTextClass(getDisplayStatus(order))]">
                        {{ getStatusLabel(getDisplayStatus(order)) }}
                      </p>
                    </div>
                  </div>

                  <!-- Payment Deadline Warning -->
                  <div v-if="getDisplayStatus(order) === 'Draft' || getDisplayStatus(order) === 'Pending Payment'"
                    class="bg-white rounded-lg p-4 flex items-start gap-3">
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

                  <!-- Delivery Proof for History -->
                  <div v-if="order.delivery_image"
                    class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-4 capitalize">Bukti Pengiriman</h4>
                    <div class="h-48 w-full bg-gray-50 rounded-lg overflow-hidden border border-gray-100 cursor-pointer"
                      @click="openImage(order.delivery_image)">
                      <img :src="order.delivery_image" alt="Bukti Pengiriman" class="w-full h-full object-cover" />
                    </div>
                  </div>

                  <!-- Informasi Produk & Layanan -->
                  <div class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-8 capitalize">Informasi Produk & Layanan</h4>
                    <div class="space-y-4">
                      <div v-for="item in order.items" :key="item.item_code" class="flex gap-2 justify-between">
                        <div class="flex gap-3">
                          <div
                            class="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 border border-gray-100 shrink-0 overflow-hidden">
                            <img v-if="item.image" :src="item.image" :alt="item.item_name"
                              class="w-full h-full object-cover" />
                            <span v-else class="text-[10px]">No Img</span>
                          </div>
                          <div class="flex-1 min-w-0">
                            <p class="text-sm font-semibold text-gray-900 line-clamp-1">{{ item.item_name }}</p>
                            <p class="text-xs text-gray-500">{{ item.qty }} barang</p>
                          </div>
                        </div>
                        <div>
                          <p class="text-sm font-semibold text-text-secondary line-clamp-1">
                            {{ formatIDR(item.amount || 0) }}
                          </p>
                        </div>
                      </div>

                      <!-- Coupon Discount (only if applied) -->
                      <div v-if="order.coupon_code && order.discount_amount && order.discount_amount > 0"
                        class="flex items-center justify-between text-sm font-semibold">
                        <span class="text-text-secondary">Diskon Voucher ({{ order.coupon_code }})</span>
                        <span class="text-red-600 text-right">- {{ formatIDR(order.discount_amount) }}</span>
                      </div>
                    </div>
                  </div>

                  <!-- Metode Pembayaran -->
                  <div
                    class="bg-white border-l-[1.5px] border-r-[1.5px] border-b-[1.5px] border-gray-100 rounded-b-xl p-6">
                    <h4 class="text-sm font-bold text-gray-900 mb-6 capitalize">Metode Pembayaran</h4>
                    <div class="space-y-4">
                      <div v-if="order.payment_method_type"
                        class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Metode Pembayaran</span>
                        <span class="text-right">{{ order.payment_method_type }}</span>
                      </div>
                      <div v-if="order.virtual_account"
                        class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Nomor Virtual Account</span>
                        <span class="text-right">{{ order.virtual_account }}</span>
                      </div>
                      <div v-if="order.payment_gateway"
                        class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>Payment Gateway</span>
                        <span class="text-right">{{ order.payment_gateway || 'Xendit' }}</span>
                      </div>

                      <!-- Service Charges from Sales Taxes and Charges -->
                      <div v-for="(charge, index) in order.taxes" :key="index"
                        class="flex items-center justify-between text-sm font-semibold text-text-secondary">
                        <span>{{ charge.description }}</span>
                        <span class="text-right">{{ formatIDR(charge.tax_amount || 0) }}</span>
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
            <div class="bg-white border-t-[1.5px] border-gray-100 rounded-b-xl p-8 flex flex-col gap-4">
              <!-- Primary action buttons -->
              <div class="flex items-center gap-4">
                <router-link v-if="order.per_billed < 100"
                  :to="{ name: 'checkout-payment', params: { id: order.name } }"
                  class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize text-center">
                  Bayar Pesanan - {{ formatIDR(order.grand_total) }}
                </router-link>
                <button v-else-if="!canRequestReturn" @click="emit('close')"
                  class="flex-1 py-4 px-8 bg-primary text-white font-bold text-sm rounded-lg hover:bg-primary-dark transition-colors capitalize">
                  Tutup
                </button>
              </div>

              <!-- Return request button for completed orders -->
              <button v-if="canRequestReturn" @click="openReturnModal"
                class="w-full py-4 px-8 bg-[#ac208e] hover:opacity-90 text-white font-bold text-sm rounded-lg transition-opacity capitalize">
                Ajukan Pengembalian
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

    <!-- Terms & Conditions Modal -->
    <ReturnRequestModal :isOpen="isReturnModalOpen" @accept="navigateToReturnWizard" @close="closeReturnModal" />
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { call } from 'frappe-ui'
import { formatIDR } from '@/utils/formatters'
import { useReturnsStore } from '@/stores/returns'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'
import InfoCircleIcon from '@/components/icons/InfoCircleIcon.vue'
import ReturnRequestModal from '@/components/features/returns/ReturnRequestModal.vue'
import type { Order } from '@/types/order'

// Helper function to get display status
const getDisplayStatus: (order: Order) => string = (order: Order) => order.status != "Completed" ? order.status : order.ecommerce_delivery_status

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

const router = useRouter()
const returnsStore = useReturnsStore()
const isReturnModalOpen = ref(false)
const isEligibleForReturn = ref<boolean | null>(null) // null = not checked yet, true/false = eligibility status

console.log('OrderDetailModal component loaded')

// Status Logic - same as OrderCard.vue
const isWaitingPayment = computed(() => {
  return props.order.status.includes("Bill") || props.order.status.includes("To Pay");
})

const isWaitingApproval = computed(() => {
  // Logic: "Waiting Payment Approval"
  // User uploaded proof (Payment Request Created/Draft)
  if (['Transfer Manual', 'Cash Webshop'].includes(props.order.payment_method_type || '')) {
    return props.order.payment_request_status === 'Draft' || props.order.payment_request_status === 'Requested'
  }
  return false
})

const isApproved = computed(() => {
  // Logic: Payment Approved / Processing
  if (['Transfer Manual', 'Cash Webshop'].includes(props.order.payment_method_type || '')) {
    return props.order.payment_request_status === 'Submitted' || ['To Deliver', 'Processing', 'Shipped', 'Completed'].includes(getDisplayStatus(props.order))
  }
  // Payment Gateway: Auto approved if status is Processing/To Deliver
  return ['To Deliver', 'Processing', 'Shipped', 'Completed'].includes(getDisplayStatus(props.order))
})

// Check eligibility when component mounts (if modal is open)
onMounted(() => {
  console.log('Component mounted, isOpen:', props.isOpen, 'order:', props.order?.name)
  if (props.isOpen && props.order?.name) {
    checkReturnEligibility()
  }
})

// Check order return eligibility via API
const checkReturnEligibility = async () => {
  console.log('Checking return eligibility for order:', props.order)
  if (!props.order?.name) {
    isEligibleForReturn.value = false
    return
  }

  try {
    const response = await call('webshop.webshop.api.returns.check_order_return_eligibility', {
      sales_order: props.order.name
    })

    if (response) {
      isEligibleForReturn.value = response.eligible || false
    } else {
      isEligibleForReturn.value = false
    }
  } catch (error) {
    console.error('Error checking return eligibility:', error)
    isEligibleForReturn.value = false
  }
}

// Check if return can be requested for this order
const canRequestReturn = computed(() => {
  if (!props.order) return false

  // Check if order is completed/delivered
  const eligibleStatuses = ['Completed', 'Delivered', 'To Bill', 'To Deliver']
  const hasEligibleStatus = eligibleStatuses.includes(getDisplayStatus(props.order))

  // Must have eligible status AND be confirmed eligible by API
  return hasEligibleStatus && isEligibleForReturn.value === true
})


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

// Get status label in Indonesian - same as OrderCard.vue
const getStatusLabel = (status: string) => {
  if (isWaitingApproval.value) {
    return 'Menunggu Verifikasi'
  }
  if (isWaitingPayment.value) {
    return 'Menunggu Pembayaran'
  }

  // Standard mapping
  const statusMap: Record<string, string> = {
    'To Deliver and Bill': 'Menunggu Pembayaran',
    'To Pay': 'Menunggu Pembayaran',
    'Pending Payment': 'Menunggu Pembayaran',
    'To Deliver': 'Pesanan Diproses',
    'Processing': 'Pesanan Diproses',
    'Shipped': 'Pesanan Dikirim',
    'Completed': 'Selesai',
    'Cancelled': 'Dibatalkan',
    'Canceled': 'Dibatalkan',
    'Overdue': 'Menunggu Pembayaran'
  }
  return statusMap[status] || status
}

// Status badge class - same as OrderCard.vue
const statusBadgeClass = computed(() => {
  if (isWaitingApproval.value) {
    return 'bg-[#e6f7ff] text-[#1890ff]' // Figma Blue
  }
  if (isWaitingPayment.value) {
    return 'bg-[#fff7e6] text-[#faad14]' // Figma Orange
  }
  if (getDisplayStatus(props.order) === 'Completed' || getDisplayStatus(props.order) === 'Shipped') {
    return 'bg-[#e6fffa] text-[#007f62]' // Figma Green
  }
  if (getDisplayStatus(props.order) === 'Cancelled' || getDisplayStatus(props.order) === 'Canceled') {
    return 'bg-red-50 text-red-600'
  }
  // Default / Processing
  return 'bg-blue-50 text-blue-600'
})

// Get status dot color class - updated to match statusBadgeClass
const getStatusDotClass = (status: string) => {
  if (isWaitingApproval.value) {
    return 'bg-[#1890ff]' // Figma Blue
  }
  if (isWaitingPayment.value) {
    return 'bg-[#faad14]' // Figma Orange
  }
  if (status === 'Completed' || status === 'Shipped') {
    return 'bg-[#007f62]' // Figma Green
  }
  if (status === 'Cancelled' || status === 'Canceled') {
    return 'bg-red-600'
  }
  // Default / Processing
  return 'bg-blue-600'
}

// Get status text color class - updated to match statusBadgeClass
const getStatusTextClass = (status: string) => {
  if (isWaitingApproval.value) {
    return 'text-[#1890ff]' // Figma Blue
  }
  if (isWaitingPayment.value) {
    return 'text-[#faad14]' // Figma Orange
  }
  if (status === 'Completed' || status === 'Shipped') {
    return 'text-[#007f62]' // Figma Green
  }
  if (status === 'Cancelled' || status === 'Canceled') {
    return 'text-red-600'
  }
  // Default / Processing
  return 'text-blue-600'
}

// // Calculate installment amount (example: 1/3 of total)
// const calculateInstallmentAmount = () => {
//   return Math.ceil(props.order.grand_total / 3)
// }

// Handle back to payment method
const handleBackToPaymentMethod = () => {
  emit('backToPaymentMethod', props.order.name)
}

// Prevent body scroll when modal is open and check return eligibility
watch(
  () => [props.isOpen, props.order] as const,
  ([isOpen, order]) => {
    console.log('Watch fired - isOpen:', isOpen, 'Order:', order?.name)
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      // Check return eligibility when modal opens or order changes
      if (order?.name) {
        checkReturnEligibility()
      }
    } else {
      document.body.style.overflow = ''
      // Reset eligibility when modal closes
      isEligibleForReturn.value = null
    }
  }
)

// Open image in new tab
const openImage = (url: string) => {
  window.open(url, '_blank')
}

// Return request functions
const openReturnModal = () => {
  isReturnModalOpen.value = true
}

const closeReturnModal = () => {
  isReturnModalOpen.value = false
}

const navigateToReturnWizard = () => {
  isReturnModalOpen.value = false
  emit('close') // Close the order detail modal first
  router.push(`/order/${props.order.name}/return`)
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
