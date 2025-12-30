# Student Management API Documentation
## Multi-Student Account Management

Complete API reference for managing students under customer accounts and per-student cart switching.

---

## Overview

The Student Management system allows parents (customers) to:
- Add multiple students/children to their account
- Switch between students when shopping
- Maintain separate shopping carts per student
- View all student carts at once

**Key Concept:** Only one student can be "active" at a time. The active student determines which cart is used for shopping operations.

---

## Base URL

```
/api/method/webshop.webshop.api.student
```

For session management:
```
/api/method/webshop.webshop.shopping_cart.student_utils
```

---

## API Endpoints

### 0. Add To Cart

**Endpoint:** `POST /api/method/webshop.webshop.api.products.add_to_cart`

**Description:** Add an item to the shopping cart for the specified student

**Authentication:** Required

**Request Body:**

```json
{
  "item_code": "ITEM-001",
  "qty": 2,
  "additional_notes": "Gift wrap please",
  "student": "CUST-00001-ABC123"  // Student DocType name (optional, defaults to active student)
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_code | string | Yes | The item to add to cart |
| qty | number | No | Quantity to add (default: 1) |
| additional_notes | string | No | Additional notes for the item |
| student | string | No | Student DocType name to add to specific student's cart |

**Success Response (200 OK):**

```json
{
  "message": {
    "name": "QTN-CART-2024-00001",
    "student": "CUST-00001-ABC123",
    "items": [...],
    "total_qty": 3,
    "grand_total": 150.00
  }
}
```

---

### 1. Get Students

**Endpoint:** `GET /api/method/webshop.webshop.api.student.get_students`

**Description:** Get all students for the currently logged-in customer

**Authentication:** Required

**Request:** No parameters

**Success Response (200 OK):**

```json
{
  "message": [
    {
      "name": "CUST-00001-ABC123",  // Student DocType name (unique identifier)
      "student_name": "Alice Doe",   // Student's display name
      "school_unit": "High School",
      "grade_level": "Grade 10",
      "date_of_birth": "2010-05-15",
      "is_active": 1,
      "is_primary": 0,
      "notes": null
    },
    {
      "name": "CUST-00001-XYZ789",   // Student DocType name (unique identifier)
      "student_name": "Bob Doe",     // Student's display name
      "school_unit": "Elementary",
      "grade_level": "Grade 5",
      "date_of_birth": "2012-08-20",
      "is_active": 1,
      "is_primary": 0,
      "notes": null
    }
  ]
}
```

**Error Response (403 Forbidden):**

```json
{
  "message": "Not authenticated"
}
```

---

### 2. Add Student

**Endpoint:** `POST /api/method/webshop.webshop.api.student.add_student`

**Description:** Add a new student to the current customer account

**Authentication:** Required

**Request Body:**

```json
{
  "student_name": "Charlie Doe",
  "school_unit": "Middle School",
  "grade_level": "Grade 7",
  "date_of_birth": "2011-03-10"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_name | string | Yes | Student's full name |
| school_unit | string | Yes | School Unit name (must exist) |
| grade_level | string | No | Student's grade level |
| date_of_birth | string | No | Date in YYYY-MM-DD format |

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "student_id": "CUST-00001-DEF456",
    "message": "Student added successfully"
  }
}
```

**Error Response (400 Bad Request):**

```json
{
  "message": {
    "success": false,
    "message": "School Unit 'Invalid Unit' does not exist"
  }
}
```

---

### 3. Update Student

**Endpoint:** `POST /api/method/webshop.webshop.api.student.update_student`

**Description:** Update student information

**Authentication:** Required

**Request Body:**

```json
{
  "student_name": "CUST-00001-ABC123",  // Student DocType name (unique identifier)
  "new_student_name": "Alice Marie Doe",  // Updated display name (optional)
  "school_unit": "High School",  // Updated school unit (optional)
  "grade_level": "Grade 11",  // Updated grade level (optional)
  "date_of_birth": "2010-05-15"  // Updated date of birth (optional)
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_name | string | Yes | Student DocType name (unique identifier) to update |
| new_student_name | string | No | Updated display name |
| school_unit | string | No | Updated school unit |
| grade_level | string | No | Updated grade level |
| date_of_birth | string | No | Updated date of birth |
| is_active | number | No | Updated active status (0 or 1) |

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "message": "Student updated successfully"
  }
}
```

**Error Response (404 Not Found):**

```json
{
  "message": {
    "success": false,
    "message": "Student not found"
  }
}
```

---

### 4. Delete Student

**Endpoint:** `POST /api/method/webshop.webshop.api.student.delete_student`

**Description:** Delete a student from the account

**Authentication:** Required

**Request Body:**

```json
{
  "student_name": "CUST-00001-ABC123"  // Student DocType name (unique identifier) to delete
}
```

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "message": "Student deleted successfully"
  }
}
```

**Error Response (403 Forbidden):**

```json
{
  "message": {
    "success": false,
    "message": "Student does not belong to your account"
  }
}
```

**Note:** Deleting a student does NOT delete their existing orders. Historical data is preserved.

---

### 5. Update Cart Item Quantity

**Endpoint:** `POST /api/method/webshop.webshop.api.products.update_cart_item_qty`

**Description:** Update the quantity of an item in the shopping cart for the specified student

**Authentication:** Required

**Request Body:**

```json
{
  "item_code": "ITEM-001",
  "qty": 3,
  "student_name": "CUST-00001-ABC123"  // Student DocType name (optional, defaults to active student)
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_code | string | Yes | The item code to update |
| qty | number | Yes | New quantity (set to 0 to remove item) |
| student_name | string | No | Student DocType name to specify which cart to update |

**Success Response (200 OK):**

```json
{
  "message": {
    "name": "QTN-CART-2024-00001",
    "student": "CUST-00001-ABC123",
    "items": [...],
    "total_qty": 3,
    "grand_total": 150.00
  }
}
```

---

### 6. Set Active Student

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.student_utils.set_active_student`

**Description:** Set the active student for shopping. This determines which cart is used.

**Authentication:** Required

**Request Body:**

```json
{
  "student_name": "CUST-00001-ABC123"  // Student DocType name (unique identifier)
}
```

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "student_name": "CUST-00001-ABC123",
    "student_display_name": "Alice Doe",
    "school_unit": "High School"
  }
}
```

**Side Effects:**
- Sets `frappe.session.active_student` in backend (was `active_student_id`)
- Sets `active_student` cookie in browser (expires in 30 days, was `active_student_id`)
- All subsequent cart operations use this student's cart

**Error Response (403 Forbidden):**

---

### 7. Remove From Cart

**Endpoint:** `POST /api/method/webshop.webshop.api.products.remove_from_cart`

**Description:** Remove an item from the shopping cart for the specified student

**Authentication:** Required

**Request Body:**

```json
{
  "item_code": "ITEM-001",
  "student_name": "CUST-00001-ABC123"  // Student DocType name (optional, defaults to active student)
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_code | string | Yes | The item code to remove from cart |
| student_name | string | No | Student DocType name to specify which cart to remove from |

**Success Response (200 OK):**

```json
{
  "message": {
    "name": "QTN-CART-2024-00001",
    "student": "CUST-00001-ABC123",
    "items": [...],
    "total_qty": 2,
    "grand_total": 100.00
  }
}
```

---

**Error Response (403 Forbidden):**

```json
{
  "message": {
    "success": false,
    "message": "Student does not belong to your account"
  }
}
```

---

### 6. Get Customer Students

**Endpoint:** `GET /api/method/webshop.webshop.shopping_cart.student_utils.get_customer_students`

**Description:** Alternative endpoint to get students (same as get_students)

**Authentication:** Required

**Response:** Same as `get_students` endpoint

---

### 7. Clear Active Student

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.student_utils.clear_active_student`

**Description:** Clear the active student selection

**Authentication:** Required

**Request:** No body required

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true
  }
}
```

**Side Effects:**
- Clears `frappe.session.active_student_id`
- Deletes `active_student_id` cookie
- Cart operations will use default behavior (no student linkage)

---

### 8. Get Cart By Student

**Endpoint:** `GET /api/method/webshop.webshop.api.student.get_cart_by_student`

**Description:** Get cart for a specific student without setting them as active

**Authentication:** Required

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| student_name | string | Yes | Student DocType name (unique identifier) to get cart for |

**Example:**

```
GET /api/method/webshop.webshop.api.student.get_cart_by_student?student_name=CUST-00001-ABC123
```

**Success Response (200 OK):**

```json
{
  "message": {
    "name": "QTN-CART-2024-00001",
    "grand_total": 150.00,
    "total_qty": 3,
    "student": "CUST-00001-ABC123",  // Student DocType name
    "student_display_name": "Alice Doe",  // Student's display name
    "items": [
      {
        "item_code": "ITEM-001",
        "item_name": "School Uniform",
        "qty": 1,
        "rate": 50.00
      }
    ]
  }
}
```

**Response (No Cart):**

```json
{
  "message": null
}
```

---

### 9. Get All Student Carts

**Endpoint:** `GET /api/method/webshop.webshop.api.student.get_all_student_carts`

**Description:** Get cart summaries for all students at once

**Authentication:** Required

**Request:** No parameters

**Success Response (200 OK):**

```json
{
  "message": [
    {
      "student_name": "CUST-00001-ABC123",  // Student DocType name (unique identifier)
      "student_display_name": "Alice Doe",  // Student's display name
      "school_unit": "High School",
      "is_active": 1,
      "is_primary": 0,
      "cart": {
        "name": "QTN-CART-2024-00001",
        "grand_total": 150.00,
        "total_qty": 3
      }
    },
    {
      "student_name": "CUST-00001-XYZ789",  // Student DocType name (unique identifier)
      "student_display_name": "Bob Doe",    // Student's display name
      "school_unit": "Elementary",
      "is_active": 1,
      "is_primary": 0,
      "cart": null
    }
  ]
}
```

**Use Case:** Display a dashboard showing all children and their cart status.

---

## Frontend Integration

### Complete Student Management Flow

```typescript
// stores/students.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Student {
  name: string              // Student DocType name (unique identifier)
  student_name: string      // Student's display name
  school_unit: string
  grade_level?: string
  date_of_birth?: string
  is_active: number
  is_primary: number
  notes?: string
}

export const useStudentsStore = defineStore('students', () => {
  const students = ref<Student[]>([])
  const activeStudent = ref<string | null>(null)

  // Fetch all students
  async function fetchStudents() {
    const response = await fetch(
      '/api/method/webshop.webshop.api.student.get_students',
      { credentials: 'include' }
    )
    const data = await response.json()
    students.value = data.message
  }

  // Add new student
  async function addStudent(studentData: {
    student_name: string
    school_unit: string
    grade_level?: string
    date_of_birth?: string
  }) {
    const response = await fetch(
      '/api/method/webshop.webshop.api.student.add_student',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(studentData)
      }
    )

    const data = await response.json()

    if (!data.message.success) {
      throw new Error(data.message.message)
    }

    // Refresh student list
    await fetchStudents()

    return data.message.student_name  // Changed from student_id to student_name
  }

  // Set active student for shopping
  async function setActiveStudent(studentName: string) {
    const response = await fetch(
      '/api/method/webshop.webshop.shopping_cart.student_utils.set_active_student',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ student_name: studentName })  // Changed from student_id to student_name
      }
    )

    const data = await response.json()

    if (data.message.success) {
      activeStudent.value = studentName  // Changed from activeStudentId to activeStudent
    }

    return data.message
  }

  // Get all carts overview
  async function fetchAllCarts() {
    const response = await fetch(
      '/api/method/webshop.webshop.api.student.get_all_student_carts',
      { credentials: 'include' }
    )

    const data = await response.json()
    return data.message
  }

  return {
    students,
    activeStudent,
    fetchStudents,
    addStudent,
    setActiveStudent,
    fetchAllCarts
  }
})
```

### Cart Operations with Students

```typescript
// utils/cartApi.ts
import { call } from 'frappe-ui'
import type { CartResponse, AddToCartPayload } from '@/types/cart'

// Add to cart with student parameter
export async function addToCart(payload: AddToCartPayload, student_name?: string): Promise<CartResponse> {
  try {
    const params = { ...payload }
    if (student_name) {
      params.student_name = student_name
    }

    const response = await call('webshop.webshop.api.products.add_to_cart', params)
    return response as CartResponse
  } catch (error) {
    console.error('Error adding to cart:', error)
    throw error
  }
}

// Update cart item quantity with student parameter
export async function updateCartItemQty(
  item_code: string,
  qty: number,
  student_name?: string
): Promise<CartResponse> {
  try {
    const params: { item_code: string; qty: number; student_name?: string } = { item_code, qty }
    if (student_name) {
      params.student_name = student_name
    }

    const response = await call('webshop.webshop.api.products.update_cart_item_qty', params)
    return response as CartResponse
  } catch (error) {
    console.error('Error updating cart item quantity:', error)
    throw error
  }
}

// Remove from cart with student parameter
export async function removeFromCart(item_code: string, student_name?: string): Promise<CartResponse> {
  try {
    const params: { item_code: string; student_name?: string } = { item_code }
    if (student_name) {
      params.student_name = student_name
    }

    const response = await call('webshop.webshop.api.products.remove_from_cart', params)
    return response as CartResponse
  } catch (error) {
    console.error('Error removing from cart:', error)
    throw error
  }
}
```

### Vue Component Example

```vue
<template>
  <div class="student-selector">
    <h3>Select Student</h3>

    <div class="student-grid">
      <div
        v-for="student in students"
        :key="student.name"
        class="student-card"
        :class="{ active: student.name === activeStudent }"
        @click="selectStudent(student.name)"
      >
        <div class="student-name">{{ student.student_name }}</div>
        <div class="student-unit">{{ student.school_unit }}</div>
        <div class="student-grade">{{ student.grade_level }}</div>
      </div>

      <div class="add-student-card" @click="showAddStudentModal = true">
        <span>+ Add Student</span>
      </div>
    </div>

    <!-- Add Student Modal -->
    <AddStudentModal
      v-if="showAddStudentModal"
      @close="showAddStudentModal = false"
      @added="onStudentAdded"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useStudentsStore } from '@/stores/students'
import { useCartStore } from '@/stores/cart'

const studentsStore = useStudentsStore()
const cartStore = useCartStore()

const showAddStudentModal = ref(false)

const { students, activeStudent } = studentsStore

onMounted(async () => {
  await studentsStore.fetchStudents()

  // Restore active student from cookie if exists
  const savedStudentName = getCookie('active_student')  // Changed from active_student_id to active_student
  if (savedStudentName) {
    await selectStudent(savedStudentName)
  }
})

async function selectStudent(studentName: string) {
  try {
    await studentsStore.setActiveStudent(studentName)  // Changed from studentId to studentName

    // Refresh cart for new student
    await cartStore.fetchCart()

    // Show success message
    console.log('Switched to student:', studentName)  // Changed from studentId to studentName
  } catch (error) {
    console.error('Failed to switch student:', error)
  }
}

async function onStudentAdded() {
  showAddStudentModal.value = false
  await studentsStore.fetchStudents()
}

function getCookie(name: string) {
  const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'))
  return match ? match[2] : null
}
</script>
```

### Multi-Cart Dashboard Example

```vue
<template>
  <div class="carts-dashboard">
    <h2>All Carts</h2>

    <div class="carts-grid">
      <div v-for="item in carts" :key="item.student_id" class="cart-summary">
        <h3>{{ item.student_name }}</h3>
        <p class="school-unit">{{ item.school_unit }}</p>

        <div v-if="item.cart" class="cart-info">
          <p>Items: {{ item.cart.total_qty }}</p>
          <p class="total">Total: ${{ item.cart.grand_total }}</p>
          <button @click="viewCart(item.student_id)">View Cart</button>
        </div>

        <div v-else class="no-cart">
          <p>No items in cart</p>
          <button @click="startShopping(item.student_id)">Start Shopping</button>
        </div>
      </div>
    </div>

    <button class="checkout-all" @click="checkoutAll">
      Checkout All Carts
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStudentsStore } from '@/stores/students'

const router = useRouter()
const studentsStore = useStudentsStore()

const carts = ref([])

onMounted(async () => {
  carts.value = await studentsStore.fetchAllCarts()
})

async function viewCart(studentId: string) {
  await studentsStore.setActiveStudent(studentId)
  router.push('/cart')
}

async function startShopping(studentId: string) {
  await studentsStore.setActiveStudent(studentId)
  router.push('/products')
}

async function checkoutAll() {
  // Implement batch checkout logic
  console.log('Checkout all carts')
}
</script>
```

---

## Cookie Persistence

The `active_student` cookie is automatically set when calling `set_active_student`:

**Cookie Details:**
- **Name:** `active_student`  // Changed from active_student_id
- **Value:** Student DocType name (e.g., "CUST-00001-ABC123")
- **Expires:** 30 days from setting
- **HttpOnly:** No (accessible via JavaScript)
- **Secure:** Yes (in production with HTTPS)

**Reading Cookie:**

```typescript
function getActiveStudentFromCookie(): string | null {
  const match = document.cookie.match(/active_student=([^;]+)/)  // Changed from active_student_id
  return match ? match[1] : null
}

// Use on app initialization
const savedStudentName = getActiveStudentFromCookie()  // Changed from savedStudentId
if (savedStudentName) {
  await studentsStore.setActiveStudent(savedStudentName)  // Changed from savedStudentId
}
```

---

## Best Practices

### 1. Always Set Active Student Before Shopping

```typescript
// WRONG: Adding to cart without selecting student
await cartStore.addItem(itemCode, qty) // Cart has no student linkage

// CORRECT: Select student first
await studentsStore.setActiveStudent(studentName)  // Changed from studentId
await cartStore.addItem(itemCode, qty) // Cart linked to student
```

### 2. Restore Active Student on Page Load

```typescript
// App initialization
async function initializeApp() {
  await authStore.checkAuth()

  if (authStore.isAuthenticated) {
    await studentsStore.fetchStudents()

    // Restore from cookie
    const savedStudentName = getActiveStudentFromCookie()  // Changed from savedStudentId
    if (savedStudentName && studentsStore.students.find(s => s.name === savedStudentName)) {  // Changed from student_id to name
      await studentsStore.setActiveStudent(savedStudentName)  // Changed from savedStudentId
    } else if (studentsStore.students.length > 0) {
      // Auto-select first student if none saved
      await studentsStore.setActiveStudent(studentsStore.students[0].name)  // Changed from student_id to name
    }
  }
}
```

### 3. Prompt Student Selection If None Active

```typescript
// In cart page or product page
onMounted(() => {
  if (!studentsStore.activeStudent && studentsStore.students.length > 0) {  // Changed from activeStudentId to activeStudent
    // Show modal: "Please select a student to continue shopping"
    showStudentSelectorModal.value = true
  }
})
```

### 4. Validate Student Ownership

```typescript
// Before operations, verify student belongs to current user
const student = studentsStore.students.find(s => s.name === studentName)  // Changed from student_id to name
if (!student) {
  throw new Error('Invalid student')
}
```

---

## Error Handling

```typescript
async function handleStudentOperation() {
  try {
    await studentsStore.setActiveStudent(studentId)
  } catch (error: any) {
    if (error.response?.status === 403) {
      // Student doesn't belong to user
      showError('This student does not belong to your account')
    } else if (error.response?.status === 404) {
      // Student not found
      showError('Student not found')
    } else {
      showError('An error occurred. Please try again.')
    }
  }
}
```

---

## Testing

### cURL Examples

```bash
# Get students
curl -X GET http://localhost:8080/api/method/webshop.webshop.api.student.get_students \
  -b cookies.txt

# Add student
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.student.add_student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "student_name": "New Student",
    "school_unit": "High School",
    "grade_level": "Grade 9"
  }'

# Set active student
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.student_utils.set_active_student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -c cookies.txt \
  -d '{"student_name": "CUST-00001-ABC123"}'  # Changed from student_id to student_name

# Get all carts
curl -X GET http://localhost:8080/api/method/webshop.webshop.api.student.get_all_student_carts \
  -b cookies.txt
```

---

## TypeScript Types

```typescript
// types/student.ts
export interface Student {
  name: string              // Student DocType name (unique identifier)
  student_name: string      // Student's display name
  school_unit: string
  grade_level?: string
  date_of_birth?: string
  is_active: number
  is_primary: number
  notes?: string
}

export interface StudentCart {
  student_name: string      // Student DocType name (unique identifier)
  student_display_name: string  // Student's display name
  school_unit: string
  is_active: number
  is_primary: number
  cart: {
    name: string
    grand_total: number
    total_qty: number
  } | null
}

export interface AddStudentRequest {
  student_name: string
  school_unit: string
  grade_level?: string
  date_of_birth?: string
  is_primary?: number
}

export interface SetActiveStudentRequest {
  student_name: string      // Changed from student_id to student_name
}

export interface CartApiRequest {
  item_code: string
  qty?: number
  additional_notes?: string
  student_name?: string      // Student DocType name (optional)
}

export interface CartApiResponse {
  name: string
  student?: string          // Student DocType name (if cart is linked to student)
  items: Array<{
    item_code: string
    item_name: string
    qty: number
    rate: number
    amount: number
  }>
  total_qty: number
  grand_total: number
}
```

---

## Changelog

**v1.0.0** (2024-12-20)
- Initial student management API implementation
- Per-student cart isolation
- Session-based student selection
- Cookie persistence for active student

---

**[← Back to API Documentation](../README.md)**
