import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CooperativeMemberFormData, CooperativeSettings, MembershipStatus } from '@/types/cooperative'
import type { PaymentMethod } from '@/types/checkout'
import {
  getRegistrationSettings,
  getMembershipStatus,
  registerMember,
  createRegistrationPayment
} from '@/utils/cooperativeApi'
import { getPaymentMethods } from '@/utils/checkoutApi'
import { extractErrorMessage } from '@/utils/errorHandler'

export const useCooperativeStore = defineStore('cooperative', () => {
  // State
  const currentStep = ref(1)
  const totalSteps = 5

  const settings = ref<CooperativeSettings | null>(null)
  const membershipStatus = ref<MembershipStatus | null>(null)
  const paymentMethods = ref<PaymentMethod[]>([])
  
  const paymentMethodType = ref<string>('')
  const paymentChannel = ref<string>('')

  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const error = ref<string | null>(null)

  // Form Data
  const formData = ref<CooperativeMemberFormData>({
    nik: '',
    full_name: '',
    place_of_birth: '',
    date_of_birth: '',
    gender: 'Male',
    occupation: '',
    marital_status: 'Single',
    email: '',
    phone_number: '',
    relationship_with_cooperative: '',
    ktp_photo: '',
    province: '',
    city: '',
    district: '',
    sub_district: '',
    postal_code: '',
    full_address: '',
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: '',
    emergency_contact_address: ''
  })

  // Computed Validations
  const isStep1Valid = computed(() => {
    return (
      formData.value.nik.trim() !== '' &&
      formData.value.full_name.trim() !== '' &&
      formData.value.place_of_birth.trim() !== '' &&
      formData.value.date_of_birth.trim() !== '' &&
      formData.value.gender.trim() !== '' &&
      formData.value.occupation.trim() !== '' &&
      formData.value.marital_status.trim() !== '' &&
      formData.value.email.trim() !== '' &&
      formData.value.phone_number.trim() !== '' &&
      formData.value.relationship_with_cooperative.trim() !== '' &&
      formData.value.ktp_photo.trim() !== ''
    )
  })

  const isStep2Valid = computed(() => {
    return (
      formData.value.province.trim() !== '' &&
      formData.value.city.trim() !== '' &&
      formData.value.district.trim() !== '' &&
      formData.value.sub_district.trim() !== '' &&
      formData.value.postal_code.trim() !== '' &&
      formData.value.full_address.trim() !== ''
    )
  })

  const isStep3Valid = computed(() => {
    return (
      formData.value.emergency_contact_name.trim() !== '' &&
      formData.value.emergency_contact_phone.trim() !== '' &&
      formData.value.emergency_contact_relationship.trim() !== '' &&
      formData.value.emergency_contact_address.trim() !== ''
    )
  })

  const isStep4Valid = computed(() => {
    if (!paymentMethodType.value) return false
    
    // Validate channel selection if the payment method has channels
    const method = paymentMethods.value.find(m => m.name === paymentMethodType.value)
    if (method?.payment_channels?.length && !paymentChannel.value) {
      return false
    }
    
    return true
  })

  // Actions
  const fetchSettings = async () => {
    try {
      settings.value = await getRegistrationSettings()
    } catch (err: any) {
      console.error('Failed to fetch registration settings:', err)
    }
  }

  const fetchMembershipStatus = async () => {
    isLoading.value = true
    try {
      membershipStatus.value = await getMembershipStatus()
    } catch (err: any) {
      console.error('Failed to fetch membership status:', err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchPaymentMethods = async () => {
    isLoading.value = true
    try {
      paymentMethods.value = await getPaymentMethods()
    } catch (err: any) {
      console.error('Failed to fetch payment methods:', err)
    } finally {
      isLoading.value = false
    }
  }

  const submitRegistration = async (): Promise<{ success: boolean; memberName?: string; message?: string }> => {
    isSubmitting.value = true
    error.value = null
    try {
      // 1. Register Member (Creates Draft)
      const regResponse = await registerMember(formData.value)
      if (!regResponse.member_name) {
        throw new Error('Gagal mendapatkan ID pendaftaran member')
      }
      
      const memberName = regResponse.member_name

      // 2. Create Payment Request
      await createRegistrationPayment(memberName, paymentMethodType.value, paymentChannel.value)
      
      return { success: true, memberName }
    } catch (err: any) {
      const errorMessage = extractErrorMessage(err)
      error.value = errorMessage || 'Terjadi kesalahan saat pendaftaran'
      console.error('Registration error:', err)
      return { success: false, message: error.value }
    } finally {
      isSubmitting.value = false
    }
  }

  const nextStep = () => {
    if (currentStep.value < totalSteps) {
      currentStep.value++
    }
  }

  const prevStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  const goToStep = (step: number) => {
    if (step >= 1 && step <= totalSteps) {
      currentStep.value = step
    }
  }

  const resetForm = () => {
    currentStep.value = 1
    formData.value = {
      nik: '',
      full_name: '',
      place_of_birth: '',
      date_of_birth: '',
      gender: 'Male',
      occupation: '',
      marital_status: 'Single',
      email: '',
      phone_number: '',
      relationship_with_cooperative: '',
      ktp_photo: '',
      province: '',
      city: '',
      district: '',
      sub_district: '',
      postal_code: '',
      full_address: '',
      emergency_contact_name: '',
      emergency_contact_phone: '',
      emergency_contact_relationship: '',
      emergency_contact_address: ''
    }
    paymentMethodType.value = ''
    paymentChannel.value = ''
    error.value = null
  }

  return {
    // State
    currentStep,
    totalSteps,
    settings,
    membershipStatus,
    paymentMethods,
    paymentMethodType,
    paymentChannel,
    formData,
    isLoading,
    isSubmitting,
    error,

    // Computed
    isStep1Valid,
    isStep2Valid,
    isStep3Valid,
    isStep4Valid,

    // Actions
    fetchSettings,
    fetchMembershipStatus,
    fetchPaymentMethods,
    submitRegistration,
    nextStep,
    prevStep,
    goToStep,
    resetForm
  }
})
