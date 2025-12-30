# Shopping Cart API Documentation
## Per-Student Cart Management

Complete API reference for managing shopping carts with per-student isolation.

---

## Overview

The Shopping Cart system provides:
- **Per-student carts**: Each student has their own separate cart
- **Session-based**: Cart determined by active student selection
- **Persistent**: Carts saved as Quotations in database
- **Complete workflow**: Add items → Update → Checkout → Create Sales Order

**Important:** Cart operations use the currently active student. Call `set_active_student` before cart operations.

---

## Base URL

```
/api/method/webshop.webshop.shopping_cart.cart
```

---

## How Carts Work

### Cart = Quotation

Behind the scenes, a cart is a **Quotation** document with:
- `order_type = "Shopping Cart"`
- `docstatus = 0` (draft)
- `student_id` = Active student's ID
- `party_name` = Customer name
- `contact_email` = User email

### Cart Identification

Each cart is uniquely identified by:
```
party_name + contact_email + order_type + student_id
```

Switching students switches carts automatically.

---

## API Endpoints

### 1. Get Cart Quotation

**Endpoint:** `GET /api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation`

**Description:** Get the current cart for the active student

**Authentication:** Required

**Request:** No parameters required (uses active student from session)

**Success Response (200 OK):**

```json
{
  "message": {
    "doc": {
      "name": "QTN-CART-2024-00001",
      "doctype": "Quotation",
      "party_name": "CUST-00001",
      "contact_email": "parent@example.com",
      "order_type": "Shopping Cart",
      "student_id": "CUST-00001-ABC123",
      "student_name": "Alice Doe",
      "school_unit": "High School",
      "grand_total": 250.00,
      "total_qty": 5,
      "currency": "USD",
      "items": [
        {
          "item_code": "ITEM-001",
          "item_name": "School Uniform",
          "qty": 2,
          "rate": 50.00,
          "amount": 100.00,
          "description": "Blue uniform set"
        },
        {
          "item_code": "ITEM-002",
          "item_name": "Backpack",
          "qty": 1,
          "rate": 75.00,
          "amount": 75.00
        }
      ]
    },
    "shipping_addresses": [
      {
        "name": "Address-001",
        "address_line1": "123 Main St",
        "city": "New York",
        "state": "NY",
        "country": "United States"
      }
    ],
    "billing_addresses": [
      {
        "name": "Address-002",
        "address_line1": "456 Elm St",
        "city": "Boston",
        "state": "MA"
      }
    ]
  }
}
```

**Response (Empty Cart):**

```json
{
  "message": {
    "doc": {
      "name": "QTN-CART-2024-00002",
      "items": [],
      "grand_total": 0,
      "total_qty": 0,
      "student_id": "CUST-00001-ABC123"
    },
    "shipping_addresses": [],
    "billing_addresses": []
  }
}
```

**Use Case:** Display cart page, show cart icon badge count

---

### 2. Update Cart

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.cart.update_cart`

**Description:** Add, update, or remove items from cart

**Authentication:** Required

**Request Body:**

```json
{
  "item_code": "ITEM-001",
  "qty": 3,
  "additional_notes": "Size: Large",
  "with_items": true
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_code | string | Yes | Item code to add/update |
| qty | number | Yes | Quantity (set to 0 to remove item) |
| additional_notes | string | No | Notes for this item |
| with_items | boolean | No | Return full cart with items (default: true) |

**Success Response (200 OK):**

```json
{
  "message": {
    "name": "QTN-CART-2024-00001",
    "grand_total": 350.00,
    "total_qty": 6,
    "items": [
      {
        "item_code": "ITEM-001",
        "item_name": "School Uniform",
        "qty": 3,
        "rate": 50.00,
        "amount": 150.00
      }
    ]
  }
}
```

**Examples:**

```typescript
// Add item
await updateCart('ITEM-001', 2)

// Update quantity
await updateCart('ITEM-001', 5)

// Remove item
await updateCart('ITEM-001', 0)
```

---

### 3. Place Order (Checkout)

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.cart.place_order`

**Description:** Convert cart to Sales Order and process checkout

**Authentication:** Required

**Request:** No body required (uses current cart)

**Success Response (200 OK):**

```json
{
  "message": "SO-2024-00001"
}
```

Returns the Sales Order name.

**Side Effects:**
- Creates **Sales Order** from cart Quotation
- Copies `student_id`, `student_name`, `school_unit` to Sales Order
- Marks Quotation as submitted (`docstatus = 1`)
- Clears cart (new empty cart created for next order)
- Triggers payment workflow if configured

**Error Response (400 Bad Request):**

```json
{
  "message": "Cart is empty"
}
```

**Error Response (400 - Missing Address):**

```json
{
  "message": "Please set shipping address"
}
```

---

### 4. Update Cart Address

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.cart.update_cart_address`

**Description:** Set shipping and billing addresses for cart

**Authentication:** Required

**Request Body:**

```json
{
  "shipping_address_name": "Address-001",
  "billing_address_name": "Address-002"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| shipping_address_name | string | Yes | Address name for shipping |
| billing_address_name | string | No | Address name for billing (defaults to shipping) |

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "shipping_address_name": "Address-001",
    "billing_address_name": "Address-002"
  }
}
```

---

### 5. Request for Quotation

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.cart.request_for_quotation`

**Description:** Submit cart as quotation request without converting to order

**Authentication:** Required

**Request:** No body required

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "quotation": "QTN-2024-00001"
  }
}
```

**Use Case:** Request quote for bulk items or special pricing before ordering.

---

### 6. Apply Coupon Code

**Endpoint:** `POST /api/method/webshop.webshop.shopping_cart.cart.apply_coupon_code`

**Description:** Apply promotional coupon to cart

**Authentication:** Required

**Request Body:**

```json
{
  "applied_code": "SUMMER2024"
}
```

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "discount_amount": 25.00,
    "grand_total": 225.00
  }
}
```

**Error Response (400 - Invalid Coupon):**

```json
{
  "message": "Invalid or expired coupon code"
}
```

---

## Frontend Integration

### Complete Cart Store (Pinia)

```typescript
// stores/cart.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface CartItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  image?: string
}

interface Cart {
  name: string
  grand_total: number
  total_qty: number
  items: CartItem[]
  student_id?: string
  student_name?: string
}

export const useCartStore = defineStore('cart', () => {
  const cart = ref<Cart | null>(null)
  const loading = ref(false)

  const itemCount = computed(() => cart.value?.total_qty || 0)
  const totalAmount = computed(() => cart.value?.grand_total || 0)
  const isEmpty = computed(() => !cart.value || cart.value.items.length === 0)

  // Fetch current cart
  async function fetchCart() {
    loading.value = true
    try {
      const response = await fetch(
        '/api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation',
        { credentials: 'include' }
      )

      const data = await response.json()
      cart.value = data.message.doc
    } catch (error) {
      console.error('Failed to fetch cart:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Add or update item
  async function updateItem(itemCode: string, qty: number, notes?: string) {
    loading.value = true
    try {
      const response = await fetch(
        '/api/method/webshop.webshop.shopping_cart.cart.update_cart',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            item_code: itemCode,
            qty: qty,
            additional_notes: notes,
            with_items: true
          })
        }
      )

      const data = await response.json()
      cart.value = data.message

      return data.message
    } catch (error) {
      console.error('Failed to update cart:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Remove item
  async function removeItem(itemCode: string) {
    return updateItem(itemCode, 0)
  }

  // Update address
  async function updateAddress(shippingAddress: string, billingAddress?: string) {
    const response = await fetch(
      '/api/method/webshop.webshop.shopping_cart.cart.update_cart_address',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          shipping_address_name: shippingAddress,
          billing_address_name: billingAddress || shippingAddress
        })
      }
    )

    return response.json()
  }

  // Checkout
  async function checkout() {
    loading.value = true
    try {
      const response = await fetch(
        '/api/method/webshop.webshop.shopping_cart.cart.place_order',
        {
          method: 'POST',
          credentials: 'include'
        }
      )

      const data = await response.json()
      const salesOrderName = data.message

      // Clear cart after successful checkout
      cart.value = null
      await fetchCart()

      return salesOrderName
    } catch (error) {
      console.error('Checkout failed:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // Apply coupon
  async function applyCoupon(couponCode: string) {
    const response = await fetch(
      '/api/method/webshop.webshop.shopping_cart.cart.apply_coupon_code',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ applied_code: couponCode })
      }
    )

    const data = await response.json()

    if (data.message.success) {
      await fetchCart() // Refresh cart to show discount
    }

    return data.message
  }

  return {
    cart,
    loading,
    itemCount,
    totalAmount,
    isEmpty,
    fetchCart,
    updateItem,
    removeItem,
    updateAddress,
    checkout,
    applyCoupon
  }
})
```

### Cart Page Component

```vue
<template>
  <div class="cart-page">
    <h1>Shopping Cart</h1>

    <div v-if="loading" class="loading">Loading cart...</div>

    <div v-else-if="isEmpty" class="empty-cart">
      <p>Your cart is empty</p>
      <router-link to="/products">Continue Shopping</router-link>
    </div>

    <div v-else class="cart-content">
      <!-- Student Info -->
      <div v-if="cart?.student_name" class="student-info">
        <strong>Shopping for:</strong> {{ cart.student_name }}
        ({{ cart.school_unit }})
      </div>

      <!-- Cart Items -->
      <div class="cart-items">
        <div
          v-for="item in cart?.items"
          :key="item.item_code"
          class="cart-item"
        >
          <div class="item-info">
            <h3>{{ item.item_name }}</h3>
            <p>{{ item.item_code }}</p>
          </div>

          <div class="item-quantity">
            <button @click="decrementQty(item)">-</button>
            <input
              type="number"
              :value="item.qty"
              @change="updateQuantity(item, $event)"
              min="1"
            />
            <button @click="incrementQty(item)">+</button>
          </div>

          <div class="item-price">
            <p class="rate">${{ item.rate.toFixed(2) }} each</p>
            <p class="amount">${{ item.amount.toFixed(2) }}</p>
          </div>

          <button class="remove-btn" @click="removeItem(item.item_code)">
            Remove
          </button>
        </div>
      </div>

      <!-- Cart Summary -->
      <div class="cart-summary">
        <div class="summary-row">
          <span>Subtotal:</span>
          <span>${{ totalAmount.toFixed(2) }}</span>
        </div>

        <div class="summary-row total">
          <span><strong>Total:</strong></span>
          <span><strong>${{ totalAmount.toFixed(2) }}</strong></span>
        </div>

        <button class="checkout-btn" @click="handleCheckout">
          Proceed to Checkout
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useStudentsStore } from '@/stores/students'

const router = useRouter()
const cartStore = useCartStore()
const studentsStore = useStudentsStore()

const { cart, loading, isEmpty, totalAmount } = cartStore

onMounted(async () => {
  // Ensure student is selected
  if (!studentsStore.activeStudentId) {
    router.push('/select-student')
    return
  }

  await cartStore.fetchCart()
})

async function updateQuantity(item: any, event: Event) {
  const qty = parseInt((event.target as HTMLInputElement).value)
  if (qty > 0) {
    await cartStore.updateItem(item.item_code, qty)
  }
}

async function incrementQty(item: any) {
  await cartStore.updateItem(item.item_code, item.qty + 1)
}

async function decrementQty(item: any) {
  if (item.qty > 1) {
    await cartStore.updateItem(item.item_code, item.qty - 1)
  }
}

async function removeItem(itemCode: string) {
  if (confirm('Remove this item from cart?')) {
    await cartStore.removeItem(itemCode)
  }
}

async function handleCheckout() {
  try {
    // Navigate to checkout page with address selection
    router.push('/checkout')
  } catch (error: any) {
    alert('Checkout failed: ' + error.message)
  }
}
</script>
```

### Product Page - Add to Cart

```vue
<template>
  <div class="product-page">
    <div class="product-details">
      <h1>{{ product.item_name }}</h1>
      <p class="price">${{ product.rate }}</p>

      <div class="quantity-selector">
        <label>Quantity:</label>
        <input v-model.number="qty" type="number" min="1" />
      </div>

      <button
        class="add-to-cart-btn"
        @click="addToCart"
        :disabled="loading"
      >
        {{ loading ? 'Adding...' : 'Add to Cart' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useStudentsStore } from '@/stores/students'

const props = defineProps<{
  product: {
    item_code: string
    item_name: string
    rate: number
  }
}>()

const cartStore = useCartStore()
const studentsStore = useStudentsStore()

const qty = ref(1)
const loading = ref(false)

async function addToCart() {
  // Check if student is selected
  if (!studentsStore.activeStudentId) {
    alert('Please select a student first')
    return
  }

  loading.value = true

  try {
    await cartStore.updateItem(props.product.item_code, qty.value)

    // Show success message
    alert(`Added ${qty.value} x ${props.product.item_name} to cart`)

    // Reset quantity
    qty.value = 1
  } catch (error) {
    alert('Failed to add item to cart')
  } finally {
    loading.value = false
  }
}
</script>
```

### Checkout Page

```vue
<template>
  <div class="checkout-page">
    <h1>Checkout</h1>

    <div class="checkout-steps">
      <!-- Step 1: Review Items -->
      <div class="step">
        <h2>1. Review Items</h2>
        <div class="order-summary">
          <p v-for="item in cart?.items" :key="item.item_code">
            {{ item.item_name }} x {{ item.qty }} = ${{ item.amount }}
          </p>
          <p class="total">Total: ${{ totalAmount }}</p>
        </div>
      </div>

      <!-- Step 2: Select Address -->
      <div class="step">
        <h2>2. Shipping Address</h2>
        <select v-model="selectedAddress">
          <option value="">Select address...</option>
          <option
            v-for="addr in addresses"
            :key="addr.name"
            :value="addr.name"
          >
            {{ addr.address_line1 }}, {{ addr.city }}
          </option>
        </select>
      </div>

      <!-- Step 3: Place Order -->
      <div class="step">
        <button
          class="place-order-btn"
          @click="placeOrder"
          :disabled="!selectedAddress || loading"
        >
          {{ loading ? 'Processing...' : 'Place Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()

const { cart, totalAmount } = cartStore

const addresses = ref([])
const selectedAddress = ref('')
const loading = ref(false)

onMounted(async () => {
  // Fetch addresses from API
  // addresses.value = await fetchAddresses()
})

async function placeOrder() {
  loading.value = true

  try {
    // Set address
    await cartStore.updateAddress(selectedAddress.value)

    // Place order
    const salesOrderName = await cartStore.checkout()

    // Redirect to success page
    router.push(`/order-success/${salesOrderName}`)
  } catch (error: any) {
    alert('Failed to place order: ' + error.message)
  } finally {
    loading.value = false
  }
}
</script>
```

---

## Best Practices

### 1. Always Check Active Student

```typescript
// Before any cart operation
if (!studentsStore.activeStudentId) {
  showStudentSelector()
  return
}

await cartStore.updateItem(itemCode, qty)
```

### 2. Refresh Cart After Student Switch

```typescript
async function switchStudent(studentId: string) {
  await studentsStore.setActiveStudent(studentId)

  // Important: Fetch new student's cart
  await cartStore.fetchCart()
}
```

### 3. Handle Empty Cart Gracefully

```typescript
if (cartStore.isEmpty) {
  showEmptyCartMessage()
  return
}
```

### 4. Show Loading States

```typescript
const loading = ref(false)

async function addToCart() {
  loading.value = true
  try {
    await cartStore.updateItem(itemCode, qty)
  } finally {
    loading.value = false
  }
}
```

---

## Testing

### cURL Examples

```bash
# Login first
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.auth.login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "parent@example.com", "password": "password"}'

# Set active student
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.student_utils.set_active_student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_id": "CUST-00001-ABC123"}'

# Get cart
curl -X GET http://localhost:8080/api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation \
  -b cookies.txt

# Add item to cart
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.cart.update_cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "item_code": "ITEM-001",
    "qty": 2,
    "with_items": true
  }'

# Place order
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.cart.place_order \
  -b cookies.txt
```

---

## TypeScript Types

```typescript
// types/cart.ts
export interface CartItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  description?: string
  image?: string
}

export interface Cart {
  name: string
  doctype: 'Quotation'
  party_name: string
  contact_email: string
  order_type: 'Shopping Cart'
  student_id?: string
  student_name?: string
  school_unit?: string
  grand_total: number
  total_qty: number
  currency: string
  items: CartItem[]
}

export interface UpdateCartRequest {
  item_code: string
  qty: number
  additional_notes?: string
  with_items?: boolean
}

export interface UpdateAddressRequest {
  shipping_address_name: string
  billing_address_name?: string
}
```

---

## Changelog

**v1.0.0** (2024-12-20)
- Initial cart API implementation
- Per-student cart isolation
- Complete checkout workflow
- Address management

---

**[← Back to API Documentation](../README.md)**
