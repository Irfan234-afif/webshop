<template>
  <div class="relative bg-white rounded-2xl overflow-hidden hover:shadow-lg transition-all border group border-gray-200">
    <div class="p-5 flex flex-col h-full">
      <!-- Header: Icon, Date and ID -->
      <!-- Header: Icon, Date and ID -->
      <div class="flex gap-4 items-center mb-4">
        <div class="bg-primary/10 rounded-full w-12 h-12 flex items-center justify-center shrink-0">
          <ReceiptIcon class="w-6 h-6 text-primary" />
        </div>
        <div class="flex-1 min-w-0 flex justify-between items-start">
          <div>
             <div class="flex items-center gap-2">
                <h3 class="font-bold text-gray-900 text-base">Pesanan #{{ order.name }}</h3>
             </div>
             <p class="text-xs text-gray-500 font-semibold mt-1">{{ formatDate(order.transaction_date) }}</p>
          </div>
          <!-- Status Badge -->
          <div :class="['px-3 py-1 rounded-full flex items-center justify-center text-xs font-bold', statusBadgeClass]">
            {{ statusLabel }}
          </div>
        </div>
      </div>

      <!-- Items Section -->
      <div class="mb-4">
        <!-- Render 3 items max -->
        <div v-if="order.items && order.items.length > 0" class="space-y-3 mb-3">
          <div v-for="item in visibleItems" :key="item.item_code" class="flex gap-3">
             <div class="w-12 h-12 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 border border-gray-100 shrink-0 overflow-hidden">
                <img v-if="item.image" :src="item.image" :alt="item.item_name" class="w-full h-full object-cover" />
                <span v-else class="text-[10px]">No Img</span>
             </div>
             <div class="flex-1 min-w-0">
               <p class="text-sm font-semibold text-gray-900 line-clamp-1">{{ item.item_name }}</p>
               <p class="text-xs text-gray-500">{{ item.qty }} barang</p>
             </div>
          </div>
           <div v-if="remainingItems > 0" class="text-xs text-gray-500 pl-[60px]">
            + {{ remainingItems }} barang lainnya
          </div>
        </div>
        
        <!-- Only summary validation if needed or simplified view as in figma -->
        <!-- Logic for display depending on card type -->
      </div>
      
      <!-- Divider -->
      <div class="h-px bg-gray-100 w-full mb-4"></div>

      <!-- Footer: Total and Status/Action -->
      <div class="flex justify-between items-center gap-3">
        <div>
           <p class="text-xs text-gray-500 mb-1">Total Belanja</p>
           <p class="text-base font-bold text-gray-900">{{ formatIDR(order.grand_total) }}</p>
        </div>
        
        <!-- Action Button based on Status -->
        <button
          @click="$emit('view', order)"
          :class="['px-5 py-2.5 rounded-lg text-sm font-bold transition-colors', buttonClass]"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Order } from '@/types/order'
import { formatIDR } from '@/utils/formatters'
import ReceiptIcon from '@/components/icons/ReceiptIcon.vue'

const props = defineProps<{
  order: Order
  isHistory?: boolean
}>()

defineEmits(['view'])

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

// Item logic
const visibleItems = computed(() => {
    // We don't have items in the list view response currently! 
    // We need to fetch items or use the summary logic.
    // The current backend get_orders doesn't return items list, only summary.
    // However, Figma shows items. 
    // If we want to show items, we need to update backend to return items (at least top 3).
    // FOR NOW: I will follow the current design logic which seems to show *one* representative item or just summary info?
    // Wait, the Figma design for "Riwayat" shows "Seragam Sekolah..." text.
    // The "Pesanan" card shows "Seragam Sekolah..." text.
    // So distinct items are visible.
    // BUT `get_orders` response in `orders.py` DOES NOT include items! 
    // I missed that. I need to update `orders.py` to return items or I can't show them.
    return props.order.items?.slice(0, 2) || []
})

const remainingItems = computed(() => {
    return (props.order.items?.length || 0) - (visibleItems.value.length)
})

// Status Logic
const isWaitingPayment = computed(() => {
  // Logic: "Waiting Payment"
  // If payment method is Transfer Manual or Cash Webshop check for payment request
  // But strictly: "Waiting Payment" means you haven't paid yet.
  
  if (['Transfer Manual', 'Cash Webshop'].includes(props.order.payment_method_type || '')) {
     // If no payment request exists (or no status), it means waiting for payment/upload proof
     // If Status is "Pending Payment" or "To Deliver and Bill"
     return !props.order.payment_request_status && ['To Deliver and Bill', 'Pending Payment', 'Overdue'].includes(props.order.status)
  }
  return false
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
        return props.order.payment_request_status === 'Submitted' || ['To Deliver', 'Processing', 'Shipped', 'Completed'].includes(props.order.status)
    }
    // Payment Gateway: Auto approved if status is Processing/To Deliver
    return ['To Deliver', 'Processing', 'Shipped', 'Completed'].includes(props.order.status)
})


const buttonText = computed(() => {
    if (props.isHistory) {
        return 'Lihat Detail'
    }
    if (isWaitingPayment.value) {
        return `Bayar Pesanan`
    }
    if (isWaitingApproval.value) {
        return 'Lihat Detail' // Or specific text? Figma says "Lihat Detail" for waiting approval
    }
    if (isApproved.value) {
        return 'Lihat Detail'
    }
    if (props.order.status === 'Cancelled') {
        return 'Lihat Detail'
    }
    return 'Lihat Detail'
})

const buttonClass = computed(() => {
    if (isWaitingPayment.value) {
        return 'bg-primary text-white hover:bg-primary-dark'
    }
    // Default / History / Approved
    return 'bg-primary text-white hover:bg-primary-dark' 
})

// Status Badge Logic
const statusLabel = computed(() => {
    if (isWaitingApproval.value) {
        return 'Menunggu Verifikasi'
    }
    if (isWaitingPayment.value) {
        return 'Menunggu Pembayaran'
    }
    
    // Standard mapping
    const statusMap: Record<string, string> = {
        'To Deliver and Bill': 'Menunggu Pembayaran',
        'Pending Payment': 'Menunggu Pembayaran',
        'To Deliver': 'Pesanan Diproses',
        'Processing': 'Pesanan Diproses',
        'Shipped': 'Pesanan Dikirim',
        'Completed': 'Selesai',
        'Cancelled': 'Dibatalkan',
        'Canceled': 'Dibatalkan',
        'Overdue': 'Menunggu Pembayaran'
    }
    return statusMap[props.order.status] || props.order.status
})

const statusBadgeClass = computed(() => {
    if (isWaitingApproval.value) {
        return 'bg-[#e6f7ff] text-[#1890ff]' // Figma Blue
    }
    if (isWaitingPayment.value) {
        return 'bg-[#fff7e6] text-[#faad14]' // Figma Orange
    }
    if (props.order.status === 'Completed' || props.order.status === 'Shipped') {
        return 'bg-[#e6fffa] text-[#007f62]' // Figma Green
    }
    if (props.order.status === 'Cancelled' || props.order.status === 'Canceled') {
        return 'bg-red-50 text-red-600'
    }
    // Default / Processing
    return 'bg-blue-50 text-blue-600'
})
</script>
