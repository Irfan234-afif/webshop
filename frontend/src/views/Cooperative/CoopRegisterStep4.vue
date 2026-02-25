<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <button @click="handleBack" class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 class="text-2xl font-bold text-gray-900">Metode Pembayaran (4/5)</h2>
      </div>
      <p class="text-gray-600">
        Pilih metode pembayaran untuk biaya pendaftaran anggota koperasi.
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 80%"></div>
      </div>
    </div>

    <!-- Fee Summary -->
    <div class="bg-purple-50 rounded-xl p-6 mb-8 border border-purple-100">
      <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Rincian Biaya
      </h3>
      <div class="space-y-3">
        <div class="flex justify-between items-center pb-3 border-b border-purple-200">
          <span class="text-gray-600">Simpanan Pokok</span>
          <span class="font-medium">{{ formatCurrency(cooperativeStore.settings?.principal_saving_amount || 0) }}</span>
        </div>
        <div class="flex justify-between items-center pb-3 border-b border-purple-200">
          <span class="text-gray-600">Simpanan Wajib (Bulan Pertama)</span>
          <span class="font-medium">{{ formatCurrency(cooperativeStore.settings?.mandatory_saving_amount || 0) }}</span>
        </div>
        <div class="flex justify-between items-center pt-2">
          <span class="font-bold text-gray-900">Total Pembayaran</span>
          <span class="text-xl font-bold text-primary">{{ formatCurrency(cooperativeStore.settings?.total_registration_amount || 0) }}</span>
        </div>
      </div>
    </div>

    <!-- Payment Selector Component -->
    <div class="mb-8">
      <CoopPaymentMethodSelector ref="paymentMethodSelectorRef" />
    </div>

    <!-- Actions -->
    <div class="flex gap-4">
      <button type="button" @click="handleBack"
        class="flex-1 bg-white border-2 border-gray-200 text-gray-700 font-bold py-4 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors">
        Kembali
      </button>
      <button type="button" @click="handleNext" :disabled="!isStep4Valid"
        class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        Lanjut
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useCooperativeStore } from '@/stores/cooperative'
import CoopPaymentMethodSelector from './components/CoopPaymentMethodSelector.vue'

const cooperativeStore = useCooperativeStore()
const isStep4Valid = computed(() => cooperativeStore.isStep4Valid)
const paymentMethodSelectorRef = ref<InstanceType<typeof CoopPaymentMethodSelector> | null>(null)

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

const handleNext = () => {
  const isChannelRequired = paymentMethodSelectorRef.value?.isChannelRequired
  
  if (isChannelRequired) {
    // Cannot proceed if channel is required but not selected
    return
  }

  if (isStep4Valid.value) {
    cooperativeStore.nextStep()
  }
}

const handleBack = () => {
  cooperativeStore.prevStep()
}
</script>
