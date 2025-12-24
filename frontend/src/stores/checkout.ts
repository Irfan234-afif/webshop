import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  CheckoutData,
  PaymentMethod,
  OrderConfirmationResponse
} from '@/types/checkout'
import {
  getCheckoutData,
  updatePickupType,
  updatePaymentMethod,
  getPaymentMethods,
  placeOrderWithPayment
} from '@/utils/checkoutApi'

export const useCheckoutStore = defineStore('checkout', () => {
  // State
  const checkoutData = ref<CheckoutData | null>(null)
  const currentStep = ref<number>(1)
  const pickupType = ref<string>('')
  const paymentMethodType = ref<string>('')
  const deliveryDate = ref<string>('')
  const paymentMethods = ref<PaymentMethod[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<Error | null>(null)

  // Getters
  const subtotal = computed(() => checkoutData.value?.subtotal || 0)
  const voucherDiscount = computed(() => checkoutData.value?.voucher_discount || 0)
  const memberDiscount = computed(() => checkoutData.value?.member_discount || 0)
  const total = computed(() => checkoutData.value?.total || 0)
  const items = computed(() => checkoutData.value?.items || [])
  const quotationName = computed(() => checkoutData.value?.quotation_name || '')

  const canProceedToStep2 = computed(() => {
    if (!pickupType.value) return false
    if (pickupType.value === 'Ambil di koperasi') {
      return !!deliveryDate.value
    }
    return true
  })

  const canProceedToStep3 = computed(() => {
    return !!paymentMethodType.value
  })

  const canPlaceOrder = computed(() => {
    return canProceedToStep2.value && canProceedToStep3.value
  })

  // Actions
  async function initializeCheckout(studentName: string) {
    isLoading.value = true
    error.value = null

    try {
      console.log('🔍 initializeCheckout: Starting with student:', studentName)

      // CRITICAL: Pass student_name directly to get_checkout_data
      // Backend will set active student and fetch quotation for that student
      const data = await getCheckoutData(studentName)
      checkoutData.value = data

      console.log('✅ initializeCheckout: Data fetched successfully', data)

      // Initialize local state from checkout data
      if (data.pickup_type) {
        pickupType.value = data.pickup_type
      }
      if (data.payment_method_type) {
        paymentMethodType.value = data.payment_method_type
      }
      if (data.delivery_date) {
        deliveryDate.value = data.delivery_date
      }
    } catch (err) {
      error.value = err as Error
      console.error('❌ initializeCheckout: Failed:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCheckoutData(studentName?: string) {
    isLoading.value = true
    error.value = null

    try {
      const data = await getCheckoutData(studentName)
      checkoutData.value = data

      // Initialize local state from checkout data
      if (data.pickup_type) {
        pickupType.value = data.pickup_type
      }
      if (data.payment_method_type) {
        paymentMethodType.value = data.payment_method_type
      }
      if (data.delivery_date) {
        deliveryDate.value = data.delivery_date
      }
    } catch (err) {
      error.value = err as Error
      console.error('Failed to fetch checkout data:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function setPickupType(type: string, deliveryDateTime?: string) {
    isLoading.value = true
    error.value = null

    try {
      // CRITICAL: Pass quotation_name explicitly
      if (!quotationName.value) {
        throw new Error('Quotation name not found. Please refresh and try again.')
      }

      console.log('🔍 setPickupType: Updating quotation:', quotationName.value)

      await updatePickupType({
        quotation_name: quotationName.value,
        pickup_type: type,
        delivery_date: deliveryDateTime
      })

      pickupType.value = type
      deliveryDate.value = deliveryDateTime || ''

      // Update checkout data
      if (checkoutData.value) {
        checkoutData.value.pickup_type = type
        checkoutData.value.delivery_date = deliveryDateTime
      }

      console.log('✅ setPickupType: Updated successfully')
    } catch (err) {
      error.value = err as Error
      console.error('❌ setPickupType: Failed:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function setPaymentMethod(type: string) {
    isLoading.value = true
    error.value = null

    try {
      // CRITICAL: Pass quotation_name explicitly
      if (!quotationName.value) {
        throw new Error('Quotation name not found. Please refresh and try again.')
      }

      console.log('🔍 setPaymentMethod: Updating quotation:', quotationName.value)

      await updatePaymentMethod({
        quotation_name: quotationName.value,
        payment_method_type: type
      })

      paymentMethodType.value = type

      // Update checkout data
      if (checkoutData.value) {
        checkoutData.value.payment_method_type = type
      }

      console.log('✅ setPaymentMethod: Updated successfully')
    } catch (err) {
      error.value = err as Error
      console.error('❌ setPaymentMethod: Failed:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPaymentMethods() {
    isLoading.value = true
    error.value = null

    try {
      const methods = await getPaymentMethods()
      paymentMethods.value = methods
    } catch (err) {
      error.value = err as Error
      console.error('Failed to fetch payment methods:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function placeOrder(): Promise<OrderConfirmationResponse> {
    isLoading.value = true
    error.value = null

    try {
      // CRITICAL: Pass quotation_name explicitly
      if (!quotationName.value) {
        throw new Error('Quotation name not found. Please refresh and try again.')
      }

      console.log('🔍 placeOrder: Creating order from quotation:', quotationName.value)

      const response = await placeOrderWithPayment(quotationName.value)

      console.log('✅ placeOrder: Order created successfully:', response.sales_order)

      return response
    } catch (err) {
      error.value = err as Error
      console.error('❌ placeOrder: Failed:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function nextStep() {
    if (currentStep.value < 3) {
      currentStep.value++
    }
  }

  function previousStep() {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  function goToStep(step: number) {
    if (step >= 1 && step <= 3) {
      currentStep.value = step
    }
  }

  function resetCheckout() {
    checkoutData.value = null
    currentStep.value = 1
    pickupType.value = ''
    paymentMethodType.value = ''
    deliveryDate.value = ''
    paymentMethods.value = []
    error.value = null
  }

  return {
    // State
    checkoutData,
    currentStep,
    pickupType,
    paymentMethodType,
    deliveryDate,
    paymentMethods,
    isLoading,
    error,

    // Getters
    subtotal,
    voucherDiscount,
    memberDiscount,
    total,
    items,
    quotationName,
    canProceedToStep2,
    canProceedToStep3,
    canPlaceOrder,

    // Actions
    initializeCheckout,
    fetchCheckoutData,
    setPickupType,
    setPaymentMethod,
    fetchPaymentMethods,
    placeOrder,
    nextStep,
    previousStep,
    goToStep,
    resetCheckout
  }
})
