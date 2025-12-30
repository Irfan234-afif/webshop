# Getting Started with Webshop APIs
## Frontend Integration Guide

Complete guide for integrating your frontend application with Frappe Webshop backend APIs.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [API Conventions](#api-conventions)
3. [Authentication Setup](#authentication-setup)
4. [Error Handling](#error-handling)
5. [TypeScript Types](#typescript-types)
6. [CORS Configuration](#cors-configuration)
7. [Development Setup](#development-setup)
8. [Testing APIs](#testing-apis)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Backend Requirements
- Frappe Framework v14+ or v15+
- ERPNext installed
- Webshop app installed with student management features
- School Units created in the system

### Frontend Requirements
- Modern JavaScript framework (Vue 3, React, Angular, etc.)
- Fetch API or Axios for HTTP requests
- State management library (Pinia, Vuex, Redux, etc.)
- TypeScript (recommended)

---

## API Conventions

### Base URL Structure

All API endpoints follow this pattern:

```
{base_url}/api/method/{app}.{module}.{file}.{function}
```

**Examples:**
```
/api/method/webshop.webshop.api.auth.login
/api/method/webshop.webshop.api.student.get_students
/api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation
```

**Environment-specific URLs:**
```typescript
const API_BASE_URL = {
  development: 'http://localhost:8080',
  production: 'https://your-domain.com'
}
```

### Request Methods

| Method | Usage |
|--------|-------|
| `GET` | Retrieve data (no side effects) |
| `POST` | Create, update, or trigger actions |

**Note:** Even operations that would traditionally be PUT/DELETE use POST in Frappe.

### Request Headers

```typescript
const headers = {
  'Content-Type': 'application/json',
  // CSRF token automatically handled by Frappe
}
```

### Response Format

All APIs return consistent structure:

```json
{
  "message": {
    // Response data here
  }
}
```

**Success Response:**
```json
{
  "message": {
    "success": true,
    "data": { /* actual data */ }
  }
}
```

**Error Response:**
```json
{
  "message": "Error description",
  "exc_type": "ValidationError"
}
```

---

## Authentication Setup

### Session-Based Authentication

Frappe uses **session cookies** for authentication. No JWT tokens required.

#### Login Flow

```typescript
// 1. Login
const response = await fetch('/api/method/webshop.webshop.api.auth.login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // CRITICAL: Include cookies
  body: JSON.stringify({ email, password })
})

// 2. Session cookie automatically set by backend
// 3. All subsequent requests include this cookie
```

#### Authenticated Requests

```typescript
// Always include credentials: 'include'
const response = await fetch('/api/method/some.endpoint', {
  credentials: 'include' // Sends session cookie
})
```

### Axios Configuration

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/method',
  withCredentials: true, // Include cookies
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  config => {
    // Optional: Add custom headers
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
```

### Session Verification

```typescript
// Check if user is authenticated
async function checkAuth() {
  try {
    const response = await fetch(
      '/api/method/webshop.webshop.api.auth.get_current_user',
      { credentials: 'include' }
    )

    const data = await response.json()

    return data.message.success && data.message.user !== null
  } catch {
    return false
  }
}

// Use in app initialization
if (!await checkAuth()) {
  router.push('/login')
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad Request | Show validation error |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show access denied |
| 404 | Not Found | Show not found message |
| 409 | Conflict | Show duplicate error |
| 500 | Server Error | Show generic error |

### Error Response Structure

```json
{
  "message": "Error description",
  "exc_type": "ValidationError",
  "_server_messages": "[...]"
}
```

### Centralized Error Handler

```typescript
interface APIError {
  message: string
  status: number
  exc_type?: string
}

function handleAPIError(error: any): APIError {
  if (error.response) {
    // HTTP error response
    return {
      message: error.response.data.message || 'An error occurred',
      status: error.response.status,
      exc_type: error.response.data.exc_type
    }
  } else if (error.request) {
    // Network error
    return {
      message: 'Network error. Please check your connection.',
      status: 0
    }
  } else {
    // Other error
    return {
      message: error.message || 'An unexpected error occurred',
      status: 0
    }
  }
}

// Usage
try {
  await api.post('endpoint', data)
} catch (error) {
  const apiError = handleAPIError(error)

  if (apiError.status === 401) {
    router.push('/login')
  } else {
    showErrorToast(apiError.message)
  }
}
```

### User-Friendly Error Messages

```typescript
const ERROR_MESSAGES: Record<string, string> = {
  'Invalid email or password': 'Incorrect email or password. Please try again.',
  'User with email {email} already exists': 'An account with this email already exists.',
  'School Unit does not exist': 'Selected school unit is invalid. Please select from the list.',
  'Cart is empty': 'Your cart is empty. Add items before checking out.',
}

function getUserFriendlyError(message: string): string {
  return ERROR_MESSAGES[message] || message
}
```

---

## TypeScript Types

### Global Types

```typescript
// types/api.ts

export interface APIResponse<T> {
  message: T
}

export interface SuccessResponse {
  success: true
  message?: string
}

export interface ErrorResponse {
  success: false
  message: string
}

// User & Authentication
export interface User {
  email: string
  full_name: string
  user_type: string
}

export interface Customer {
  name: string
  customer_name: string
}

export interface LoginResponse {
  success: true
  message: string
  user: User
  customer: Customer
  students: Student[]
}

// Student
export interface Student {
  student_id: string
  student_name: string
  school_unit: string
  grade_level?: string
  date_of_birth?: string
  is_active: number
}

// Cart
export interface CartItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  description?: string
}

export interface Cart {
  name: string
  party_name: string
  grand_total: number
  total_qty: number
  student_id?: string
  student_name?: string
  items: CartItem[]
}

// School Unit
export interface SchoolUnit {
  name: string
  unit_name: string
  unit_code: string
  description?: string
  is_active: number
}
```

### API Function Types

```typescript
// types/api-functions.ts
import type { APIResponse, LoginResponse, Student, Cart } from './api'

export interface AuthAPI {
  login(email: string, password: string): Promise<APIResponse<LoginResponse>>
  register(data: RegisterData): Promise<APIResponse<any>>
  logout(): Promise<APIResponse<SuccessResponse>>
  getCurrentUser(): Promise<APIResponse<any>>
}

export interface StudentAPI {
  getStudents(): Promise<APIResponse<Student[]>>
  addStudent(data: AddStudentData): Promise<APIResponse<any>>
  setActiveStudent(studentId: string): Promise<APIResponse<SuccessResponse>>
}

export interface CartAPI {
  getCart(): Promise<APIResponse<{ doc: Cart }>>
  updateCart(itemCode: string, qty: number): Promise<APIResponse<Cart>>
  checkout(): Promise<APIResponse<string>>
}
```

---

## CORS Configuration

### Development Setup

For local development with separate frontend and backend:

#### Option 1: Vite Proxy (Recommended)

```typescript
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        ws: true // WebSocket support
      }
    }
  }
})
```

Frontend runs on `localhost:5173`, API calls proxied to `localhost:8080`.

#### Option 2: site_config.json

```json
{
  "allow_cors": "*",
  "allowed_origins": [
    "http://localhost:5173",
    "http://localhost:3000"
  ]
}
```

Restart Frappe after changing config:
```bash
bench restart
```

### Production Setup

Use reverse proxy (Nginx/Traefik) to serve both frontend and backend from same domain:

```
your-domain.com          → Frontend
your-domain.com/api      → Backend API
```

No CORS issues when same-origin.

---

## Development Setup

### 1. Install Dependencies

```bash
# Vue 3
npm install pinia vue-router

# React
npm install axios react-router-dom zustand

# TypeScript
npm install -D typescript @types/node
```

### 2. Create API Client

```typescript
// src/api/client.ts
const API_BASE = '/api/method'

export async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}/${endpoint}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const data = await response.json()
  return data.message
}

export const authAPI = {
  login: (email: string, password: string) =>
    apiCall('webshop.webshop.api.auth.login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    }),

  getCurrentUser: () =>
    apiCall('webshop.webshop.api.auth.get_current_user')
}

export const studentAPI = {
  getStudents: () =>
    apiCall('webshop.webshop.api.student.get_students'),

  setActive: (studentId: string) =>
    apiCall('webshop.webshop.shopping_cart.student_utils.set_active_student', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId })
    })
}
```

### 3. Setup State Management

See individual API documentation for complete store examples:
- [Authentication Store](../authentication/AUTH_API.md#vue-3--pinia-example)
- [Students Store](../student_management/STUDENT_API.md#frontend-integration)
- [Cart Store](../shopping_cart/CART_API.md#complete-cart-store-pinia)

### 4. Router Guards

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { path: '/products', component: Products, meta: { requiresAuth: true } },
    { path: '/cart', component: Cart, meta: { requiresAuth: true } }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth) {
    const isAuth = await authStore.checkAuth()

    if (!isAuth) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
```

---

## Testing APIs

### Using cURL

```bash
# Login
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.auth.login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"email": "test@example.com", "password": "password"}'

# Authenticated request
curl -X GET http://localhost:8080/api/method/webshop.webshop.api.student.get_students \
  -b cookies.txt
```

### Using Postman

1. **Import Collection**: Create collection with base URL
2. **Set Environment**: Add `base_url` variable
3. **Login**: POST to login endpoint
4. **Cookie Management**: Postman automatically handles cookies
5. **Test Endpoints**: All subsequent requests include session

### Using Browser DevTools

1. Open Network tab
2. Login via frontend
3. Check cookie: `sid` should be set
4. Monitor API calls
5. Inspect request/response payloads

---

## Best Practices

### 1. Always Include Credentials

```typescript
// ✅ CORRECT
fetch('/api/method/endpoint', {
  credentials: 'include'
})

// ❌ WRONG
fetch('/api/method/endpoint') // Session not sent
```

### 2. Handle Loading States

```typescript
const loading = ref(false)

async function fetchData() {
  loading.value = true
  try {
    const data = await api.getData()
    return data
  } finally {
    loading.value = false
  }
}
```

### 3. Debounce User Input

```typescript
import { debounce } from 'lodash-es'

const checkEmail = debounce(async (email: string) => {
  const available = await api.checkEmailAvailability(email)
  showAvailability(available)
}, 500)
```

### 4. Cache API Responses

```typescript
const cache = new Map()

async function fetchWithCache(key: string, fetcher: () => Promise<any>) {
  if (cache.has(key)) {
    return cache.get(key)
  }

  const data = await fetcher()
  cache.set(key, data)

  return data
}
```

### 5. Validate Before API Calls

```typescript
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

async function register(email: string, password: string) {
  if (!validateEmail(email)) {
    throw new Error('Invalid email format')
  }

  if (password.length < 6) {
    throw new Error('Password must be at least 6 characters')
  }

  return api.register({ email, password })
}
```

### 6. Use Environment Variables

```typescript
// .env
VITE_API_BASE_URL=http://localhost:8080

// src/config.ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL
```

---

## Troubleshooting

### Issue: 401 Unauthorized on All Requests

**Cause:** Session cookie not being sent

**Solution:**
```typescript
// Ensure credentials: 'include' in all requests
fetch('/api/method/endpoint', {
  credentials: 'include' // This is required!
})
```

### Issue: CORS Errors

**Cause:** Frontend and backend on different origins

**Solution 1 - Development:**
Use Vite proxy (see CORS Configuration section)

**Solution 2 - Production:**
Serve from same domain using reverse proxy

### Issue: Session Expires Quickly

**Cause:** Default Frappe session timeout

**Solution:**
Extend session timeout in `site_config.json`:
```json
{
  "session_expiry": "24:00:00"
}
```

### Issue: Student Not Selected

**Cause:** Forgot to call `set_active_student`

**Solution:**
```typescript
// Before any cart operation
if (!studentsStore.activeStudentId) {
  await studentsStore.setActiveStudent(students[0].student_id)
}

await cartStore.addItem(itemCode, qty)
```

### Issue: Cart Empty After Student Switch

**Cause:** Not refreshing cart after switching students

**Solution:**
```typescript
async function switchStudent(studentId: string) {
  await studentsStore.setActiveStudent(studentId)
  await cartStore.fetchCart() // Must refresh!
}
```

---

## Additional Resources

- [Authentication API Docs](../authentication/AUTH_API.md)
- [Student Management API Docs](../student_management/STUDENT_API.md)
- [Shopping Cart API Docs](../shopping_cart/CART_API.md)
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [ERPNext API Reference](https://frappeframework.com/docs/user/en/api/rest)

---

## Quick Reference

### Essential Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `auth.login` | POST | No | Login user |
| `auth.get_current_user` | GET | Yes | Check session |
| `student.get_students` | GET | Yes | List students |
| `student_utils.set_active_student` | POST | Yes | Select student |
| `cart.get_cart_quotation` | GET | Yes | Get cart |
| `cart.update_cart` | POST | Yes | Update cart |
| `cart.place_order` | POST | Yes | Checkout |

### Common Patterns

```typescript
// Login
await api.post('auth.login', { email, password })

// Get Data
const students = await api.get('student.get_students')

// Update Data
await api.post('cart.update_cart', { item_code, qty })

// Check Auth
const user = await api.get('auth.get_current_user')
if (!user.success) redirect('/login')
```

---

**[← Back to API Documentation](../README.md)**
