<script setup lang="ts">
import { ref, computed } from 'vue'
import type { CartItem } from '@/types/cart'

interface Props {
  items: CartItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  checkout: []
}>()

// Voucher state
const voucherCode = ref('')
const isDetailsExpanded = ref(true)

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}

const subtotal = computed(() => {
  return props.items.reduce((sum, item) => sum + item.price * item.quantity, 0)
})

// Mock values for voucher and discount
const voucherDiscount = ref(0)
// const memberDiscount = ref(100000)

const total = computed(() => {
  return subtotal.value - voucherDiscount.value
})

const handleApplyVoucher = () => {
  // TODO: Implement voucher application
  console.log('Applying voucher:', voucherCode.value)
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
      <div class="bg-mute border-t-[1.5px] border-x-[1.5px] border-border rounded-t-xl p-8">
        <div class="bg-white flex items-center justify-between h-[58px] rounded-full pl-6 pr-0 py-3">
          <!-- Voucher Icon -->
          <div class="w-6 h-6 flex-shrink-0">
            <svg class="w-full h-full text-primary" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9 12h6m-6 4h6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- Voucher Input -->
          <input
            v-model="voucherCode"
            type="text"
            placeholder="Masukan Kode Voucher"
            class="flex-1 px-4 bg-transparent border-none outline-none text-sm font-medium text-text-secondary placeholder:text-text-secondary capitalize"
          />

          <!-- Apply Button -->
          <button
            @click="handleApplyVoucher"
            class="bg-primary h-[58px] px-7 py-3.5 rounded-full text-white font-bold text-sm capitalize hover:bg-secondary-alt transition-colors"
          >
            Gunakan
          </button>
        </div>
      </div>

      <!-- Bill Details Section -->
      <div class="bg-mute border-[1.5px] border-border rounded-b-xl p-8 flex flex-col gap-8">
        <!-- Details Header -->
        <button
          @click="toggleDetails"
          class="flex items-center justify-between w-full"
        >
          <h2
            class="text-lg font-bold text-text capitalize"
          >
            Rincian Tagihan
          </h2>
          <svg
            class="w-3 h-1.5 transition-transform"
            :class="{ 'rotate-180': !isDetailsExpanded }"
            viewBox="0 0 11 6"
            fill="none"
          >
            <path d="M1 1L5.5 5L10 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- Items List -->
        <div v-if="isDetailsExpanded" class="flex flex-col gap-6">
          <div
            v-for="item in items"
            :key="item.id"
            class="flex items-center justify-between font-semibold text-sm text-text-secondary"
          >
            <p class="overflow-hidden overflow-ellipsis">{{ item.title }}</p>
            <p class="overflow-hidden overflow-ellipsis text-right">
              {{ formatCurrency(item.price * item.quantity) }}
            </p>
          </div>

          <!-- Voucher Row -->
          <div class="flex items-center justify-between font-semibold text-sm text-text-secondary">
            <p class="overflow-hidden overflow-ellipsis">Voucher</p>
            <p class="overflow-hidden overflow-ellipsis text-right">{{ voucherDiscount }}</p>
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
        <p
          class="text-base font-bold text-text text-start capitalize"
        >
          Total Tagihan
        </p>
        <div class="flex flex-col gap-4">
          <p
            class="text-2xl font-bold text-primary text-start capitalize"
          >
            {{ formatCurrency(total) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Checkout Button -->
    <button
      @click="handleCheckout"
      :disabled="items.length === 0"
      class="bg-primary text-white font-bold py-4 px-8 h-[58px] rounded-xl hover:bg-secondary-alt disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-3 capitalize text-sm"
    >
      Buat Pesanan
    </button>
  </div>
</template>

<style scoped>
.rotate-180 {
  transform: rotate(180deg);
}
</style>
