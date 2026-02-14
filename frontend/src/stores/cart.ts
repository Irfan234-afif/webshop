import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, AddToCartPayload, Student, StudentCart } from '@/types/cart'
import * as cartApi from '@/utils/cartApi'
import { getCookie } from '@/utils/storage'

export const useCartStore = defineStore('cart', () => {
  // State
  const students = ref<Student[]>([])
  const studentCarts = ref<StudentCart[]>([])
  const selectedStudentCart = ref<StudentCart | null>(null)
  const activeStudent = ref<string | null>(getCookie('active_student') ? decodeURIComponent(getCookie('active_student')!) : null)
  const items = ref<CartItem[]>([])
  const total = ref<number>(0)
  const isLoading = ref(false)
  const error = ref<Error | null>(null)
  const allowItemsNotInStock = ref(false)

  // Getters
  const itemCount = computed(() => {
    // Calculate total item count from all student carts
    return studentCarts.value.reduce((total, cart) => {
      const cartItemCount = cart.items?.reduce((sum, item) => sum + item.quantity, 0) || 0
      return total + cartItemCount
    }, 0)
  })

  const totalPrice = computed(() => {
    // Use total from backend if available, otherwise calculate
    if (total.value > 0) {
      return total.value
    }
    return items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
  })

  const hasItem = (itemCode: string) =>
    items.value.some(item => item.item_code === itemCode)

  const getItemQuantity = (itemCode: string): number => {
    const item = items.value.find(i => i.item_code === itemCode)
    return item?.quantity || 0
  }

  const getItemByCode = (itemCode: string) => {
    return items.value.find(i => i.item_code === itemCode)
  }

  const activeStudentName = computed(() => {
    if (!activeStudent.value) return ''
    const student = students.value.find(s => s.name === activeStudent.value)
    return student ? student.student_name : ""
  })

  // Actions

  /**
   * Fetch all students and their carts from backend API
   * This is the primary function for loading multi-student cart data
   */
  const fetchAllStudentCarts = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await cartApi.getAllStudentCarts()
      studentCarts.value = response.students as StudentCart[]
      allowItemsNotInStock.value = !!response.allowItemsNotInStock

      selectedStudentCart.value = studentCarts.value.find(sc => sc.name === activeStudent.value) || null
    } catch (e) {
      error.value = e as Error
      console.error('Failed to fetch student carts:', e)

      // Reset on error
      students.value = []
      items.value = []
      total.value = 0
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch cart items from backend API (single student cart)
   * For backward compatibility - uses current active student
   */
  const fetchCart = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await cartApi.getCart()

      items.value = response.items
      total.value = response.total

      console.log('Cart fetched successfully:', response)
    } catch (e) {
      error.value = e as Error
      console.error('Failed to fetch cart:', e)

      // On error, reset to empty cart
      items.value = []
      total.value = 0
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch list of students for current customer
   */
  const fetchStudents = async () => {
    try {
      const response = await cartApi.getStudents()
      students.value = response.map((s: any) => ({
        name: s.name, // Student DocType name (unique identifier)
        student_name: s.student_name, // Student's display name
        school_unit: s.school_unit,
        grade_level: s.grade_level,
        date_of_birth: s.date_of_birth,
        is_active: s.is_active,
        is_primary: s.is_primary,
        notes: s.notes
      }))
      console.log('Students fetched:', students.value)
    } catch (e) {
      console.error('Failed to fetch students:', e)
      throw e
    }
  }

  /**
   * Set active student for shopping session
   */
  const setActiveStudent = async (student: Student | string) => {
    try {
      const studentName = typeof student === 'string' ? student : student.name
      await cartApi.setActiveStudent(studentName)
      activeStudent.value = studentName
      localStorage.setItem('active_student', studentName)
      console.log('Active student set to:', studentName)
    } catch (e) {
      console.error('Failed to set active student:', e)
      throw e
    }
  }

  /**
   * Add item to cart via backend API
   * Requires student to specify which student's cart
   */
  const addToCart = async (payload: AddToCartPayload) => {
    isLoading.value = true
    error.value = null

    try {
      // Validate student is provided
      if (!payload.student) {
        throw new Error('student is required for adding items to cart')
      }

      await cartApi.addToCart(payload, payload.student)

      // Refresh all student carts after adding
      await fetchAllStudentCarts()

      console.log('Added to cart:', payload)
    } catch (e) {
      error.value = e as Error
      console.error('Failed to add to cart:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update item quantity in cart
   */
  const updateQuantity = async (itemCode: string, quantity: number, quotation_name: string) => {
    isLoading.value = true
    error.value = null

    try {
      // Get the active student to ensure we're updating the correct cart
      await cartApi.updateCartItemQty(itemCode, quantity, quotation_name)

      // Refresh all student carts after updating
      await fetchAllStudentCarts()

      console.log('Updated cart item quantity:', itemCode, quantity)
    } catch (e) {
      error.value = e as Error
      console.error('Failed to update cart item quantity:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Remove item from cart
   */
  const removeItem = async (itemCode: string, quotation_name: string) => {
    isLoading.value = true
    error.value = null

    try {
      await cartApi.removeFromCart(itemCode, quotation_name)

      // Refresh all student carts after removing
      await fetchAllStudentCarts()

      console.log('Removed item from cart:', itemCode)
    } catch (e) {
      error.value = e as Error
      console.error('Failed to remove item from cart:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Clear entire cart (local state only - use with caution)
   */
  const clearCart = () => {
    items.value = []
    total.value = 0
  }

  const resetState = () => {
    students.value = []
    studentCarts.value = []
    selectedStudentCart.value = null
    activeStudent.value = null
    items.value = []
    total.value = 0
    error.value = null
    localStorage.removeItem('active_student')
  }

  const getItemsByStudent = (studentName: string) => {
    return items.value.filter(item => item.student === studentName)
  }

  const getStudentCartTotal = (studentName: string) => {
    return getItemsByStudent(studentName).reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    )
  }

  const getStudentItemCount = (studentName: string) => {
    return getItemsByStudent(studentName).reduce(
      (sum, item) => sum + item.quantity,
      0
    )
  }

  /**
   * Initialize the cart store with student data
   */
  const initialize = async () => {
    if (students.value.length === 0) {
      await fetchStudents()
    }
    // Try to get active student from cookie first
    const storedActiveStudent = getCookie('active_student')
    activeStudent.value = storedActiveStudent ? decodeURIComponent(storedActiveStudent) : null
    
    // If no active student, select the primary student
    if (!activeStudent.value && students.value.length > 0) {
      const primaryStudent = students.value.find(s => s.is_primary)
      if (primaryStudent) {
        await setActiveStudent(primaryStudent)
        console.log('Auto-selected primary student:', primaryStudent.student_name)
      } else {
        // Fallback: select the first student if no primary is set
        const firstStudent = students.value[0]
        if (firstStudent) {
          await setActiveStudent(firstStudent)
          console.log('Auto-selected first student:', firstStudent.student_name)
        }
      }
    }
    
    // Fetch all student carts to get the current state from backend
    // This ensures we have the most up-to-date information
    await fetchAllStudentCarts()
  }

  return {
    // State
    items,
    students,
    studentCarts,
    activeStudent,
    isLoading,
    error,
    total,
    selectedStudentCart,
    allowItemsNotInStock,
    // Getters
    itemCount,
    totalPrice,
    hasItem,
    getItemQuantity,
    getItemByCode,
    getItemsByStudent,
    getStudentCartTotal,
    getStudentItemCount,
    activeStudentName,
    // Actions
    fetchAllStudentCarts,
    fetchCart,
    fetchStudents,
    setActiveStudent,
    addToCart,
    updateQuantity,
    removeItem,
    clearCart,
    resetState,
    initialize
  }
})
