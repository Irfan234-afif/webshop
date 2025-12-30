<template>
  <div class="container mx-auto px-4 py-8">
    <div class="mb-6">
      <button 
        @click="goBack" 
        class="flex items-center text-primary font-medium hover:text-primary-dark transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
        </svg>
        Kembali
      </button>
    </div>
    
    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>
    
    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
      <p class="text-red-700">{{ error }}</p>
    </div>
    
    <!-- Order details -->
    <div v-else-if="order" class="bg-white border border-gray-200 rounded-xl overflow-hidden">
      <div class="p-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Pesanan #{{ order.name }}</h1>
            <p class="text-gray-500">Tanggal: {{ formatDate(order.transaction_date) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <a :href="`/api/method/erpnext.accounts.doctype.payment_request.payment_request.make_payment_request?dn=${ order.name }&dt=Sales Order&submit_doc=1&order_type=Shopping Cart`"
              class="btn btn-primary btn-sm" id="pay-for-order">
              Pay
            </a>
            <span 
              class="px-3 py-1 rounded-full text-sm font-medium"
              :class="getStatusClass(order.status)"
            >
              {{ order.status }}
            </span>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-sm text-gray-500 mb-1">Total Pembayaran</p>
            <p class="text-lg font-semibold">{{ formatIDR(order.grand_total) }}</p>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-sm text-gray-500 mb-1">Siswa</p>
            <p class="text-lg font-semibold">{{ order.student_name || 'Tidak ada siswa' }}</p>
          </div>
          
          <div class="bg-gray-50 p-4 rounded-lg">
            <p class="text-sm text-gray-500 mb-1">Jenis Pesanan</p>
            <p class="text-lg font-semibold">{{ order.order_type || 'N/A' }}</p>
          </div>
        </div>
        
        <!-- Order items -->
        <div class="mb-8">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Item dalam Pesanan</h2>
          <div class="space-y-4">
            <div 
              v-for="item in order.items" 
              :key="item.item_code"
              class="flex items-center border-b border-gray-100 pb-4 last:border-0 last:pb-0"
            >
              <div class="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center mr-4">
                <img 
                  v-if="item.image" 
                  :src="item.image" 
                  :alt="item.item_name"
                  class="w-full h-full object-cover"
                >
                <div v-else class="text-gray-400">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">{{ item.item_name }}</h3>
                <p class="text-sm text-gray-500">{{ item.description }}</p>
              </div>
              
              <div class="text-right">
                <p class="font-medium">{{ formatIDR(item.rate) }}</p>
                <p class="text-sm text-gray-500">Qty: {{ item.qty }}</p>
                <p class="font-semibold mt-1">{{ formatIDR(item.amount) }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Action buttons -->
        <div class="flex flex-wrap gap-3">
          <button 
            v-if="order.status === 'Draft'"
            @click="payForOrder(order.name)"
            class="px-6 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-lg transition-colors"
          >
            Bayar Sekarang
          </button>
          
          <button 
            v-if="order.status === 'Draft'"
            @click="cancelOrder(order.name)"
            class="px-6 py-3 bg-red-50 hover:bg-red-100 text-red-700 font-semibold rounded-lg transition-colors"
          >
            Batalkan Pesanan
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { formatIDR } from '@/utils/formatters'
import { call } from 'frappe-ui'

interface OrderItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  description?: string
  image?: string
}

interface Order {
  name: string
  status: string
  transaction_date: string
  grand_total: number
  total_qty: number
  customer: string
  order_type: string
  student?: string
  student_name?: string
  items: OrderItem[]
  currency: string
}

const router = useRouter()
const route = useRoute()
const order = ref<Order | null>(null)
const isLoading = ref(true)
const error = ref<string | null>(null)

// Get order ID from route params
const orderId = computed(() => route.params.id as string)

// Fetch order details from the backend
const fetchOrderDetails = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await call('webshop.webshop.api.orders.get_order_details', {
      order_name: orderId.value
    })
    
    if (response) {
      order.value = response
    }
  } catch (err) {
    console.error('Error fetching order details:', err)
    error.value = 'Gagal memuat detail pesanan. Silakan coba lagi nanti.'
  } finally {
    isLoading.value = false
  }
}

// Format date to readable format
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Get status class for styling
const getStatusClass = (status: string) => {
  switch (status) {
    case 'Completed':
      return 'bg-green-100 text-green-800'
    case 'Pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'Cancelled':
      return 'bg-red-100 text-red-800'
    case 'Draft':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

// Go back to previous page
const goBack = () => {
  router.go(-1)
}

// Cancel order
const cancelOrder = (orderId: string) => {
  console.log('Cancel order:', orderId)
  // Implementation would go here
}

// Pay for order
const payForOrder = (orderId: string) => {
  console.log('Pay for order:', orderId)
  // Implementation would go here
}

onMounted(() => {
  fetchOrderDetails()
})
</script>