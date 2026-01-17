<template>
  <DefaultLayout>
    <Container class="py-4 md:py-6 lg:py-8">
      <div class="max-w-2xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
              {{ currentStep }}
            </div>
            <h2 class="text-xl font-semibold">{{ stepTitle }}</h2>
          </div>
          <!-- Close/Cancel Button -->
          <button @click="handleClose" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Progress Bar -->
        <div class="px-6 pt-4">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-primary h-2 rounded-full transition-all duration-300" :style="{ width: progressWidth }">
            </div>
          </div>
        </div>

        <!-- Description -->
        <div class="px-6 py-4">
          <p class="text-sm text-gray-600">{{ stepDescription }}</p>
        </div>

        <!-- Content -->
        <div class="px-6 py-4 min-h-[400px]">
          <!-- Address Form (shown if no address) -->
          <AddressForm v-if="needsAddress" :student-name="studentName" @address-created="handleAddressCreated" />

          <!-- Regular checkout steps (shown if has address) -->
          <template v-else>
            <!-- Step 1: Pickup Type -->
            <PickupTypeSelector v-if="currentStep === 1" ref="pickupTypeSelectorRef" />

            <!-- Step 2: Payment Method -->
            <PaymentMethodSelector v-if="currentStep === 2" ref="paymentMethodSelectorRef" />

            <!-- Step 3: Order Confirmation -->
            <OrderConfirmation v-if="currentStep === 3" />
          </template>

          <!-- Loading State -->
          <div v-if="isLoading" class="flex items-center justify-center py-12">
            <div class="spinner"></div>
          </div>

          <!-- Error State -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
            <p class="text-red-800 text-sm">{{ error.message }}</p>
          </div>
        </div>

        <!-- Footer (hidden when showing address form) -->
        <div v-if="!needsAddress" class="border-t border-gray-200 p-6">
          <div class="flex gap-4">
            <!-- Back Button -->
            <button v-if="currentStep > 1" @click="handleBack" class="btn-secondary flex-1" :disabled="isLoading">
              {{ backButtonText }}
            </button>

            <!-- Next/Confirm Button -->
            <button @click="handleNext" class="btn-primary flex-1" :disabled="!canProceed || isLoading">
              {{ nextButtonText }}
            </button>
          </div>
        </div>
      </div>
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import PickupTypeSelector from './components/PickupTypeSelector.vue'
import PaymentMethodSelector from './components/PaymentMethodSelector.vue'
import OrderConfirmation from './components/OrderConfirmation.vue'
import AddressForm from './components/AddressForm.vue'

const router = useRouter()
const route = useRoute()

// Get student name from route query
const studentName = computed(() => route.query.student as string || '')

const checkoutStore = useCheckoutStore()
const {
  currentStep,
  isLoading,
  error,
  canProceedToStep2,
  canProceedToStep3,
  canPlaceOrder,
  checkoutData
} = storeToRefs(checkoutStore)

const needsAddress = computed(() => !checkoutData.value?.has_address)

const pickupTypeSelectorRef = ref<InstanceType<typeof PickupTypeSelector> | null>(null)
const paymentMethodSelectorRef = ref<InstanceType<typeof PaymentMethodSelector> | null>(null)

// Initialize checkout
onMounted(async () => {
  if (!studentName.value) {
    console.warn('⚠️ No student name provided, redirecting to cart')
    router.push('/cart')
    return
  }

  console.log('🔍 CheckoutPage: Initializing with student:', studentName.value)

  try {
    await checkoutStore.initializeCheckout(studentName.value)
    console.log('✅ CheckoutPage: Initialization successful')
  } catch (err) {
    console.error('❌ CheckoutPage: Initialization failed:', err)
  }

  // Load payment methods
  await checkoutStore.fetchPaymentMethods()
})

onUnmounted(() => {
  checkoutStore.resetCheckout()
})

const stepTitle = computed(() => {
  // Show address form title if address is needed
  if (needsAddress.value) {
    return 'Lengkapi Alamat Pengiriman'
  }

  const titles = {
    1: 'Pilih Jenis Pengambilan Seragam (1/3)',
    2: 'Pilih Metode Pembayaran (2/3)',
    3: 'Konfirmasi Pesanan (3/3)'
  }
  return titles[currentStep.value as keyof typeof titles] || ''
})

const stepDescription = computed(() => {
  // Show address form description if address is needed
  if (needsAddress.value) {
    return 'Sebelum melanjutkan checkout, kami memerlukan alamat pengiriman Anda untuk mengirimkan pesanan.'
  }

  const descriptions = {
    1: 'Tentukan metode pengambilan pesanan Anda, lalu pilih hari dan jam yang tersedia agar pesanan dapat diproses tepat waktu.',
    2: 'Pilih metode pembayaran yang tersedia sesuai dengan jenis produk dan status keanggotaan Anda.',
    3: 'Periksa kembali detail pesanan, metode pengambilan, dan total pembayaran sebelum menyelesaikan transaksi.'
  }
  return descriptions[currentStep.value as keyof typeof descriptions] || ''
})

const progressWidth = computed(() => {
  return `${(currentStep.value / 3) * 100}%`
})

const backButtonText = computed(() => {
  const texts = {
    2: 'Kembali',
    3: 'Kembali'
  }
  return texts[currentStep.value as keyof typeof texts] || 'Kembali'
})

const nextButtonText = computed(() => {
  const texts = {
    1: 'Pilih Metode Pembayaran',
    2: 'Konfirmasi Pesanan',
    3: `Bayar Pesanan`
  }
  return texts[currentStep.value as keyof typeof texts] || 'Selanjutnya'
})

const canProceed = computed(() => {
  if (currentStep.value === 1) {
    return canProceedToStep2.value
  } else if (currentStep.value === 2) {
    return canProceedToStep3.value
  } else if (currentStep.value === 3) {
    return canPlaceOrder.value
  }
  return false
})

function handleClose() {
  if (confirm('Apakah Anda yakin ingin membatalkan checkout?')) {
    checkoutStore.resetCheckout()
    router.push('/cart')
  }
}

function handleBack() {
  checkoutStore.previousStep()
}

async function handleAddressCreated() {
  console.log('Address created, reloading checkout data for student:', studentName.value)

  try {
    // Reload checkout data to get updated has_address status
    await checkoutStore.fetchCheckoutData(studentName.value)
  } catch (err) {
    console.error('Failed to reload checkout data:', err)
    error.value = err as Error
  }
}

async function handleNext() {
  try {
    if (currentStep.value === 1) {
      // Save pickup type (data already synced to store via watchers)
      const selectedType = checkoutStore.pickupType
      const selectedDate = checkoutStore.deliveryDate
      const selectedTime = checkoutStore.deliveryTime

      if (!selectedType || !selectedDate || !selectedTime) {
        return
      }

      // Save to backend
      await checkoutStore.setPickupType(selectedType, selectedDate, selectedTime)
      checkoutStore.nextStep()
    } else if (currentStep.value === 2) {
      // Save payment method
      const selectedMethod = paymentMethodSelectorRef.value?.selectedMethod
      if (!selectedMethod) {
        return
      }

      // Validate channel selection if required
      const isChannelRequired = paymentMethodSelectorRef.value?.isChannelRequired

      if (isChannelRequired) {
        console.warn('⚠️ Channel selection required but not selected')
        return
      }

      await checkoutStore.setPaymentMethod(selectedMethod)
      checkoutStore.nextStep()
    } else if (currentStep.value === 3) {
      // Place order and redirect to payment
      const result = await checkoutStore.placeOrder()

      // Redirect to unified checkout payment page
      if (result.payment_url) {
        router.push(`/order/${result.sales_order}/checkout`)
      } else {
        router.push(`/orders`) // Or somewhere else reasonable
      }
    }
  } catch (err) {
    console.error('Checkout error:', err)
  }
}

function formatIDR(amount: number): string {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount)
}
</script>

<style scoped>
.btn-primary {
  @apply px-6 py-3 bg-primary text-white rounded-lg font-bold hover:bg-opacity-90 transition-all duration-200;
}

.btn-primary:disabled {
  @apply bg-gray-300 cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 border-2 border-primary text-primary rounded-lg font-bold hover:bg-purple-50 transition-all duration-200;
}

.btn-secondary:disabled {
  @apply border-gray-300 text-gray-300 cursor-not-allowed;
}

.spinner {
  @apply w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin;
}
</style>
