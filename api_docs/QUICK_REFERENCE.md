# API Quick Reference Cheat Sheet
## Webshop APIs at a Glance

---

## 🚀 Quick Start

```typescript
// 1. Login
POST /api/method/webshop.webshop.api.auth.login
{ "email": "user@example.com", "password": "password" }

// 2. Get students
GET /api/method/webshop.webshop.api.student.get_students

// 3. Set active student
POST /api/method/webshop.webshop.shopping_cart.student_utils.set_active_student
{ "student_id": "CUST-00001-ABC123" }

// 4. Add to cart
POST /api/method/webshop.webshop.shopping_cart.cart.update_cart
{ "item_code": "ITEM-001", "qty": 2 }

// 5. Checkout
POST /api/method/webshop.webshop.shopping_cart.cart.place_order
```

---

## 📖 Authentication

| Endpoint | Auth | Body |
|----------|------|------|
| `auth.register` | ❌ | `{ name, email, phone_number, password, students[] }` |
| `auth.login` | ❌ | `{ email, password }` |
| `auth.logout` | ✅ | - |
| `auth.get_current_user` | ✅ | - |
| `auth.check_email_availability` | ❌ | Query: `?email=...` |

---

## 👨‍👩‍👧‍👦 Student Management

| Endpoint | Auth | Body |
|----------|------|------|
| `student.get_students` | ✅ | - |
| `student.add_student` | ✅ | `{ student_name, school_unit, grade_level? }` |
| `student.update_student` | ✅ | `{ student_id, student_name?, ... }` |
| `student.delete_student` | ✅ | `{ student_id }` |
| `student.get_cart_by_student` | ✅ | Query: `?student_id=...` |
| `student.get_all_student_carts` | ✅ | - |
| `student_utils.set_active_student` | ✅ | `{ student_id }` |
| `student_utils.clear_active_student` | ✅ | - |

---

## 🛒 Shopping Cart

| Endpoint | Auth | Body |
|----------|------|------|
| `cart.get_cart_quotation` | ✅ | - |
| `cart.update_cart` | ✅ | `{ item_code, qty, additional_notes? }` |
| `cart.update_cart_address` | ✅ | `{ shipping_address_name, billing_address_name? }` |
| `cart.place_order` | ✅ | - |
| `cart.apply_coupon_code` | ✅ | `{ applied_code }` |

---

## 🔧 Request Format

```typescript
// GET Request
fetch('/api/method/endpoint', {
  credentials: 'include' // REQUIRED
})

// POST Request
fetch('/api/method/endpoint', {
  method: 'POST',
  credentials: 'include', // REQUIRED
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ param1, param2 })
})
```

---

## ✅ Response Format

```json
{
  "message": {
    // Response data here
  }
}
```

---

## ❌ Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Show validation error |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Show not found |
| 409 | Conflict | Duplicate entry |
| 500 | Server Error | Generic error |

---

## 🎯 Common Patterns

### Login & Session Check
```typescript
// Login
await fetch('/api/method/webshop.webshop.api.auth.login', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
})

// Check session
const response = await fetch('/api/method/webshop.webshop.api.auth.get_current_user', {
  credentials: 'include'
})
const data = await response.json()
const isAuth = data.message.success && data.message.user !== null
```

### Student Selection
```typescript
// Get all students
const response = await fetch('/api/method/webshop.webshop.api.student.get_students', {
  credentials: 'include'
})
const students = await response.json()

// Set active student
await fetch('/api/method/webshop.webshop.shopping_cart.student_utils.set_active_student', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ student_id: students.message[0].student_id })
})
```

### Cart Operations
```typescript
// Add to cart
await fetch('/api/method/webshop.webshop.shopping_cart.cart.update_cart', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ item_code: 'ITEM-001', qty: 2 })
})

// Get cart
const cart = await fetch('/api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation', {
  credentials: 'include'
})

// Checkout
const order = await fetch('/api/method/webshop.webshop.shopping_cart.cart.place_order', {
  method: 'POST',
  credentials: 'include'
})
```

---

## 🍪 Cookie Management

**Active Student Cookie:**
- Name: `active_student_id`
- Set by: `set_active_student` API
- Expires: 30 days
- Use: Persists student selection across sessions

**Session Cookie:**
- Name: `sid`
- Set by: Login API
- Use: Authentication for all requests

**Reading Cookie:**
```typescript
const value = document.cookie.match(/cookie_name=([^;]+)/)?.[1]
```

---

## 💡 Best Practices

1. **Always include `credentials: 'include'`** in fetch requests
2. **Set active student before cart operations**
3. **Refresh cart after switching students**
4. **Validate input before API calls**
5. **Handle loading and error states**
6. **Use TypeScript for type safety**

---

## 🐛 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 on all requests | No credentials | Add `credentials: 'include'` |
| CORS errors | Different origin | Use Vite proxy or same domain |
| Empty cart after switch | Not refreshed | Call `fetchCart()` after switch |
| "Student not selected" | No active student | Call `set_active_student` first |

---

## 📦 TypeScript Types

```typescript
interface User {
  email: string
  full_name: string
  user_type: string
}

interface Student {
  student_id: string
  student_name: string
  school_unit: string
  grade_level?: string
  is_active: number
}

interface CartItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
}

interface Cart {
  name: string
  grand_total: number
  total_qty: number
  student_id?: string
  items: CartItem[]
}
```

---

## 🧪 Testing with cURL

```bash
# Login
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.auth.login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "user@example.com", "password": "password"}'

# Get students
curl -X GET http://localhost:8080/api/method/webshop.webshop.api.student.get_students \
  -b cookies.txt

# Set active student
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.student_utils.set_active_student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_id": "CUST-00001-ABC123"}'

# Add to cart
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.cart.update_cart \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"item_code": "ITEM-001", "qty": 2}'

# Checkout
curl -X POST http://localhost:8080/api/method/webshop.webshop.shopping_cart.cart.place_order \
  -b cookies.txt
```

---

## 📚 Full Documentation

- [Complete README](./README.md)
- [Authentication Guide](./authentication/AUTH_API.md)
- [Student Management Guide](./student_management/STUDENT_API.md)
- [Shopping Cart Guide](./shopping_cart/CART_API.md)
- [Getting Started](./common/GETTING_STARTED.md)
- [Postman Collection](./Webshop_API.postman_collection.json)

---

**Last Updated:** 2024-12-20
