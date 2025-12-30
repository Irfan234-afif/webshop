# Cart Integration Documentation

This document explains how to use the shopping cart integration with the Frappe Webshop backend, including support for **variant attributes** (Size, Color, etc.).

## Overview

The cart system integrates the Vue frontend with the Frappe ERPNext backend through:

1. **Backend API** (`/apps/webshop/webshop/webshop/api/products.py`) - Cart API endpoints
2. **Frontend Types** (`/frontend/src/types/cart.ts`) - TypeScript type definitions
3. **API Utilities** (`/frontend/src/utils/cartApi.ts`) - API request functions
4. **Pinia Store** (`/frontend/src/stores/cart.ts`) - Cart state management

## Features

✅ **Fetch cart items** with complete details
✅ **Add items to cart** with quantity and notes
✅ **Update item quantities** or remove items
✅ **Variant attribute support** - Display Size, Color, and custom attributes
✅ **Stock information** - Real-time stock status and quantities
✅ **Student-based carts** - Support for multi-student cart organization
✅ **Automatic price calculation** - Backend handles all pricing and taxes

## Backend API Endpoints

All endpoints are under `/api/method/webshop.webshop.api.products.*`

### 1. Get Cart Items

**Endpoint:** `get_cart_items()`

Retrieves the current shopping cart with all items, including variant attributes.

```python
# Backend call
frappe.call({
    method: 'webshop.webshop.api.products.get_cart_items',
    callback: (r) => {
        console.log(r.message)
    }
})
```

**Response:**
```json
{
    "items": [
        {
            "id": "QTN-ITEM-0001",
            "item_code": "SHIRT-001-M",
            "productId": "shirt-001",
            "title": "Cotton T-Shirt",
            "image": "/files/shirt.jpg",
            "price": 150000,
            "quantity": 2,
            "amount": 300000,
            "variantAttributes": [
                {
                    "attribute": "Size",
                    "value": "M",
                    "label": "Size",
                    "displayValue": "M"
                },
                {
                    "attribute": "Color",
                    "value": "Blue",
                    "label": "Color",
                    "displayValue": "Blue"
                }
            ],
            "selectedSize": "M",
            "selectedColor": "Blue",
            "inStock": true,
            "stockQuantity": 50
        }
    ],
    "total": 300000,
    "itemCount": 2,
    "quotation_name": "QTN-CART-00001"
}
```

### 2. Add to Cart

**Endpoint:** `add_to_cart(item_code, qty, additional_notes)`

Adds an item to the cart.

```python
frappe.call({
    method: 'webshop.webshop.api.products.add_to_cart',
    args: {
        item_code: 'SHIRT-001-M',
        qty: 2,
        additional_notes: 'Gift wrap please'
    },
    callback: (r) => {
        console.log('Updated cart:', r.message)
    }
})
```

### 3. Update Cart Item Quantity

**Endpoint:** `update_cart_item_qty(item_code, qty)`

Updates the quantity of an existing item (set qty to 0 to remove).

```python
frappe.call({
    method: 'webshop.webshop.api.products.update_cart_item_qty',
    args: {
        item_code: 'SHIRT-001-M',
        qty: 5
    },
    callback: (r) => {
        console.log('Updated cart:', r.message)
    }
})
```

### 4. Remove from Cart

**Endpoint:** `remove_from_cart(item_code)`

Removes an item from the cart (shorthand for setting qty to 0).

```python
frappe.call({
    method: 'webshop.webshop.api.products.remove_from_cart',
    args: {
        item_code: 'SHIRT-001-M'
    },
    callback: (r) => {
        console.log('Updated cart:', r.message)
    }
})
```

## Frontend Usage

### 1. Using the Cart Store (Pinia)

The recommended way to interact with the cart is through the Pinia store:

```typescript
<script setup lang="ts">
import { useCartStore } from '@/stores/cart'

const cartStore = useCartStore()

// Fetch cart on component mount
onMounted(async () => {
  await cartStore.fetchCart()
})

// Add item to cart
const handleAddToCart = async () => {
  try {
    await cartStore.addToCart({
      item_code: 'SHIRT-001-M',
      qty: 2,
      additional_notes: 'Gift wrap'
    })
    console.log('Item added successfully!')
  } catch (error) {
    console.error('Failed to add item:', error)
  }
}

// Update quantity
const updateQty = async (itemCode: string, newQty: number) => {
  await cartStore.updateQuantity(itemCode, newQty)
}

// Remove item
const removeItem = async (itemCode: string) => {
  await cartStore.removeItem(itemCode)
}
</script>

<template>
  <div>
    <!-- Loading state -->
    <div v-if="cartStore.isLoading">Loading cart...</div>

    <!-- Error state -->
    <div v-if="cartStore.error">{{ cartStore.error.message }}</div>

    <!-- Cart items -->
    <div v-for="item in cartStore.items" :key="item.id">
      <h3>{{ item.title }}</h3>
      <p>Price: {{ item.price }}</p>
      <p>Quantity: {{ item.quantity }}</p>
      <p>Total: {{ item.amount }}</p>

      <!-- Display variant attributes -->
      <div v-if="item.variantAttributes">
        <p v-for="attr in item.variantAttributes" :key="attr.attribute">
          {{ attr.label }}: {{ attr.displayValue }}
        </p>
      </div>

      <!-- Or use quick access properties -->
      <div v-if="item.selectedSize">
        Size: {{ item.selectedSize }}
      </div>
      <div v-if="item.selectedColor">
        Color: {{ item.selectedColor }}
      </div>

      <button @click="updateQty(item.item_code, item.quantity + 1)">+</button>
      <button @click="updateQty(item.item_code, item.quantity - 1)">-</button>
      <button @click="removeItem(item.item_code)">Remove</button>
    </div>

    <!-- Cart summary -->
    <div>
      <p>Total Items: {{ cartStore.itemCount }}</p>
      <p>Total Price: {{ cartStore.totalPrice }}</p>
    </div>
  </div>
</template>
```

### 2. Direct API Calls

You can also use the API utilities directly without the store:

```typescript
import * as cartApi from '@/utils/cartApi'

// Get cart
const cart = await cartApi.getCart()

// Add to cart
const updatedCart = await cartApi.addToCart({
  item_code: 'SHIRT-001-M',
  qty: 2
})

// Update quantity
const cart = await cartApi.updateCartItemQty('SHIRT-001-M', 5)

// Remove item
const cart = await cartApi.removeFromCart('SHIRT-001-M')

// Format variant attributes for display
import { getVariantDisplayText } from '@/utils/cartApi'

const displayText = getVariantDisplayText(item.variantAttributes)
// Output: "Size: M, Color: Blue"
```

## TypeScript Types

### CartItem

```typescript
interface CartItem {
  id: string                      // Quotation Item name
  item_code: string               // ERPNext item code
  productId: string               // Website item route or item_code
  title: string                   // Product title
  image: string                   // Product image URL
  price: number                   // Item price
  quantity: number                // Item quantity
  amount: number                  // Total (price * quantity)

  // Variant information
  variantAttributes?: VariantAttribute[]
  selectedSize?: string           // Quick access to size
  selectedColor?: string          // Quick access to color

  // Stock information
  inStock?: boolean
  stockQuantity?: number

  // Student information (optional)
  studentId?: string
  studentName?: string
  schoolUnit?: string
}
```

### VariantAttribute

```typescript
interface VariantAttribute {
  attribute: string        // Attribute name (e.g., "Size", "Color")
  value: string           // Attribute value (e.g., "M", "Red")
  label: string           // Display label
  displayValue: string    // Formatted display value
}
```

## Variant Attributes

The cart system automatically detects and includes variant attributes for items. Common attributes include:

- **Size / Ukuran** - Automatically set to `selectedSize`
- **Color / Warna / Colour** - Automatically set to `selectedColor`
- **Custom attributes** - Available in `variantAttributes` array

### Backend Configuration

Variant attributes are stored in the **Item Variant Attribute** DocType in ERPNext. The cart API automatically fetches these attributes for each variant item in the cart.

### Frontend Display

You have two options for displaying variant attributes:

**Option 1: Use quick access properties**
```vue
<div v-if="item.selectedSize">
  Size: {{ item.selectedSize }}
</div>
```

**Option 2: Loop through all attributes**
```vue
<div v-if="item.variantAttributes">
  <span v-for="attr in item.variantAttributes" :key="attr.attribute">
    {{ attr.label }}: {{ attr.displayValue }}
  </span>
</div>
```

**Option 3: Use the helper function**
```typescript
import { getVariantDisplayText } from '@/utils/cartApi'

const displayText = getVariantDisplayText(item.variantAttributes)
// Returns: "Size: M, Color: Blue"
```

## Student-Based Carts

The cart system supports multi-student organization for parent accounts:

```typescript
// Get items for specific student
const studentItems = cartStore.getItemsByStudent('student-1')

// Get total for specific student
const studentTotal = cartStore.getStudentCartTotal('student-1')

// Get item count for student
const studentCount = cartStore.getStudentItemCount('student-1')
```

Items will include `studentId`, `studentName`, and `schoolUnit` when applicable.

## Error Handling

All cart operations may throw errors. Always wrap in try-catch:

```typescript
try {
  await cartStore.addToCart({
    item_code: 'SHIRT-001-M',
    qty: 2
  })
} catch (error) {
  console.error('Cart operation failed:', error)
  // Show error to user
  alert(error.message)
}
```

Common error scenarios:
- Item out of stock
- Invalid item code
- Network errors
- Session expired
- Validation errors (e.g., qty must be > 0)

## Development Mode

For development/testing, you can use mock data:

```typescript
// Load mock data (only in development)
cartStore.loadMockData()
```

This populates the cart with sample items including variant attributes.

## Best Practices

1. **Always fetch cart on mount** - Call `fetchCart()` when cart component mounts
2. **Handle loading states** - Show loading indicator during operations
3. **Handle errors** - Display user-friendly error messages
4. **Use item_code for operations** - Always use `item_code` (not `id` or `productId`) for update/remove operations
5. **Display variant attributes** - Show size, color, and other variant details to users
6. **Check stock status** - Use `inStock` and `stockQuantity` to show availability
7. **Use the store** - Prefer using the Pinia store over direct API calls for automatic state synchronization

## Example: Complete Cart Component

See `/frontend/src/components/features/cart/` for full cart component examples (coming soon).

## Troubleshooting

### Cart not loading
- Check that user is authenticated
- Verify backend is running on port 8000
- Check browser console for errors

### Variant attributes not showing
- Ensure item has variants defined in ERPNext
- Check Item Variant Attribute records exist
- Verify `variantAttributes` is not null/empty

### Stock information missing
- Ensure website warehouse is set on Website Item
- Check that item has stock available
- Verify stock tracking is enabled for the item

## API Reference

For complete API documentation, see:
- Backend: `/apps/webshop/webshop/webshop/api/products.py`
- Frontend Types: `/frontend/src/types/cart.ts`
- API Utils: `/frontend/src/utils/cartApi.ts`
- Store: `/frontend/src/stores/cart.ts`
