<template>
  <DefaultLayout>
    <div class="min-h-screen bg-background py-8">
      <Container>
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
          <h1 class="text-3xl font-bold text-gray-900">Ajukan Pengembalian</h1>
          <p class="text-gray-600 mt-2">
            Pilih alasan pengembalian pesanan agar tim koperasi dapat memahami kendala yang dialami
            dan memproses pengajuan dengan tepat.
          </p>
        </div>

        <!-- Progress indicator -->
        <div class="bg-white border border-gray-200 rounded-xl p-4 md:p-8 mb-6">
          <!-- Desktop: Full labels -->
          <div class="hidden md:flex items-center justify-between">
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

          <!-- Mobile: Compact with current step label -->
          <div class="md:hidden">
            <div class="flex items-center justify-between mb-3">
              <div v-for="step in steps" :key="step.number" class="flex items-center"
                :class="{ 'flex-1': step.number < steps.length }">
                <!-- Step circle (smaller on mobile) -->
                <div
                  class="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs transition-all"
                  :class="{
                    'bg-primary text-white': currentStep === step.number,
                    'bg-green-500 text-white': currentStep > step.number,
                    'bg-gray-200 text-gray-500': currentStep < step.number
                  }">
                  <svg v-if="currentStep > step.number" class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clip-rule="evenodd" />
                  </svg>
                  <span v-else>{{ step.number }}</span>
                </div>

                <!-- Connector line -->
                <div v-if="step.number < steps.length" class="flex-1 h-0.5 mx-2 transition-colors" :class="{
                  'bg-primary': currentStep > step.number,
                  'bg-gray-200': currentStep <= step.number
                }"></div>
              </div>
            </div>
            <!-- Current step label -->
            <p class="text-center text-sm font-semibold text-gray-900">
              Langkah {{ currentStep }}/{{ steps.length }}: {{ steps[currentStep - 1]?.title }}
            </p>
          </div>
        </div>

        <!-- Step content -->
        <div class="bg-white border border-gray-200 rounded-xl p-8 mb-6">
          <StepSelectReason v-if="currentStep === 1" @update:selectedReason="formData.return_reason = $event"
            @update:otherReason="formData.other_reason = $event" @update:isValid="stepValidation.step1 = $event" />

          <StepUploadProof v-else-if="currentStep === 2" @update:files="formData.supporting_documents = $event"
            @update:isValid="stepValidation.step2 = $event" />

          <StepPaymentMethod v-else-if="currentStep === 3"
            @update:selectedPaymentMethod="formData.refund_payment_mode = $event"
            @update:bankDetails="updateBankDetails" @update:isValid="stepValidation.step3 = $event" />

          <StepConfirmation v-else-if="currentStep === 4" ref="confirmationStep" :formData="formData"
            :orderSummary="orderSummary" />
        </div>

        <!-- Navigation buttons -->
        <div class="flex items-center justify-between gap-4">
          <button v-if="currentStep > 1" @click="previousStep" type="button"
            class="px-6 py-3 border-2 border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-colors">
            Kembali ({{ getPreviousStepLabel() }})
          </button>
          <div v-else></div>

          <button v-if="currentStep < 4" @click="nextStep" type="button" :disabled="!isCurrentStepValid"
            class="px-6 py-3 font-semibold rounded-lg transition-all" :class="{
              'bg-primary text-white hover:opacity-90': isCurrentStepValid,
              'bg-gray-300 text-gray-500 cursor-not-allowed': !isCurrentStepValid
            }">
            {{ getNextStepLabel() }}
          </button>

          <button v-else @click="submitReturnRequest" type="button" :disabled="isSubmitting"
            class="px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed flex items-center">
            <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            Konfirmasi Pengembalian
          </button>
        </div>
      </Container>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReturnsStore } from '@/stores/returns'
import type { ReturnRequestFormData, EligibleOrder } from '@/types/returns'
import StepSelectReason from '@/components/features/returns/StepSelectReason.vue'
import StepUploadProof from '@/components/features/returns/StepUploadProof.vue'
import StepPaymentMethod from '@/components/features/returns/StepPaymentMethod.vue'
import StepConfirmation from '@/components/features/returns/StepConfirmation.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import { useAlertStore } from '@/stores/alert'

const router = useRouter()
const route = useRoute()
const returnsStore = useReturnsStore()
const alertStore = useAlertStore()

const currentStep = ref(1)
const isSubmitting = ref(false)
const confirmationStep = ref<InstanceType<typeof StepConfirmation> | null>(null)

const formData = ref<ReturnRequestFormData>({
  sales_order: route.params.orderId as string,
  return_reason: '',
  other_reason: '',
  supporting_documents: [],
  refund_payment_mode: '',
  bank_name: '',
  account_number: '',
  account_holder_name: ''
})

const stepValidation = ref({
  step1: false,
  step2: true, // Upload is optional
  step3: false,
  step4: true
})

const orderSummary = ref<EligibleOrder | null>(null)

const steps = [
  { number: 1, title: 'Pilih Alasan Pengembalian' },
  { number: 2, title: 'Upload Bukti Pendukung' },
  { number: 3, title: 'Metode Pengembalian Dana' },
  { number: 4, title: 'Konfirmasi Pengajuan pesanan' }
]

const isCurrentStepValid = computed(() => {
  return stepValidation.value[`step${currentStep.value}` as keyof typeof stepValidation.value]
})

onMounted(async () => {
  await loadOrderSummary()
  // Initialize the return request in store
  returnsStore.initReturnRequest(formData.value.sales_order)
})

async function loadOrderSummary() {
  try {
    await returnsStore.fetchEligibleOrders()
    const order = returnsStore.eligibleOrders.find(
      o => o.sales_order === formData.value.sales_order
    )

    if (order) {
      orderSummary.value = order
    } else {
      // Order not eligible, redirect back
      alert('Pesanan ini tidak dapat dikembalikan')
      // router.push('/orders')
    }
  } catch (err) {
    console.error('Error loading order summary:', err)
  }
}

function nextStep() {
  if (currentStep.value < 4 && isCurrentStepValid.value) {
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
    router.push(`/order/${formData.value.sales_order}`)
  }
}

function getNextStepLabel(): string {
  switch (currentStep.value) {
    case 1:
      return 'Upload Bukti Pendukung'
    case 2:
      return 'Metode Refund'
    case 3:
      return 'Konfirmasi Pengembalian'
    default:
      return 'Lanjutkan'
  }
}

function getPreviousStepLabel(): string {
  switch (currentStep.value) {
    case 2:
      return 'Alasan Pengembalian'
    case 3:
      return 'Upload Bukti'
    case 4:
      return 'Metode Refund'
    default:
      return 'Kembali'
  }
}

function updateBankDetails(details: { bank_name: string; account_number: string; account_holder_name: string }) {
  formData.value.bank_name = details.bank_name
  formData.value.account_number = details.account_number
  formData.value.account_holder_name = details.account_holder_name
}

async function submitReturnRequest() {
  try {
    isSubmitting.value = true

    // Clear any previous errors
    confirmationStep.value?.setSubmissionError(null)

    const response = await returnsStore.createReturnRequest(formData.value)

    if (response) {
      // Success - redirect to return requests list or show success message
      alertStore.success('Pengajuan pengembalian berhasil dibuat!', 'Success')
      router.push('/orders?tab=returns')
    }
  } catch (err: any) {
    console.error('Error submitting return request:', err)

    // Show error in confirmation step
    const errorMessage = returnsStore.error || 'Terjadi kesalahan. Silakan coba lagi.'
    confirmationStep.value?.setSubmissionError(errorMessage)

    // Scroll to top to show error
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    isSubmitting.value = false
  }
}
</script>
