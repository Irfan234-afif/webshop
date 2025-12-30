<template>
  <Teleport to="body">
    <div v-if="isOpen" class="checkout-page">
      <!-- Modal Overlay -->
      <div
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
        @click="handleBackdropClick"
      >
        <div
          class="checkout-modal bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col"
          @click.stop
        >
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
              {{ currentStep }}
            </div>
            <h2 class="text-xl font-semibold">{{ stepTitle }}</h2>
          </div>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Progress Bar -->
        <div class="px-6 pt-4">
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              class="bg-primary h-2 rounded-full transition-all duration-300"
              :style="{ width: progressWidth }"
            ></div>
          </div>
        </div>

        <!-- Description -->
        <div class="px-6 py-4">
          <p class="text-sm text-gray-600">{{ stepDescription }}</p>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-6 py-4">
          <!-- Address Form (shown if no address) -->
          <AddressForm
            v-if="needsAddress"
            :student-name="props.studentName"
            @address-created="handleAddressCreated"
          />

          <!-- Regular checkout steps (shown if has address) -->
          <template v-else>
            <!-- Step 1: Pickup Type -->
            <PickupTypeSelector
              v-if="currentStep === 1"
              ref="pickupTypeSelectorRef"
            />

            <!-- Step 2: Payment Method -->
            <PaymentMethodSelector
              v-if="currentStep === 2"
              ref="paymentMethodSelectorRef"
            />

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
            <button
              v-if="currentStep > 1"
              @click="handleBack"
              class="btn-secondary flex-1"
              :disabled="isLoading"
            >
              {{ backButtonText }}
            </button>

            <!-- Next/Confirm Button -->
            <button
              @click="handleNext"
              class="btn-primary flex-1"
              :disabled="!canProceed || isLoading"
            >
              {{ nextButtonText }}
            </button>
          </div>
        </div>
      </div>
    </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'
import PickupTypeSelector from './components/PickupTypeSelector.vue'
import PaymentMethodSelector from './components/PaymentMethodSelector.vue'
import OrderConfirmation from './components/OrderConfirmation.vue'
import AddressForm from './components/AddressForm.vue'

const router = useRouter()

// Props
interface Props {
  isOpen: boolean
  studentName: string
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  orderPlaced: [orderId: string]
}>()

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

// Handle escape key to close modal
const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.isOpen) {
    handleClose()
  }
}

// Watch for modal open/close to manage body scroll and load data
watch(() => props.isOpen, async (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleEscape)

    // Debug: Log student name being sent
    console.log('🔍 CheckoutModal: Opening with student:', props.studentName)

    // CRITICAL: Initialize checkout with student name
    // This sets active student first, then fetches checkout data
    try {
      await checkoutStore.initializeCheckout(props.studentName)
      console.log('✅ CheckoutModal: Initialization successful')
    } catch (err) {
      console.error('❌ CheckoutModal: Initialization failed:', err)
    }

    // Load payment methods
    await checkoutStore.fetchPaymentMethods()
  } else {
    document.body.style.overflow = ''
    document.removeEventListener('keydown', handleEscape)
  }
})

onMounted(() => {
  if (props.isOpen) {
    document.body.style.overflow = 'hidden'
    document.addEventListener('keydown', handleEscape)
  }
})

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleEscape)
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
    2: 'Kembali (Jenis Pengambilan)',
    3: 'Kembali (Metode Pembayaran)'
  }
  return texts[currentStep.value as keyof typeof texts] || 'Kembali'
})

const nextButtonText = computed(() => {
  const texts = {
    1: 'Pilih Metode Pembayaran',
    2: 'Konfirmasi Pesanan',
    3: `Bayar Pesanan - ${formatIDR(checkoutStore.total)}`
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
    emit('close')
  }
}

function handleBackdropClick(e: MouseEvent) {
  // Only close if clicking the backdrop itself, not the modal content
  if (e.target === e.currentTarget) {
    handleClose()
  }
}

function handleBack() {
  checkoutStore.previousStep()
}

async function handleAddressCreated() {
  console.log('✅ Address created, reloading checkout data for student:', props.studentName)

  try {
    // Reload checkout data to get updated has_address status
    await checkoutStore.fetchCheckoutData(props.studentName)

    console.log('✅ Checkout data reloaded')
    console.log('   - has_address:', checkoutData.value?.has_address)
    console.log('   - shipping_address:', checkoutData.value?.shipping_address)
    console.log('   - billing_address:', checkoutData.value?.billing_address)
    console.log('   - needsAddress computed:', needsAddress.value)

    // If address is now available, the UI should automatically switch to Step 1
    // due to the needsAddress computed property becoming false
    if (checkoutData.value?.has_address) {
      console.log('✅ Address verified - checkout steps should now be visible')
    } else {
      console.warn('⚠️ Address created but has_address is still false')
    }
  } catch (err) {
    console.error('❌ Failed to reload checkout data:', err)
    error.value = err as Error
  }
}

async function handleNext() {
  try {
    if (currentStep.value === 1) {
      // Save pickup type (data already synced to store via watchers)
      const selectedType = checkoutStore.pickupType
      const selectedDate = checkoutStore.deliveryDate

      if (!selectedType || !selectedDate) {
        // This shouldn't happen since button is disabled, but just in case
        return
      }

      // Save to backend
      await checkoutStore.setPickupType(selectedType, selectedDate)
      checkoutStore.nextStep()
    } else if (currentStep.value === 2) {
      // Save payment method
      const selectedMethod = paymentMethodSelectorRef.value?.selectedMethod
      if (!selectedMethod) {
        return
      }

      await checkoutStore.setPaymentMethod(selectedMethod)
      checkoutStore.nextStep()
    } else if (currentStep.value === 3) {
      // Place order and redirect to payment
      const result = await checkoutStore.placeOrder()

      // Emit order placed event with order ID
      emit('orderPlaced', result.sales_order)

      // Redirect to unified checkout payment page
      if (result.payment_url) {
        // Close modal first
        emit('close')
        // Navigate to unified checkout route
        router.push(`/order/${result.sales_order}/checkout`)
      } else {
        // If no payment URL, close modal (parent will handle navigation)
        emit('close')
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
.checkout-modal {
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn-primary {
  @apply px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-opacity-90 transition-all duration-200;
}

.btn-primary:disabled {
  @apply bg-gray-300 cursor-not-allowed;
}

.btn-secondary {
  @apply px-6 py-3 border-2 border-primary text-primary rounded-lg font-medium hover:bg-purple-50 transition-all duration-200;
}

.btn-secondary:disabled {
  @apply border-gray-300 text-gray-300 cursor-not-allowed;
}

.spinner {
  @apply w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin;
}
</style>
