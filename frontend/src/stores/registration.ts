import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RegistrationFormData, StudentData, RegistrationPayload } from '@/types/auth'

export const useRegistrationStore = defineStore('registration', () => {
  // Current step (1-3)
  const currentStep = ref(1)
  const totalSteps = 3

  // Loading and error states
  const isRegistering = ref(false)
  const emailError = ref('')
  const passwordError = ref('')

  // Form data
  const formData = ref<RegistrationFormData>({
    name: '',
    email: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    students: [
      {
        student_name: '',
        school_unit: '',
        grade_level: '',
        date_of_birth: '',
        nisn: ''
      }
    ]
  })

  // Computed validations
  const isStep1Valid = computed(() => {
    return (
      formData.value.name.trim() !== '' &&
      formData.value.email.trim() !== '' &&
      formData.value.phoneNumber.trim() !== '' &&
      formData.value.password.trim() !== '' &&
      formData.value.password === formData.value.confirmPassword &&
      !emailError.value
    )
  })

  const isStep2Valid = computed(() => {
    return formData.value.students.every(student =>
      student.student_name.trim() !== '' &&
      student.school_unit.trim() !== ''
    )
  })

  // Actions
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

  const addStudent = () => {
    formData.value.students.push({
      student_name: '',
      school_unit: '',
      grade_level: '',
      date_of_birth: '',
      nisn: ''
    })
  }

  const removeStudent = (index: number) => {
    if (formData.value.students.length > 1) {
      formData.value.students.splice(index, 1)
    }
  }

  const validateEmail = async () => {
    if (!formData.value.email) {
      emailError.value = ''
      return
    }

    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.value.email)) {
      emailError.value = 'Format email tidak valid'
      return
    }

    // Check email availability via API
    try {
      const response = await fetch(
        `/api/method/webshop.webshop.api.auth.check_email_availability?email=${formData.value.email}`
      )
      const data = await response.json()

      if (!data.message.success || !data.message.available) {
        emailError.value = data.message.message || 'Email sudah terdaftar'
      } else {
        emailError.value = ''
      }
    } catch (error) {
      console.error('Error checking email availability:', error)
      emailError.value = 'Terjadi kesalahan saat memeriksa email'
    }
  }

  const validatePasswordMatch = () => {
    if (formData.value.password !== formData.value.confirmPassword) {
      passwordError.value = 'Kata sandi tidak cocok'
    } else {
      passwordError.value = ''
    }
  }

  const submitRegistration = async (): Promise<{ success: boolean; message?: string }> => {
    isRegistering.value = true
    emailError.value = ''
    passwordError.value = ''

    try {
      // Prepare registration payload
      const registrationData: RegistrationPayload = {
        name: formData.value.name,
        email: formData.value.email,
        phone_number: formData.value.phoneNumber,
        password: formData.value.password,
        students: formData.value.students
      }

      // Call registration API
      const response = await fetch('/api/method/webshop.webshop.api.auth.register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registrationData)
      })

      const result = await response.json()

      if (result.message.success) {
        // Registration successful - reset form
        resetForm()
        return { success: true }
      } else {
        // Handle error from API
        emailError.value = result.message.message || 'Terjadi kesalahan saat pendaftaran'
        return { success: false, message: result.message.message }
      }
    } catch (error) {
      console.error('Registration error:', error)
      const errorMessage = 'Terjadi kesalahan saat pendaftaran. Silakan coba lagi.'
      emailError.value = errorMessage
      return { success: false, message: errorMessage }
    } finally {
      isRegistering.value = false
    }
  }

  const resetForm = () => {
    currentStep.value = 1
    formData.value = {
      name: '',
      email: '',
      phoneNumber: '',
      password: '',
      confirmPassword: '',
      students: [
        {
          student_name: '',
          school_unit: '',
          grade_level: '',
          date_of_birth: '',
          nisn: ''
        }
      ]
    }
    emailError.value = ''
    passwordError.value = ''
  }

  return {
    // State
    currentStep,
    totalSteps,
    isRegistering,
    emailError,
    passwordError,
    formData,

    // Getters
    isStep1Valid,
    isStep2Valid,

    // Actions
    nextStep,
    prevStep,
    goToStep,
    addStudent,
    removeStudent,
    validateEmail,
    validatePasswordMatch,
    submitRegistration,
    resetForm
  }
})
