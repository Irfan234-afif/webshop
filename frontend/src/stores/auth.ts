import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'
import { getCookie } from '@/utils/storage'

interface User {
  email: string
  full_name: string
  user_type: string
  phone?: string
}

interface Customer {
  name: string
  customer_name: string
}

interface Student {
  student_id: string
  student_name: string
  school_unit: string
  grade_level: string
  is_active: number
}

interface AuthState {
  user: User | null
  customer: Customer | null
  students: Student[]
  isAuthenticated: boolean
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const customer = ref<Customer | null>(null)
  const students = ref<Student[]>([])
  const isAuthenticated = ref(!!getCookie('user_id') && getCookie('user_id') !== 'Guest')
  const isLoading = ref(true)

  const stripHtml = (html: string) => {
    const tmp = document.createElement("DIV")
    tmp.innerHTML = html
    return tmp.textContent || tmp.innerText || ""
  }

  // Check current user status
  const fetchCurrentUser = async (): Promise<void> => {
    isLoading.value = true
    try {
      const response = await call('webshop.webshop.api.auth.get_current_user')

      if (response.success && response.user) {
        user.value = response.user
        customer.value = response.customer
        console.log("customer : ", response.customer);
        students.value = response.students || []
        isAuthenticated.value = true
      } else {
        user.value = null
        customer.value = null
        students.value = []
        isAuthenticated.value = false
      }
    } catch (error) {
      console.error('Error fetching current user:', error)
      user.value = null
      customer.value = null
      students.value = []
      isAuthenticated.value = false
    } finally {
      isLoading.value = false
    }
  }

  // Login function
  const login = async (email: string, password: string): Promise<{ success: boolean; message?: string }> => {
    try {
      const response = await call('webshop.webshop.api.auth.login', {
        email,
        password
      })

      if (response.success) {
        user.value = response.user
        customer.value = response.customer
        students.value = response.students || []
        isAuthenticated.value = true
        return { success: true }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, message: 'Login failed' }
    }
  }

  // Logout function
  const logout = async (): Promise<void> => {
    try {
      await call('webshop.webshop.api.auth.logout')
      user.value = null
      customer.value = null
      students.value = []
      isAuthenticated.value = false
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  // Forgot Password function
  const forgotPassword = async (email: string): Promise<{ success: boolean; message?: string }> => {
    try {
      const response = await call('webshop.webshop.api.auth.reset_password', {
        email
      })

      if (response.success) {
        return { success: true, message: response.message }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('Forgot password error:', error)
      return { success: false, message: 'Gagal memproses permintaan' }
    }
  }

    // Update Profile function
  const updateProfile = async (fullName: string, phone: string): Promise<{ success: boolean; message?: string }> => {
    try {
      const response = await call('webshop.webshop.api.auth.update_profile', {
        full_name: fullName,
        phone: phone
      })

      if (response.success) {
        // Update local state
        if (user.value) {
            user.value.full_name = fullName
            user.value.phone = phone
        }
        return { success: true, message: response.message }
      } else {
        return { success: false, message: response.message }
      }
    } catch (error) {
      console.error('Update profile error:', error)
      return { success: false, message: 'Update profile failed' }
    }
  }

  // Update Password function
  const updateUserPassword = async (newPassword: string, key?: string, oldPassword?: string): Promise<{ success: boolean; message?: string }> => {
    try {
      const response = await call('frappe.core.doctype.user.user.update_password', {
        new_password: newPassword,
        key: key || undefined,
        old_password: oldPassword || undefined,
        logout_all_sessions: 1
      })

      return { success: true, message: 'Kata sandi berhasil diperbarui' }
    } catch (error: any) {
      console.error('Update password error:', error)
      let message = error.message || 'Gagal memperbarui kata sandi'
      
      if (error.messages && error.messages.length > 0) {
        message = stripHtml(error.messages[0])
      }
      
      return { success: false, message }
    }
  }

  // Check if user is a guest (not authenticated)
  const isGuest = computed(() => {
    return !isAuthenticated.value
  })

  return {
    // State
    user,
    customer,
    students,
    isAuthenticated,
    isLoading,

    // Getters
    isGuest,

    // Actions
    fetchCurrentUser,
    login,
    logout,
    forgotPassword,
    updateProfile,
    updateUserPassword
  }
})