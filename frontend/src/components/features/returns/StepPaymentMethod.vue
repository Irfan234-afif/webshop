<template>
  <div class="space-y-6">
    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <!-- Payment method selection -->
    <div v-else class="space-y-4">
      <div
        v-for="method in refundPaymentMethods"
        :key="method.name"
        @click="selectPaymentMethod(method.name)"
        class="bg-white border-2 rounded-xl p-6 cursor-pointer transition-all hover:shadow-md"
        :class="{
          'border-primary bg-primary/5': selectedPaymentMethod === method.name,
          'border-gray-200': selectedPaymentMethod !== method.name
        }"
      >
        <div class="flex items-start">
          <!-- Icon -->
          <div class="flex-shrink-0 mr-4">
            <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
              <!-- Cash icon -->
              <svg v-if="method.payment_type === 'Cash'" class="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
              </svg>
              <!-- Bank transfer icon -->
              <svg v-else class="w-6 h-6 text-primary" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
              </svg>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1">
            <h3 class="font-bold text-gray-900 text-lg mb-1">{{ method.title }}</h3>
            <p v-if="method.description" class="text-sm text-gray-600">
              {{ method.description }}
            </p>
            <p v-else class="text-sm text-gray-600">
              {{ method.payment_type === 'Cash' 
                ? 'Dana dikembalikan secara tunai di koperasi. Jadwal pengambilan akan diinformasikan admin' 
                : 'Lakukan transfer manual ke rekening resmi koperasi sesuai instruksi yang diberikan.' 
              }}
            </p>
          </div>

          <!-- Radio button -->
          <div class="ml-4 flex-shrink-0">
            <div 
              class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
              :class="{
                'border-primary bg-primary': selectedPaymentMethod === method.name,
                'border-gray-300': selectedPaymentMethod !== method.name
              }"
            >
              <div 
                v-if="selectedPaymentMethod === method.name"
                class="w-2 h-2 bg-white rounded-full"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bank details form (shown for Transfer Manual) -->
      <div 
        v-if="isTransferManualSelected" 
        class="bg-gray-50 border border-gray-200 rounded-xl p-6 space-y-4"
      >
        <h4 class="font-semibold text-gray-900">Detail Rekening Bank</h4>
        <p class="text-sm text-gray-600">
          Dana akan ditransfer ke rekening yang Anda masukkan di bawah ini.
        </p>

        <!-- Bank Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nama Bank <span class="text-red-500">*</span>
          </label>
          <input
            v-model="bankDetails.bank_name"
            type="text"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            :class="{ 'border-red-500': bankDetailsErrors.bank_name }"
            placeholder="Contoh: Bank Central Asia (BCA)"
          />
          <p v-if="bankDetailsErrors.bank_name" class="text-sm text-red-600 mt-1">
            {{ bankDetailsErrors.bank_name }}
          </p>
        </div>

        <!-- Account Number -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nomor Rekening <span class="text-red-500">*</span>
          </label>
          <input
            v-model="bankDetails.account_number"
            type="text"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            :class="{ 'border-red-500': bankDetailsErrors.account_number }"
            placeholder="Contoh: 1234567890"
            @input="validateAccountNumber"
          />
          <p v-if="bankDetailsErrors.account_number" class="text-sm text-red-600 mt-1">
            {{ bankDetailsErrors.account_number }}
          </p>
        </div>

        <!-- Account Holder Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Nama Pemilik Rekening <span class="text-red-500">*</span>
          </label>
          <input
            v-model="bankDetails.account_holder_name"
            type="text"
            class="w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent"
            :class="{ 'border-red-500': bankDetailsErrors.account_holder_name }"
            placeholder="Nama sesuai rekening bank"
          />
          <p v-if="bankDetailsErrors.account_holder_name" class="text-sm text-red-600 mt-1">
            {{ bankDetailsErrors.account_holder_name }}
          </p>
        </div>

        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <p class="text-sm text-yellow-800">
              Pastikan data rekening yang Anda masukkan benar. Dana akan ditransfer ke rekening ini dan tidak dapat diubah setelah pengajuan disetujui.
            </p>
          </div>
        </div>
      </div>

      <!-- Validation error -->
      <div v-if="validationError" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p class="text-yellow-800">{{ validationError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useReturnsStore } from '@/stores/returns'

interface BankDetails {
  bank_name: string
  account_number: string
  account_holder_name: string
}

interface Emits {
  (e: 'update:selectedPaymentMethod', value: string): void
  (e: 'update:bankDetails', value: BankDetails): void
  (e: 'update:isValid', value: boolean): void
}

const emit = defineEmits<Emits>()

const returnsStore = useReturnsStore()

const selectedPaymentMethod = ref('')
const bankDetails = ref<BankDetails>({
  bank_name: '',
  account_number: '',
  account_holder_name: ''
})
const bankDetailsErrors = ref<Record<string, string>>({})
const validationError = ref('')

const isLoading = computed(() => returnsStore.isLoading)
const error = computed(() => returnsStore.error)
const refundPaymentMethods = computed(() => returnsStore.refundPaymentMethods)

const isTransferManualSelected = computed(() => {
  const selectedMethod = refundPaymentMethods.value.find(m => m.name === selectedPaymentMethod.value)
  return selectedMethod?.payment_type === 'Transfer Manual'
})

const isValid = computed(() => {
  if (!selectedPaymentMethod.value) {
    return false
  }

  if (isTransferManualSelected.value) {
    return (
      bankDetails.value.bank_name.trim() !== '' &&
      bankDetails.value.account_number.trim() !== '' &&
      bankDetails.value.account_holder_name.trim() !== ''
    )
  }

  return true
})

watch(selectedPaymentMethod, () => {
  validationError.value = ''
  emit('update:selectedPaymentMethod', selectedPaymentMethod.value)
  
  // Clear bank details if switching to Cash
  if (!isTransferManualSelected.value) {
    bankDetails.value = {
      bank_name: '',
      account_number: '',
      account_holder_name: ''
    }
    bankDetailsErrors.value = {}
  }
  
  validateForm()
})

watch(bankDetails, () => {
  emit('update:bankDetails', bankDetails.value)
  validateForm()
}, { deep: true })

watch(isValid, (newVal) => {
  emit('update:isValid', newVal)
})

onMounted(async () => {
  await loadRefundPaymentMethods()
})

async function loadRefundPaymentMethods() {
  try {
    await returnsStore.fetchRefundPaymentMethods()
  } catch (err) {
    console.error('Error loading refund payment methods:', err)
  }
}

function selectPaymentMethod(methodName: string) {
  selectedPaymentMethod.value = methodName
}

function validateAccountNumber() {
  // Remove non-numeric characters
  bankDetails.value.account_number = bankDetails.value.account_number.replace(/\D/g, '')
  
  // Clear error if exists
  if (bankDetailsErrors.value.account_number) {
    bankDetailsErrors.value.account_number = ''
  }
}

function validateForm(): boolean {
  validationError.value = ''
  bankDetailsErrors.value = {}

  if (!selectedPaymentMethod.value) {
    validationError.value = 'Silakan pilih metode pengembalian dana'
    return false
  }

  if (isTransferManualSelected.value) {
    let hasError = false

    if (!bankDetails.value.bank_name.trim()) {
      bankDetailsErrors.value.bank_name = 'Nama bank wajib diisi'
      hasError = true
    }

    if (!bankDetails.value.account_number.trim()) {
      bankDetailsErrors.value.account_number = 'Nomor rekening wajib diisi'
      hasError = true
    } else if (bankDetails.value.account_number.length < 10) {
      bankDetailsErrors.value.account_number = 'Nomor rekening minimal 10 digit'
      hasError = true
    }

    if (!bankDetails.value.account_holder_name.trim()) {
      bankDetailsErrors.value.account_holder_name = 'Nama pemilik rekening wajib diisi'
      hasError = true
    }

    if (hasError) {
      return false
    }
  }

  return true
}

// Expose validation method for parent component
defineExpose({
  validateForm
})
</script>
