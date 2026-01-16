<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CartItem } from '@/types/cart'
import { applyCouponCode, removeCouponCode } from '@/utils/cartApi'
import { useCartStore } from '@/stores/cart'
import { useAlertStore } from '@/stores/alert'
import { extractErrorMessage } from '@/utils/errorHandler'

interface Props {
  items: CartItem[]
  quotationName?: string  // For remove coupon API call
  couponCode?: string     // Applied coupon code
  discountAmount?: number // Discount from coupon
  originalTotal?: number  // Total before discount
}

const props = defineProps<Props>()

const emit = defineEmits<{
  checkout: []
}>()

const cartStore = useCartStore()
const alertStore = useAlertStore()

// Voucher state
const voucherCode = ref('')
const isDetailsExpanded = ref(true)
const isApplyingVoucher = ref(false)

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}

const subtotal = computed(() => {
  // Use original_total if available (price before coupon discount)
  // Otherwise calculate from items
  if (props.originalTotal !== undefined && props.originalTotal > 0) {
    return props.originalTotal
  }
  return props.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

// Coupon discount from props
const couponDiscount = computed(() => {
  return props.discountAmount || 0
})

const total = computed(() => {
  return subtotal.value - couponDiscount.value
})

// Check if coupon is applied
const hasAppliedCoupon = computed(() => {
  return !!(props.couponCode && props.couponCode.trim())
})

const handleApplyVoucher = async () => {
  if (!voucherCode.value || !voucherCode.value.trim()) {
    alertStore.warning('Silakan masukkan kode voucher', 'Peringatan')
    return
  }

  isApplyingVoucher.value = true

  try {
    await applyCouponCode(voucherCode.value.trim(), cartStore.selectedStudentCart!.quotation_name)

    // Refresh cart data after applying coupon
    await cartStore.fetchAllStudentCarts()

    alertStore.success('Voucher berhasil diterapkan!', 'Berhasil')
    voucherCode.value = ''
  } catch (error: any) {
    console.error('Error applying voucher:', error)

    // Extract error message from Frappe response
    const errorMessage = extractErrorMessage(error)
    alertStore.error(errorMessage, 'Gagal')
  } finally {
    isApplyingVoucher.value = false
  }
}

const handleRemoveCoupon = async () => {
  isApplyingVoucher.value = true

  try {
    await removeCouponCode(cartStore.selectedStudentCart!.quotation_name)

    // Refresh cart data after removing coupon
    await cartStore.fetchAllStudentCarts()

    alertStore.success('Voucher berhasil dihapus!', 'Berhasil')
  } catch (error: any) {
    console.error('Error removing voucher:', error)

    const errorMessage = extractErrorMessage(error)
    alertStore.error(errorMessage, 'Gagal')
  } finally {
    isApplyingVoucher.value = false
  }
}

const handleCheckout = () => {
  emit('checkout')
}

const toggleDetails = () => {
  isDetailsExpanded.value = !isDetailsExpanded.value
}
</script>

<template>
  <div class="flex flex-col gap-4 sticky top-6">
    <div class="">
      <!-- Voucher Section -->
      <div class="bg-mute border-t-[1.5px] border-x-[1.5px] border-border rounded-t-xl p-4 sm:p-6 lg:p-8">
        <!-- Applied Coupon Display -->
        <div v-if="hasAppliedCoupon"
          class="bg-green-50 border border-green-200 flex items-center gap-3 min-h-[48px] sm:min-h-[54px] lg:min-h-[58px] rounded-full px-4 sm:px-5 lg:px-6">
          <!-- Voucher Icon -->
          <div class="w-5 h-5 sm:w-6 sm:h-6 flex-shrink-0">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
              class="w-full h-full">
              <path
                d="M14.005 4H9.99502C6.21439 4 4.32407 4 3.14958 5.17157C2.34091 5.97823 2.08903 7.12339 2.01058 8.98947C1.99502 9.35954 1.98724 9.54458 2.05634 9.66802C2.12545 9.79147 2.40133 9.94554 2.95308 10.2537C3.56586 10.5959 3.98007 11.2497 3.98007 12C3.98007 12.7503 3.56586 13.4041 2.95308 13.7463C2.40133 14.0545 2.12545 14.2085 2.05634 14.332C1.98724 14.4554 1.99502 14.6405 2.01058 15.0105C2.08903 16.8766 2.34091 18.0218 3.14958 18.8284C4.32407 20 6.21439 20 9.99502 20H14.005C17.7856 20 19.6759 20 20.8504 18.8284C21.6591 18.0218 21.911 16.8766 21.9894 15.0105C22.005 14.6405 22.0128 14.4554 21.9437 14.332C21.8746 14.2085 21.5987 14.0545 21.0469 13.7463C20.4341 13.4041 20.0199 12.7503 20.0199 12C20.0199 11.2497 20.4341 10.5959 21.0469 10.2537C21.5987 9.94554 21.8746 9.79147 21.9437 9.66803C22.0128 9.54458 22.005 9.35954 21.9894 8.98947C21.911 7.12339 21.6591 5.97823 20.8504 5.17157C19.6759 4 17.7856 4 14.005 4Z"
                stroke="#059669" stroke-width="2" />
              <path d="M9 15L15 9" stroke="#059669" stroke-width="2" stroke-linecap="round" />
              <path
                d="M15.5 14.5C15.5 15.0523 15.0523 15.5 14.5 15.5C13.9477 15.5 13.5 15.0523 13.5 14.5C13.5 13.9477 13.9477 13.5 14.5 13.5C15.0523 13.5 15.5 13.9477 15.5 14.5Z"
                fill="#059669" />
              <path
                d="M10.5 9.5C10.5 10.0523 10.0523 10.5 9.5 10.5C8.94772 10.5 8.5 10.0523 8.5 9.5C8.5 8.94772 8.94772 8.5 9.5 8.5C10.0523 8.5 10.5 8.94772 10.5 9.5Z"
                fill="#059669" />
            </svg>
          </div>

          <!-- Applied Coupon Code -->
          <div class="flex-1 min-w-0">
            <p class="text-xs text-green-600 font-medium">Kode Voucher Diterapkan</p>
            <p class="text-sm font-bold text-green-700 truncate">{{ couponCode }}</p>
          </div>

          <!-- Remove Button -->
          <button @click="handleRemoveCoupon" :disabled="isApplyingVoucher"
            class="flex-shrink-0 text-red-500 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors p-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Voucher Input (when no coupon applied) -->
        <div v-else
          class="bg-white flex items-center gap-2 sm:gap-3 min-h-[48px] sm:min-h-[54px] lg:min-h-[58px] rounded-full pl-3 sm:pl-4 lg:pl-6">
          <!-- Voucher Icon -->
          <div class="w-5 h-5 sm:w-6 sm:h-6 flex-shrink-0">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
              class="w-full h-full">
              <path
                d="M14.005 4H9.99502C6.21439 4 4.32407 4 3.14958 5.17157C2.34091 5.97823 2.08903 7.12339 2.01058 8.98947C1.99502 9.35954 1.98724 9.54458 2.05634 9.66802C2.12545 9.79147 2.40133 9.94554 2.95308 10.2537C3.56586 10.5959 3.98007 11.2497 3.98007 12C3.98007 12.7503 3.56586 13.4041 2.95308 13.7463C2.40133 14.0545 2.12545 14.2085 2.05634 14.332C1.98724 14.4554 1.99502 14.6405 2.01058 15.0105C2.08903 16.8766 2.34091 18.0218 3.14958 18.8284C4.32407 20 6.21439 20 9.99502 20H14.005C17.7856 20 19.6759 20 20.8504 18.8284C21.6591 18.0218 21.911 16.8766 21.9894 15.0105C22.005 14.6405 22.0128 14.4554 21.9437 14.332C21.8746 14.2085 21.5987 14.0545 21.0469 13.7463C20.4341 13.4041 20.0199 12.7503 20.0199 12C20.0199 11.2497 20.4341 10.5959 21.0469 10.2537C21.5987 9.94554 21.8746 9.79147 21.9437 9.66803C22.0128 9.54458 22.005 9.35954 21.9894 8.98947C21.911 7.12339 21.6591 5.97823 20.8504 5.17157C19.6759 4 17.7856 4 14.005 4Z"
                stroke="#AC208E" stroke-width="2" />
              <path d="M9 15L15 9" stroke="#AC208E" stroke-width="2" stroke-linecap="round" />
              <path
                d="M15.5 14.5C15.5 15.0523 15.0523 15.5 14.5 15.5C13.9477 15.5 13.5 15.0523 13.5 14.5C13.5 13.9477 13.9477 13.5 14.5 13.5C15.0523 13.5 15.5 13.9477 15.5 14.5Z"
                fill="#AC208E" />
              <path
                d="M10.5 9.5C10.5 10.0523 10.0523 10.5 9.5 10.5C8.94772 10.5 8.5 10.0523 8.5 9.5C8.5 8.94772 8.94772 8.5 9.5 8.5C10.0523 8.5 10.5 8.94772 10.5 9.5Z"
                fill="#AC208E" />
            </svg>
          </div>

          <!-- Voucher Input -->
          <input v-model="voucherCode" type="text" placeholder="Kode Voucher"
            class="flex-1 min-w-0 px-2 sm:px-3 lg:px-4 bg-transparent border-none outline-none focus:ring-0 text-sm sm:text-md font-medium placeholder:text-text-secondary truncate" />

          <!-- Apply Button -->
          <button @click="handleApplyVoucher" :disabled="isApplyingVoucher"
            class="bg-primary flex-shrink-0 self-stretch px-5 lg:px-7 rounded-full text-white font-bold text-xs sm:text-sm capitalize hover:bg-secondary-alt transition-colors whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isApplyingVoucher ? 'Memproses...' : 'Gunakan' }}
          </button>
        </div>
      </div>

      <!-- Bill Details Section -->
      <div class="bg-mute border-[1.5px] border-border rounded-b-xl p-8 flex flex-col gap-8">
        <!-- Details Header -->
        <button @click="toggleDetails" class="flex items-center justify-between w-full">
          <h2 class="text-lg font-bold text-text capitalize">
            Rincian Tagihan
          </h2>
          <svg class="w-3 h-1.5 transition-transform" :class="{ 'rotate-180': !isDetailsExpanded }" viewBox="0 0 11 6"
            fill="none">
            <path d="M1 1L5.5 5L10 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
              stroke-linejoin="round" />
          </svg>
        </button>

        <!-- Items List -->
        <div v-if="isDetailsExpanded" class="flex flex-col gap-6">
          <div v-for="item in items" :key="item.id"
            class="flex items-start justify-between gap-4 font-semibold text-sm text-text-secondary">
            <p class="flex-1 min-w-0 overflow-hidden line-clamp-2">{{ item.title }}</p>
            <p class="flex-shrink-0 text-right whitespace-nowrap">
              {{ formatCurrency(item.price * item.quantity) }}
            </p>
          </div>

          <!-- Coupon Discount Row (only if coupon applied) -->
          <div v-if="hasAppliedCoupon && couponDiscount > 0"
            class="flex items-center justify-between font-semibold text-sm text-red-600">
            <p class="overflow-hidden overflow-ellipsis">Diskon Voucher</p>
            <p class="overflow-hidden overflow-ellipsis text-right">- {{ formatCurrency(couponDiscount) }}</p>
          </div>

          <!-- Member Discount Row -->
          <!-- <div class="flex items-center justify-between font-semibold text-sm">
            <p class="overflow-hidden overflow-ellipsis text-text-secondary">Diskon Anggota Koperasi</p>
            <p class="overflow-hidden overflow-ellipsis text-right text-[#f92d46]">
              - {{ formatCurrency(memberDiscount) }}
            </p>
          </div> -->
        </div>
      </div>
    </div>

    <!-- Total Section -->
    <div class="bg-mute border-[1.5px] border-border rounded-xl p-8 flex flex-col gap-8">
      <div class="flex flex-col gap-6 py-1.5">
        <p class="text-base font-bold text-text text-start capitalize">
          Total Tagihan
        </p>
        <div class="flex flex-col gap-4">
          <p class="text-2xl font-bold text-primary text-start capitalize">
            {{ formatCurrency(total) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Checkout Button -->
    <button @click="handleCheckout" :disabled="items.length === 0"
      class="bg-primary text-white font-bold py-4 px-8 h-[58px] rounded-xl hover:bg-secondary-alt disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-3 capitalize text-sm">
      Buat Pesanan
    </button>
  </div>
</template>

<style scoped>
.rotate-180 {
  transform: rotate(180deg);
}
</style>
