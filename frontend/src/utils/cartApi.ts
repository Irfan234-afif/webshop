/**
 * Cart API Utilities
 *
 * Provides functions to interact with the webshop cart API endpoints.
 * Handles cart operations including fetching, adding, updating, and removing items.
 */

import { call } from 'frappe-ui'
import type { CartResponse, AddToCartPayload } from '@/types/cart'

/**
 * Base API method path for cart endpoints
 */
const API_BASE = 'webshop.webshop.api.products'

/**
 * Fetches the current shopping cart with all items
 *
 * @returns Promise<CartResponse> Cart data with items and totals
 * @throws Error if API request fails
 */
export async function getCart(): Promise<CartResponse> {
  try {
    const response = await call(`${API_BASE}.get_cart_items`)
    return response as CartResponse
  } catch (error) {
    console.error('Error fetching cart:', error)
    throw error
  }
}

/**
 * Adds an item to the shopping cart
 *
 * @param payload - Item details to add to cart
 * @param student_name - Student name (optional) to specify which cart to add to
 * @returns Promise<CartResponse> Updated cart data
 * @throws Error if API request fails or validation errors occur
 *
 * @example
 * ```typescript
 * const cart = await addToCart({
 *   item_code: 'ITEM-001',
 *   qty: 2,
 *   additional_notes: 'Gift wrap please'
 * })
 * ```
 */
export async function addToCart(payload: AddToCartPayload, student_name?: string): Promise<CartResponse> {
  try {
    const params = { ...payload }
    if (student_name) {
      params.student = student_name
    }

    const response = await call(`${API_BASE}.add_to_cart`, params)
    return response as CartResponse
  } catch (error) {
    console.error('Error adding to cart:', error)
    throw error
  }
}

/**
 * Updates the quantity of an item in the cart
 *
 * @param item_code - Item code to update
 * @param qty - New quantity (set to 0 to remove item)
 * @param student_name - Student name (optional) to specify which cart to update
 * @returns Promise<CartResponse> Updated cart data
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * // Update quantity
 * const cart = await updateCartItemQty('ITEM-001', 5)
 *
 * // Remove item (set qty to 0)
 * const cart = await updateCartItemQty('ITEM-001', 0)
 * ```
 */
export async function updateCartItemQty(
  item_code: string,
  qty: number,
  quotation_name: string
): Promise<CartResponse> {
  try {
    const params: { item_code: string; qty: number; quotation_name: string } = { item_code, qty, quotation_name }

    const response = await call(`${API_BASE}.update_cart_item_qty`, params)
    return response as CartResponse
  } catch (error) {
    console.error('Error updating cart item quantity:', error)
    throw error
  }
}

/**
 * Removes an item from the shopping cart
 *
 * @param item_code - Item code to remove
 * @param student_name - Student name (optional) to specify which cart to remove from
 * @returns Promise<CartResponse> Updated cart data
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * const cart = await removeFromCart('ITEM-001')
 * ```
 */
export async function removeFromCart(item_code: string, quotation_name: string): Promise<CartResponse> {
  try {
    const params: { item_code: string; quotation_name: string } = { item_code, quotation_name }

    const response = await call(`${API_BASE}.remove_from_cart`, params)
    return response as CartResponse
  } catch (error) {
    console.error('Error removing from cart:', error)
    throw error
  }
}

/**
 * Fetch all student carts with comprehensive details
 *
 * Returns complete cart data for all students including items with variant
 * attributes, stock information, and totals.
 *
 * @returns Promise with all students' cart details
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * const allCarts = await getAllStudentCarts()
 * console.log(allCarts.students) // Array of student carts
 * console.log(allCarts.grand_total) // Total across all students
 * ```
 */
export async function getAllStudentCarts(): Promise<any> {
  try {
    const response = await call('webshop.webshop.api.products.get_all_student_cart_details')
    return response
  } catch (error) {
    console.error('Error fetching all student carts:', error)
    throw error
  }
}

/**
 * Get list of students for current customer
 *
 * @returns Promise<Array> List of students
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * const students = await getStudents()
 * // Returns: [{ name, student_name, school_unit, ... }]
 * ```
 */
export async function getStudents(): Promise<any[]> {
  try {
    const response = await call('webshop.webshop.api.student.get_students')
    return response
  } catch (error) {
    console.error('Error fetching students:', error)
    throw error
  }
}

/**
 * Set active student for shopping session
 *
 * Changes the currently active student. This affects which cart is used for
 * subsequent add-to-cart operations. The selection is persisted via cookie.
 *
 * @param studentName - Student name (DocType name) to set as active
 * @returns Promise<any> Response from server
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * await setActiveStudent('STUDENT-123')
 * ```
 */
export async function setActiveStudent(studentName: string): Promise<any> {
  try {
    const response = await call('webshop.webshop.shopping_cart.student_utils.set_active_student', {
      student_name: studentName
    })
    return response
  } catch (error) {
    console.error('Error setting active student:', error)
    throw error
  }
}

/**
 * Get the currently active student
 *
 * @returns Promise with active student name
 * @throws Error if API request fails
 *
 * @example
 * ```typescript
 * const activeStudent = await getActiveStudent()
 * ```
 */
export async function getActiveStudent(): Promise<any> {
  try {
    const response = await call('webshop.webshop.shopping_cart.student_utils.get_active_student_name')
    return response.student_name
  } catch (error) {
    console.error('Error getting active student:', error)
    throw error
  }
}

/**
 * Helper function to get variant display text
 * Formats variant attributes into a readable string
 *
 * @param variantAttributes - Array of variant attributes
 * @returns Formatted string like "Size: M, Color: Red"
 *
 * @example
 * ```typescript
 * const display = getVariantDisplayText([
 *   { attribute: 'Size', value: 'M', label: 'Size', displayValue: 'M' },
 *   { attribute: 'Color', value: 'Red', label: 'Color', displayValue: 'Red' }
 * ])
 * // Returns: "Size: M, Color: Red"
 * ```
 */
export function getVariantDisplayText(
  variantAttributes?: Array<{ attribute: string; value: string }>
): string {
  if (!variantAttributes || variantAttributes.length === 0) {
    return ''
  }

  return variantAttributes
    .map(attr => `${attr.attribute}: ${attr.value}`)
    .join(', ')
}
