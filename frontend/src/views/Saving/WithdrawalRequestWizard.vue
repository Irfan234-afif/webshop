<template>
  <DefaultLayout>
    <Container class="py-4 md:py-6 lg:py-8">
      <div class="max-w-2xl mx-auto">
        <!-- Header with back button -->
        <div class="mb-8">
          <button @click="handleBack"
            class="flex items-center text-gray-600 hover:text-gray-900 font-medium transition-colors mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd"
                d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z"
                clip-rule="evenodd" />
            </svg>
            Kembali
          </button>
          <h1 class="text-3xl font-bold text-gray-900">Pengajuan Pengambilan Saldo</h1>
          <p class="text-gray-600 mt-2">
            Isi nominal dan pilih metode pengembalian dana untuk simpanan sukarela Anda.
          </p>
        </div>

        <!-- Progress indicator -->
        <div class="bg-white border border-gray-200 rounded-xl p-4 md:p-8 mb-6">
          <div class="flex items-center justify-between">
            <div v-for="step in steps" :key="step.number" class="flex items-center"
              :class="{ 'flex-1': step.number < steps.length }">
              <!-- Step circle -->
              <div
                class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all"
                :class="{
                  'bg-primary text-white': currentStep === step.number,
                  'bg-green-500 text-white': currentStep > step.number,
                  'bg-gray-200 text-gray-500': currentStep < step.number
                }">
                <svg v-if="currentStep > step.number" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd" />
                </svg>
                <span v-else>{{ step.number }}</span>
              </div>

              <!-- Step label -->
              <div class="ml-3 flex-shrink-0">
                <p class="font-semibold text-sm whitespace-nowrap" :class="{
                  'text-gray-900': currentStep === step.number,
                  'text-gray-500': currentStep !== step.number
                }">
                  {{ step.title }}
                </p>
              </div>

              <!-- Connector line -->
              <div v-if="step.number < steps.length" class="flex-1 h-0.5 mx-4 transition-colors" :class="{
                'bg-primary': currentStep > step.number,
                'bg-gray-200': currentStep <= step.number
              }"></div>
            </div>
          </div>
        </div>

        <!-- Step content -->
        <div class="bg-white border border-gray-200 rounded-xl p-8 mb-6">
          <!-- STEP 1: Amount -->
          <div v-if="currentStep === 1">
            <h2 class="text-xl font-bold text-gray-900 mb-6">Nominal Penarikan</h2>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Saldo Tersedia: <span class="text-primary font-bold">{{ formatIDR(voluntaryBalance) }}</span>
                </label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <span class="text-gray-500 font-medium">Rp</span>
                  </div>
                  <input 
                    type="text" 
                    inputmode="numeric"
                    v-model="displayAmount" 
                    class="w-full border border-gray-300 rounded-lg pl-12 pr-4 py-3 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-colors"
                    placeholder="0"
                  />
                </div>
                
                <div class="grid grid-cols-2 gap-2 mt-4">
                  <button 
                    v-for="amount in quickAmounts" 
                    :key="amount.value"
                    @click="setQuickAmount(amount.value)"
                    type="button"
                    class="py-4 px-3 text-sm font-medium rounded-lg border transition-colors"
                    :class="{
                      'border-primary bg-primary/5 text-primary': formData.amount === amount.value,
                      'border-gray-200 text-gray-700 hover:border-primary hover:text-primary': formData.amount !== amount.value
                    }"
                  >
                    {{ amount.label }}
                  </button>
                  <button
                    @click="setQuickAmount(voluntaryBalance)"
                    type="button"
                    class="py-2 px-3 text-sm font-medium rounded-lg border transition-colors"
                    :class="{
                      'border-primary bg-primary/5 text-primary': formData.amount === voluntaryBalance && (formData.amount || 0) > 0,
                      'border-gray-200 text-gray-700 hover:border-primary hover:text-primary': formData.amount !== voluntaryBalance || (formData.amount || 0) === 0
                    }"
                  >
                    Semua Saldo
                  </button>
                </div>

                <p v-if="amountError" class="text-sm text-red-600 mt-2">{{ amountError }}</p>
                <p v-else class="text-xs text-gray-500 mt-2">Minimal penarikan Rp 10.000</p>
              </div>
            </div>
          </div>

          <!-- STEP 2: Payment Method (Reusing Return View Component) -->
          <StepPaymentMethod 
            v-else-if="currentStep === 2"
            @update:selectedPaymentMethod="formData.refund_payment_mode = $event"
            @update:bankDetails="updateBankDetails" 
            @update:isValid="stepValidation.step2 = $event" 
          />

          <!-- STEP 3: Confirmation -->
          <div v-else-if="currentStep === 3">
            <h2 class="text-xl font-bold text-gray-900 mb-6">Konfirmasi Penarikan</h2>
            
            <div v-if="submissionError" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p class="text-red-700">{{ submissionError }}</p>
            </div>

            <div class="bg-gray-50 rounded-xl p-6 border border-gray-200 space-y-4">
              <div class="flex justify-between py-2 border-b border-gray-200">
                <span class="text-gray-600">Nominal Penarikan</span>
                <span class="font-bold text-gray-900">{{ formatIDR(formData.amount || 0) }}</span>
              </div>
              <div class="flex justify-between py-2 border-b border-gray-200">
                <span class="text-gray-600">Metode Pencairan</span>
                <span class="font-bold text-gray-900">{{ paymentMethodTitle }}</span>
              </div>
              
              <div v-if="isTransfer" class="pt-2">
                <h4 class="text-sm font-bold text-gray-700 mb-2">Detail Rekening Tujuan</h4>
                <div class="bg-white p-4 rounded-lg border border-gray-200">
                  <div class="grid grid-cols-3 gap-2 text-sm">
                    <div class="text-gray-500">Bank</div>
                    <div class="col-span-2 font-medium text-gray-900">{{ formData.bank_name }}</div>
                    
                    <div class="text-gray-500">No. Rekening</div>
                    <div class="col-span-2 font-medium text-gray-900">{{ formData.account_number }}</div>
                    
                    <div class="text-gray-500">Atas Nama</div>
                    <div class="col-span-2 font-medium text-gray-900">{{ formData.account_holder_name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Navigation buttons -->
        <div class="flex items-center justify-between gap-4">
          <button v-if="currentStep > 1" @click="previousStep" type="button"
            class="px-6 py-3 border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-colors">
            Kembali
          </button>
          <div v-else></div>

          <button v-if="currentStep < 3" @click="nextStep" type="button" :disabled="!isCurrentStepValid"
            class="px-6 py-3 font-semibold rounded-lg transition-all" :class="{
              'bg-primary text-white hover:opacity-90': isCurrentStepValid,
              'bg-gray-300 text-gray-500 cursor-not-allowed': !isCurrentStepValid
            }">
            Lanjutkan
          </button>

          <button v-else @click="submitWithdrawal" type="button" :disabled="isSubmitting"
            class="px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center">
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            Konfirmasi Penarikan
          </button>
        </div>
      </div>
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import StepPaymentMethod from '@/components/features/returns/StepPaymentMethod.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import { useAlertStore } from '@/stores/alert'
import { useReturnsStore } from '@/stores/returns'
import { createVoluntarySavingWithdrawal } from '@/utils/savingPaymentApi'
import { formatIDR } from '@/utils/formatters'

const router = useRouter()
const alertStore = useAlertStore()
const returnsStore = useReturnsStore()

const currentStep = ref(1)
const isSubmitting = ref(false)
const submissionError = ref<string | null>(null)
const amountError = ref<string | null>(null)

// Fetch Savings for the balance
const savingsResource = createResource({
  url: 'webshop.webshop.api.cooperative_payment.get_member_savings',
  auto: true
});

const voluntaryBalance = computed(() => {
  return savingsResource.data ? savingsResource.data.voluntary_saving_balance : 0;
});

const formData = ref({
  amount: null as number | null,
  refund_payment_mode: '',
  bank_name: '',
  account_number: '',
  account_holder_name: ''
})

const displayAmount = computed({
  get() {
    return formData.value.amount ? formData.value.amount.toLocaleString('id-ID') : ''
  },
  set(val: string) {
    const numericValue = parseInt(val.replace(/\D/g, ''), 10)
    formData.value.amount = isNaN(numericValue) ? null : numericValue
    validateAmount()
  }
})

const quickAmounts = [
  { label: '50.000', value: 50000 },
  { label: '100.000', value: 100000 },
  { label: '200.000', value: 200000 },
  { label: '500.000', value: 500000 },
  { label: '1.000.000', value: 1000000 },
]

function setQuickAmount(amount: number) {
  formData.value.amount = amount
  validateAmount()
}

const stepValidation = ref({
  step1: false,
  step2: false,
  step3: true
})

const steps = [
  { number: 1, title: 'Nominal Penarikan' },
  { number: 2, title: 'Metode Pencairan' },
  { number: 3, title: 'Konfirmasi' }
]

const refundPaymentMethods = computed(() => returnsStore.refundPaymentMethods)

const isTransfer = computed(() => {
  const method = refundPaymentMethods.value.find(m => m.name === formData.value.refund_payment_mode)
  return method?.payment_type === 'Transfer Manual'
})

const paymentMethodTitle = computed(() => {
  const method = refundPaymentMethods.value.find(m => m.name === formData.value.refund_payment_mode)
  return method ? method.title : '-'
})

const isCurrentStepValid = computed(() => {
  return stepValidation.value[`step${currentStep.value}` as keyof typeof stepValidation.value]
})

function validateAmount() {
  const amt = formData.value.amount || 0;
  if (amt < 10000) {
    amountError.value = "Minimal penarikan adalah Rp 10.000";
    stepValidation.value.step1 = false;
  } else if (amt > voluntaryBalance.value) {
    amountError.value = `Saldo tidak mencukupi. Maksimal: ${formatIDR(voluntaryBalance.value)}`;
    stepValidation.value.step1 = false;
  } else {
    amountError.value = null;
    stepValidation.value.step1 = true;
  }
}

function updateBankDetails(details: { bank_name: string; account_number: string; account_holder_name: string }) {
  formData.value.bank_name = details.bank_name
  formData.value.account_number = details.account_number
  formData.value.account_holder_name = details.account_holder_name
}

function nextStep() {
  if (currentStep.value < 3 && isCurrentStepValid.value) {
    currentStep.value++
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function previousStep() {
  if (currentStep.value > 1) {
    currentStep.value--
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

function handleBack() {
  if (currentStep.value > 1) {
    previousStep()
  } else {
    router.push('/saving')
  }
}

async function submitWithdrawal() {
  try {
    isSubmitting.value = true
    submissionError.value = null

    if (!formData.value.amount) return;

    let bankDetails = undefined;
    if (isTransfer.value) {
      bankDetails = {
        bank_name: formData.value.bank_name,
        account_number: formData.value.account_number,
        account_holder_name: formData.value.account_holder_name
      };
    }

    const response = await createVoluntarySavingWithdrawal(
      formData.value.amount,
      paymentMethodTitle.value, // sending title e.g "Transfer Manual" to backend
      bankDetails
    )

    if (response.status === 'success') {
      alertStore.success('Pengajuan pengambilan saldo berhasil!', 'Success')
      router.push('/saving')
    }
  } catch (err: any) {
    console.error('Error submitting withdrawal request:', err)
    submissionError.value = err.message || 'Terjadi kesalahan. Silakan coba lagi.'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    isSubmitting.value = false
  }
}
</script>
