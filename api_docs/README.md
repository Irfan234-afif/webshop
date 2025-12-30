# Webshop API Documentation
## Complete Frontend Integration Guide

This documentation provides comprehensive API references for integrating with the Frappe Webshop backend. All APIs are designed for easy frontend consumption with clear request/response formats.

---

## 📚 Documentation Structure

### [🔐 Authentication](./authentication/)
User registration, login, logout, and session management.

**Key Endpoints:**
- `POST /register` - Register new user with students
- `POST /login` - User authentication
- `POST /logout` - Session termination
- `GET /get_current_user` - Session verification

👉 **[View Authentication Docs](./authentication/AUTH_API.md)**

---

### [👨‍👩‍👧‍👦 Student Management](./student_management/)
Manage students under customer accounts, switch active students, and retrieve student data.

**Key Endpoints:**
- `GET /get_students` - Get all students
- `POST /add_student` - Add new student
- `POST /set_active_student` - Switch active student for shopping
- `GET /get_all_student_carts` - View all student carts

👉 **[View Student Management Docs](./student_management/STUDENT_API.md)**

---

### [🛒 Shopping Cart](./shopping_cart/)
Per-student cart management, checkout, and order placement.

**Key Endpoints:**
- `GET /get_cart_quotation` - Get current cart
- `POST /update_cart` - Add/update/remove items
- `POST /place_order` - Checkout and create order
- `GET /get_cart_by_student` - Get specific student's cart

👉 **[View Shopping Cart Docs](./shopping_cart/CART_API.md)**

---

### [📖 Common Resources](./common/)
Getting started guide, error handling, TypeScript types, and best practices.

**Contents:**
- API conventions and standards
- Error handling patterns
- TypeScript type definitions
- CORS and authentication setup
- Testing guide

👉 **[View Common Resources](./common/GETTING_STARTED.md)**

---

## 🚀 Quick Start

### 1. Base URL

All API endpoints are relative to your Frappe instance:

```
Production:   https://your-domain.com/api/method/
Development:  http://localhost:8080/api/method/
```

### 2. Authentication

Most endpoints require authentication via session cookies. After login, Frappe automatically manages the session.

```javascript
// Login and get session
const response = await fetch('/api/method/webshop.webshop.api.auth.login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Important: Include cookies
  body: JSON.stringify({ email, password })
})
```

### 3. Common Request Format

```javascript
// POST request example
await fetch('/api/method/module.api.endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include', // Always include for authenticated requests
  body: JSON.stringify({ param1, param2 })
})

// GET request example
await fetch('/api/method/module.api.endpoint?param1=value1', {
  credentials: 'include'
})
```

### 4. Common Response Format

All endpoints return consistent JSON structure:

```json
{
  "message": {
    "success": true,
    "data": { /* response data */ }
  }
}
```

---

## 📋 Complete API Reference

### Authentication APIs

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `webshop.webshop.api.auth.register` | POST | ❌ | Register new user |
| `webshop.webshop.api.auth.login` | POST | ❌ | User login |
| `webshop.webshop.api.auth.logout` | POST | ✅ | User logout |
| `webshop.webshop.api.auth.get_current_user` | GET | ✅ | Get current user |
| `webshop.webshop.api.auth.check_email_availability` | GET | ❌ | Check email |

### Student Management APIs

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `webshop.webshop.api.student.get_students` | GET | ✅ | List students |
| `webshop.webshop.api.student.add_student` | POST | ✅ | Add student |
| `webshop.webshop.api.student.update_student` | POST | ✅ | Update student |
| `webshop.webshop.api.student.delete_student` | POST | ✅ | Delete student |
| `webshop.webshop.api.student.get_cart_by_student` | GET | ✅ | Get student cart |
| `webshop.webshop.api.student.get_all_student_carts` | GET | ✅ | All student carts |
| `webshop.webshop.shopping_cart.student_utils.set_active_student` | POST | ✅ | Set active student |
| `webshop.webshop.shopping_cart.student_utils.get_customer_students` | GET | ✅ | Get students |
| `webshop.webshop.shopping_cart.student_utils.clear_active_student` | POST | ✅ | Clear selection |

### Shopping Cart APIs

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `webshop.webshop.shopping_cart.cart.get_cart_quotation` | GET | ✅ | Get current cart |
| `webshop.webshop.shopping_cart.cart.update_cart` | POST | ✅ | Update cart |
| `webshop.webshop.shopping_cart.cart.place_order` | POST | ✅ | Checkout |
| `webshop.webshop.shopping_cart.cart.request_for_quotation` | POST | ✅ | Request quote |
| `webshop.webshop.shopping_cart.cart.update_cart_address` | POST | ✅ | Update address |

---

## 🏗️ Typical User Journey

```
1. Register → POST /api/method/webshop.webshop.api.auth.register
   ↓
2. Login → POST /api/method/webshop.webshop.api.auth.login
   ↓
3. Get Students → GET /api/method/webshop.webshop.api.student.get_students
   ↓
4. Select Student → POST /api/method/webshop.webshop.shopping_cart.student_utils.set_active_student
   ↓
5. Browse Products → (Use ERPNext product APIs)
   ↓
6. Add to Cart → POST /api/method/webshop.webshop.shopping_cart.cart.update_cart
   ↓
7. View Cart → GET /api/method/webshop.webshop.shopping_cart.cart.get_cart_quotation
   ↓
8. Checkout → POST /api/method/webshop.webshop.shopping_cart.cart.place_order
   ↓
9. Logout → POST /api/method/webshop.webshop.api.auth.logout
```

---

## 🎯 Integration Examples

### Vue 3 + TypeScript

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  async function login(email: string, password: string) {
    const response = await fetch(
      '/api/method/webshop.webshop.api.auth.login',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password })
      }
    )
    return response.json()
  }

  return { login }
})
```

### React + Axios

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api/method',
  withCredentials: true // Important: Include cookies
})

export const authAPI = {
  login: (email: string, password: string) =>
    api.post('webshop.webshop.api.auth.login', { email, password }),

  register: (data: RegisterData) =>
    api.post('webshop.webshop.api.auth.register', data),

  getCurrentUser: () =>
    api.get('webshop.webshop.api.auth.get_current_user')
}
```

---

## 🔒 Security Best Practices

1. **Always use HTTPS in production**
2. **Never store passwords in frontend code**
3. **Include `credentials: 'include'` in all fetch requests**
4. **Validate all user input on frontend before API calls**
5. **Handle sensitive data (passwords) securely**
6. **Implement proper error handling for auth failures**
7. **Clear sensitive data on logout**

---

## 🧪 Testing

Each API documentation folder includes:
- cURL examples for quick testing
- Postman collection JSON (import to Postman)
- Python test scripts
- Example request/response payloads

---

## 📖 Additional Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Frappe REST API Guide](https://frappeframework.com/docs/user/en/api/rest)

---

## 🆘 Support & Troubleshooting

### Common Issues

**CORS Errors:**
- Configure `allowed_origins` in `site_config.json`
- Use development proxy in `vite.config.ts`

**Session Not Persisting:**
- Ensure `credentials: 'include'` in fetch/axios
- Check cookie settings (SameSite, Secure)

**401 Unauthorized:**
- Session expired - redirect to login
- Missing authentication - check if user logged in

**404 Not Found:**
- Check endpoint path spelling
- Verify API method is whitelisted with `@frappe.whitelist()`

### Getting Help

1. Check API documentation in respective folders
2. Review error logs: `bench logs`
3. Test endpoints with cURL/Postman first
4. Check browser Network tab for request details

---

## 📝 Changelog

**v1.0.0** (2024-12-20)
- Initial API documentation release
- Authentication APIs
- Student Management APIs
- Shopping Cart APIs
- Complete frontend integration examples

---

## 📄 License

Copyright (c) 2024 Frappe Technologies Pvt. Ltd.
For license information, please see license.txt

---

**Happy Coding! 🚀**

For detailed endpoint documentation, navigate to the respective folders above.
