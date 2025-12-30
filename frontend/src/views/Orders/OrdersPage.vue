<template>
  <DefaultLayout>
    <Container class="py-6">
      <!-- Breadcrumb -->
      <Breadcrumb :items="[
        { label: 'Home', to: '/' },
        { label: 'Pesanan & Riwayat Belanja' }
      ]" class="mb-6" />

      <!-- Page Title -->
      <h1 class="text-xl font-bold text-gray-900 mb-10">Pesanan & Riwayat Belanja</h1>

      <!-- Tab Navigation -->
      <div class="flex gap-6 mb-8 border-b border-gray-200">
        <button @click="activeTab = 'orders'" :class="[
          'pb-3 text-lg font-medium transition-colors relative',
          activeTab === 'orders'
            ? 'text-gray-900'
            : 'text-gray-500 hover:text-gray-700'
        ]">
          Pesanan
          <div v-if="activeTab === 'orders'"
            class="absolute bottom-0 left-0 right-0 h-[3px] bg-primary rounded-t-full" />
        </button>
        <button @click="activeTab = 'history'" :class="[
          'pb-3 text-lg font-medium transition-colors relative',
          activeTab === 'history'
            ? 'text-gray-900'
            : 'text-gray-500 hover:text-gray-700'
        ]">
          Riwayat
          <div v-if="activeTab === 'history'"
            class="absolute bottom-0 left-0 right-0 h-[3px] bg-primary rounded-t-full" />
        </button>
        <button @click="activeTab = 'subscriptions'" :class="[
          'pb-3 text-lg font-medium transition-colors relative',
          activeTab === 'subscriptions'
            ? 'text-gray-900'
            : 'text-gray-500 hover:text-gray-700'
        ]">
          Langganan
          <div v-if="activeTab === 'subscriptions'"
            class="absolute bottom-0 left-0 right-0 h-[3px] bg-primary rounded-t-full" />
        </button>
      </div>

      <!-- Filters (Visible for both tabs) -->
      <div
        class="mb-8 p-4 bg-gray-50 rounded-xl border border-gray-100 flex flex-wrap gap-4 items-center justify-between">
        <div class="flex flex-wrap gap-4 items-center w-full lg:w-auto">
          <!-- Student Filter -->
          <div
            class="relative min-w-[200px] bg-white border border-gray-200 rounded-lg px-3 py-2 flex items-center gap-3">
            <span class="text-xs text-gray-500 font-medium">Nama Siswa :</span>
            <select v-model="filters.student"
              class="appearance-none bg-transparent font-bold text-gray-900 text-sm focus:outline-none w-full pr-6 cursor-pointer">
              <option value="">Semua</option>
              <option v-for="student in studentsResource.data" :key="student" :value="student.name">
                {{ student.student_name }}
              </option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1L5 5L9 1" stroke="#9CA3AF" stroke-width="1.5" stroke-linecap="round"
                  stroke-linejoin="round" />
              </svg>
            </div>
          </div>

          <!-- Status Filter -->
          <div v-if="activeTab === 'orders'"
            class="relative min-w-[200px] bg-white border border-gray-200 rounded-lg px-3 py-2 flex items-center gap-3">
            <span class="text-xs text-gray-500 font-medium">Status Pesanan :</span>
            <select v-model="filters.status"
              class="appearance-none bg-transparent font-bold text-gray-900 text-sm focus:outline-none w-full pr-6 cursor-pointer">
              <option value="">Semua</option>
              <option value="To Deliver and Bill">Menunggu Pembayaran</option>
              <option value="To Deliver">Pesanan Diproses</option>
              <option value="Processing">Pesanan Diproses</option>
              <option value="Shipped">Pesanan Dikirim</option>
              <option value="Completed">Selesai</option>
              <option value="Cancelled">Dibatalkan</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
              <svg width="10" height="6" viewBox="0 0 10 6" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M1 1L5 5L9 1" stroke="#9CA3AF" stroke-width="1.5" stroke-linecap="round"
                  stroke-linejoin="round" />
              </svg>
            </div>
          </div>
        </div>

        <!-- Search -->
        <div class="relative w-full lg:w-72">
          <input v-model="filters.search" type="text" placeholder="Cari pesanan..."
            class="w-full bg-white border border-gray-200 rounded-lg pl-10 pr-4 py-2.5 text-sm focus:outline-none focus:border-primary transition-colors" />
          <div class="absolute left-3 top-1/2 -translate-y-1/2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z"
                stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Orders Tabs -->
      <OrdersTab v-if="activeTab === 'orders'" :orders="orders" :loading="ordersResource.loading"
        @view-order="viewOrder" />

      <HistoryTab v-if="activeTab === 'history'" :orders="orders" :loading="ordersResource.loading"
        @view-order="viewOrder" />

      <SubscriptionTab v-if="activeTab === 'subscriptions'" :subscriptions="subscriptions"
        :loading="subscriptionsResource.loading" @view-subscription="viewSubscription" />

      <!-- Infinite Scroll Trigger -->
      <div ref="infiniteScrollTrigger" class="flex justify-center p-6 h-20 opacity-0">
        <div v-if="ordersResource.loading || subscriptionsResource.loading"
          class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary opacity-100"></div>
      </div>

      <!-- Promotional Banner -->
      <div class="relative bg-gradient-to-r from-purple-700 to-purple-900 rounded-2xl overflow-hidden mb-12">
        <div class="relative z-10 px-8 py-12 md:py-16">
          <h2 class="text-2xl md:text-3xl font-bold text-white mb-4">
            Persiapan Tahun Ajaran Baru 2025/2026
          </h2>
          <p class="text-purple-100 mb-6 max-w-2xl">
            Lengkapi seragam baru dan perlengkapan sekolah. Belanja mudah, lengkap dan nyaman dengan
            berbagai pilihan ukuran dan warna yang tersedia!
          </p>
          <RouterLink to="/products"
            class="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-purple-900 font-semibold px-6 py-3 rounded-lg transition-colors">
            Mulai Belanja
            <ArrowRightIcon :size="20" />
          </RouterLink>
        </div>
        <!-- Decorative Image -->
        <div class="absolute right-0 top-0 bottom-0 w-1/2 opacity-20 hidden md:block">
          <div class="absolute inset-0 bg-gradient-to-l from-transparent to-purple-900" />
        </div>
      </div>

      <!-- Order Detail Modal -->
      <OrderDetailModal v-if="selectedOrder" :is-open="isModalOpen" :order="selectedOrder" @close="closeModal"
        @pay-order="handlePayOrder" @back-to-payment-method="handleBackToPaymentMethod" />

      <!-- Subscription Detail Modal -->
      <SubscriptionDetailModal v-if="selectedSubscription" :is-open="isSubscriptionModalOpen"
        :subscription="selectedSubscription" @close="closeSubscriptionModal" />
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, reactive, watch, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { formatIDR } from '@/utils/formatters'
import { createResource, debounce, createListResource } from 'frappe-ui'
import Container from '@/components/layout/Container.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'
import ArrowRightIcon from '@/components/icons/ArrowRightIcon.vue'
import OrderDetailModal from '@/components/features/orders/OrderDetailModal.vue'
import OrdersTab from '@/components/features/orders/OrdersTab.vue'
import HistoryTab from '@/components/features/orders/HistoryTab.vue'
import SubscriptionTab from '@/components/features/orders/SubscriptionTab.vue'
import SubscriptionDetailModal from '@/components/features/orders/SubscriptionDetailModal.vue'
import type { Order, SubscriptionItem } from '@/types/order'
import { useAuthStore } from '@/stores/auth'

const activeTab = ref<'orders' | 'history' | 'subscriptions'>('orders')
const isModalOpen = ref(false)
const isSubscriptionModalOpen = ref(false)
const selectedOrder = ref<Order | null>(null)
const selectedSubscription = ref<SubscriptionItem | null>(null)
const orders = ref<Order[]>([])
const subscriptions = ref<SubscriptionItem[]>([])
const hasMore = ref(true)
const hasMoreSubscriptions = ref(true)
const infiniteScrollTrigger = ref<HTMLElement | null>(null)

const authStore = useAuthStore()

// Filters state
const filters = reactive({
  student: '',
  status: '',
  search: ''
})

// Pagination state
const pagination = reactive({
  start: 0,
  pageLength: 10
})

const paginationSubscriptions = reactive({
  start: 0,
  pageLength: 10
})

// Filter Options Resource
// const filterOptionsResource = createResource({
//   url: 'webshop.webshop.api.orders.get_order_filter_options',
//   auto: true
// })

const studentsResource = createListResource({
  doctype: 'Student',
  fields: ['name', 'student_name'],
  filters: {
    customer: authStore.customer?.name
  },
  orderBy: 'creation desc',
  start: 0,
  pageLength: 5,
  auto: false
})

watch(() => authStore.customer, (newCustomer) => {
  if (newCustomer?.name) {
    studentsResource.update({
      filters: {
        customer: newCustomer.name
      }
    })
    studentsResource.reload()
  }
}, { immediate: true })

// Orders Resource
const ordersResource = createResource({
  url: 'webshop.webshop.api.orders.get_orders',
  auto: false,
  onSuccess: (data: any) => {
    const newOrders = data.orders || []
    if (pagination.start === 0) {
      orders.value = newOrders
    } else {
      orders.value = [...orders.value, ...newOrders]
    }

    // Increment for next page
    pagination.start += pagination.pageLength

    if (newOrders.length < pagination.pageLength) {
      hasMore.value = false
    } else {
      hasMore.value = true
    }
  }
})

// Subscriptions Resource
const subscriptionsResource = createResource({
  url: 'webshop.webshop.api.subscriptions.get_subscriptions',
  auto: false,
  onSuccess: (data: any) => {
    const newSubscriptions = data.subscriptions || []
    if (paginationSubscriptions.start === 0) {
      subscriptions.value = newSubscriptions
    } else {
      subscriptions.value = [...subscriptions.value, ...newSubscriptions]
    }

    // Increment for next page
    paginationSubscriptions.start += paginationSubscriptions.pageLength

    if (newSubscriptions.length < paginationSubscriptions.pageLength) {
      hasMoreSubscriptions.value = false
    } else {
      hasMoreSubscriptions.value = true
    }
  }
})

// Unique Students from Backend
// const uniqueStudents = computed(() => {
//   return studentsResource.data || []
// })


// Fetch orders
const fetchOrders = async (reset = false) => {
  if (reset) {
    pagination.start = 0
    hasMore.value = true
    // orders.value = [] // Optional: clear immediately or wait for response
  }

  if (!hasMore.value && !reset) return

  ordersResource.fetch({
    search_text: filters.search,
    student: filters.student,
    status: filters.status,
    tab: activeTab.value,
    start: pagination.start,
    page_length: pagination.pageLength
  })
}

// Fetch subscriptions
const fetchSubscriptions = async (reset = false) => {
  if (reset) {
    paginationSubscriptions.start = 0
    hasMoreSubscriptions.value = true
  }

  if (!hasMoreSubscriptions.value && !reset) return

  subscriptionsResource.fetch({
    student: filters.student,
    start: paginationSubscriptions.start,
    page_length: paginationSubscriptions.pageLength
  })
}

// Watchers
watch(activeTab, () => {
  filters.status = '' // Reset status filter when switching tabs
  if (activeTab.value === 'subscriptions') {
    fetchSubscriptions(true)
  } else {
    fetchOrders(true)
  }
})

watch(
  () => [filters.status, filters.student, filters.search],
  debounce(() => {
    if (activeTab.value === 'subscriptions') {
      fetchSubscriptions(true)
    } else {
      fetchOrders(true)
    }
  }, 500)
)

// Infinite Scroll Observer
let observer: IntersectionObserver | null = null

const setupIntersectionObserver = () => {
  if (observer) observer.disconnect()

  observer = new IntersectionObserver((entries) => {
    if (entries && entries.length > 0) {
      const target = entries[0]
      if (activeTab.value === 'subscriptions') {
        if (target && target.isIntersecting && hasMoreSubscriptions.value && !subscriptionsResource.loading) {
          fetchSubscriptions(false)
        }
      } else {
        if (target && target.isIntersecting && hasMore.value && !ordersResource.loading) {
          fetchOrders(false)
        }
      }
    }
  }, {
    root: null,
    rootMargin: '100px',
    threshold: 0.1
  })

  if (infiniteScrollTrigger.value) {
    observer.observe(infiniteScrollTrigger.value)
  }
}

onMounted(() => {
  // initial fetch is handled by watch(activeTab) if we trigger it, or explicit call? 
  // activeTab is 'orders' by default. 
  // Let's call explicitly to be safe, or just let the component lifecycle handle it.
  fetchOrders(true)
  nextTick(() => {
    setupIntersectionObserver()
  })
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

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case 'Completed':
    case 'Shipped':
      return 'bg-green-100 text-green-700'
    case 'To Deliver':
    case 'Processing':
      return 'bg-blue-100 text-blue-700'
    case 'Cancelled':
    case 'Canceled':
      return 'bg-red-100 text-red-700'
    case 'Draft':
    case 'To Deliver and Bill':
    case 'Pending Payment':
      return 'bg-orange-100 text-orange-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

// Open order detail modal
const openOrderDetailModal = (order: Order) => {
  selectedOrder.value = order
  isModalOpen.value = true
}

// Close modal
const closeModal = () => {
  isModalOpen.value = false
  selectedOrder.value = null
}

// View order details
const viewOrder = (order: Order) => {
  openOrderDetailModal(order)
}

// View subscription details
const viewSubscription = (subscription: SubscriptionItem) => {
  selectedSubscription.value = subscription
  isSubscriptionModalOpen.value = true
}

// Close subscription modal
const closeSubscriptionModal = () => {
  isSubscriptionModalOpen.value = false
  selectedSubscription.value = null
}

// Pay for order (installment)
const payForOrder = (orderId: string) => {
  console.log('Pay for order:', orderId)
}

// Handle back to payment method
const handleBackToPaymentMethod = (orderId: string) => {
  console.log('Back to payment method:', orderId)
  closeModal()
}

// Handle pay order from modal
const handlePayOrder = (orderId: string) => {
  payForOrder(orderId)
  closeModal()
}
</script>
