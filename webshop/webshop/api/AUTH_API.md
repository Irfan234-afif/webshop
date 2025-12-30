# Authentication API Documentation
## Webshop Login & Registration

This document provides complete API documentation for authentication endpoints in the Frappe Webshop application.

---

## Base URL

All API endpoints are relative to your Frappe instance:

```
https://your-domain.com/api/method/webshop.webshop.api.auth
```

For local development:
```
http://localhost:8080/api/method/webshop.webshop.api.auth
```

---

## Authentication Flow

### 1. Registration Flow

```
User fills registration form
    ↓
POST /register (with name, email, phone, password, students)
    ↓
Backend creates: User → Contact → Customer → Students
    ↓
Returns: Success with user, customer, and students data
    ↓
Frontend can auto-login or redirect to login page
```

### 2. Login Flow

```
User enters email and password
    ↓
POST /login
    ↓
Backend authenticates and creates session
    ↓
Returns: User info, customer info, students list
    ↓
Frontend stores session (cookies handled by Frappe)
    ↓
Frontend can call /get_current_user to verify session
```

### 3. Session Management

Frappe handles session cookies automatically. After login:
- Session cookie (`sid`) is set in browser
- All subsequent API calls include this cookie
- No need to manually manage tokens

---

## API Endpoints

### 1. Register

**Endpoint:** `POST /api/method/webshop.webshop.api.auth.register`

**Description:** Register a new user account with customer and optional students

**Authentication:** None (allow_guest)

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone_number": "+1234567890",
  "password": "SecurePassword123",
  "students": [
    {
      "student_name": "Alice Doe",
      "school_unit": "High School",
      "grade_level": "Grade 10",
      "date_of_birth": "2010-05-15",
      "nisn": "3453452423443"
    },
    {
      "student_name": "Bob Doe",
      "school_unit": "Elementary",
      "grade_level": "Grade 5",
      "nisn": "3453452423443"
    }
  ]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Full name of the customer/parent |
| email | string | Yes | Email address (must be valid and unique) |
| phone_number | string | Yes | Phone number |
| password | string | Yes | Account password (min 6 characters recommended) |
| students | array | No | Array of student objects to create |

**Students Object Structure:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| student_name | string | Yes | Student's full name |
| school_unit | string | Yes | School Unit name (must exist in system) |
| grade_level | string | No | Student's grade level |
| date_of_birth | string | No | Date in YYYY-MM-DD format |

**Success Response (201 Created):**

```json
{
  "message": {
    "success": true,
    "message": "Registration successful",
    "user": {
      "email": "john.doe@example.com",
      "full_name": "John Doe"
    },
    "customer": {
      "name": "CUST-00001",
      "customer_name": "John Doe"
    },
    "students": [
      {
        "student_id": "CUST-00001-ABC123",
        "student_name": "Alice Doe",
        "school_unit": "High School",
        "grade_level": "Grade 10"
      },
      {
        "student_id": "CUST-00001-XYZ789",
        "student_name": "Bob Doe",
        "school_unit": "Elementary",
        "grade_level": "Grade 5"
      }
    ]
  }
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "message": {
    "success": false,
    "message": "Name, email, and password are required"
  }
}
```

**409 Conflict (Email Already Exists):**
```json
{
  "message": {
    "success": false,
    "message": "User with email john.doe@example.com already exists"
  }
}
```

**500 Internal Server Error:**
```json
{
  "message": {
    "success": false,
    "message": "Error details..."
  }
}
```

---

### 2. Login

**Endpoint:** `POST /api/method/webshop.webshop.api.auth.login`

**Description:** Login with email and password

**Authentication:** None (allow_guest)

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "password": "SecurePassword123"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | User email address |
| password | string | Yes | User password |

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "message": "Login successful",
    "user": {
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "user_type": "Website User"
    },
    "customer": {
      "name": "CUST-00001",
      "customer_name": "John Doe"
    },
    "students": [
      {
        "student_id": "CUST-00001-ABC123",
        "student_name": "Alice Doe",
        "school_unit": "High School",
        "grade_level": "Grade 10",
        "is_active": 1
      },
      {
        "student_id": "CUST-00001-XYZ789",
        "student_name": "Bob Doe",
        "school_unit": "Elementary",
        "grade_level": "Grade 5",
        "is_active": 1
      }
    ]
  }
}
```

**Error Responses:**

**401 Unauthorized (Invalid Credentials):**
```json
{
  "message": {
    "success": false,
    "message": "Invalid email or password"
  }
}
```

**400 Bad Request:**
```json
{
  "message": {
    "success": false,
    "message": "Email and password are required"
  }
}
```

**Side Effects:**
- Sets session cookie (`sid`) in browser
- Creates user session in backend
- Session persists until logout or expiration

---

### 3. Logout

**Endpoint:** `POST /api/method/webshop.webshop.api.auth.logout`

**Description:** Logout current user and destroy session

**Authentication:** Required (user must be logged in)

**Request Body:** None

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "message": "Logout successful"
  }
}
```

**Side Effects:**
- Destroys session cookie
- Clears backend session
- User must login again to access protected resources

---

### 4. Get Current User

**Endpoint:** `GET /api/method/webshop.webshop.api.auth.get_current_user`

**Description:** Get information about currently logged-in user

**Authentication:** Required

**Request:** No parameters

**Success Response (200 OK):**

```json
{
  "message": {
    "success": true,
    "user": {
      "email": "john.doe@example.com",
      "full_name": "John Doe",
      "user_type": "Website User"
    },
    "customer": {
      "name": "CUST-00001",
      "customer_name": "John Doe"
    },
    "students": [
      {
        "student_id": "CUST-00001-ABC123",
        "student_name": "Alice Doe",
        "school_unit": "High School",
        "grade_level": "Grade 10",
        "is_active": 1
      }
    ]
  }
}
```

**Not Authenticated Response:**

```json
{
  "message": {
    "success": false,
    "message": "Not authenticated",
    "user": null
  }
}
```

**Use Case:**
- Check if user is still logged in
- Restore user state on page refresh
- Verify session validity

---

### 5. Check Email Availability

**Endpoint:** `GET /api/method/webshop.webshop.api.auth.check_email_availability`

**Description:** Check if an email is available for registration

**Authentication:** None (allow_guest)

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| email | string | Yes | Email to check |

**Example Request:**

```
GET /api/method/webshop.webshop.api.auth.check_email_availability?email=john.doe@example.com
```

**Success Response (Email Available):**

```json
{
  "message": {
    "success": true,
    "available": true,
    "message": "Email is available"
  }
}
```

**Success Response (Email Taken):**

```json
{
  "message": {
    "success": true,
    "available": false,
    "message": "Email is already registered"
  }
}
```

**Error Response (Invalid Email):**

```json
{
  "message": {
    "success": false,
    "available": false,
    "message": "Invalid email format"
  }
}
```

**Use Case:**
- Real-time email validation during registration form input
- Show availability feedback before form submission

---

## Frontend Integration Examples

### JavaScript/Fetch Example

#### Registration

```javascript
async function register(userData) {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.auth.register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: userData.name,
        email: userData.email,
        phone_number: userData.phoneNumber,
        password: userData.password,
        students: userData.students // Optional array
      })
    });

    const data = await response.json();

    if (data.message.success) {
      console.log('Registration successful:', data.message);
      // Redirect to login or auto-login
      return data.message;
    } else {
      console.error('Registration failed:', data.message.message);
      throw new Error(data.message.message);
    }
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
}

// Usage
register({
  name: 'John Doe',
  email: 'john.doe@example.com',
  phoneNumber: '+1234567890',
  password: 'SecurePassword123',
  students: [
    {
      student_name: 'Alice Doe',
      school_unit: 'High School',
      grade_level: 'Grade 10'
    }
  ]
});
```

#### Login

```javascript
async function login(email, password) {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.auth.login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Important: Include cookies
      body: JSON.stringify({
        email: email,
        password: password
      })
    });

    const data = await response.json();

    if (data.message.success) {
      console.log('Login successful:', data.message);
      // Store user data in state management (Pinia/Vuex/Redux)
      return data.message;
    } else {
      console.error('Login failed:', data.message.message);
      throw new Error(data.message.message);
    }
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

// Usage
login('john.doe@example.com', 'SecurePassword123');
```

#### Check Current User (Session Verification)

```javascript
async function getCurrentUser() {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.auth.get_current_user', {
      method: 'GET',
      credentials: 'include' // Important: Include cookies
    });

    const data = await response.json();

    if (data.message.success && data.message.user) {
      console.log('User is authenticated:', data.message);
      return data.message;
    } else {
      console.log('User is not authenticated');
      return null;
    }
  } catch (error) {
    console.error('Get current user error:', error);
    return null;
  }
}

// Usage - call on app initialization
const user = await getCurrentUser();
if (!user) {
  // Redirect to login page
}
```

#### Logout

```javascript
async function logout() {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.auth.logout', {
      method: 'POST',
      credentials: 'include' // Important: Include cookies
    });

    const data = await response.json();

    if (data.message.success) {
      console.log('Logout successful');
      // Clear local state and redirect to login
      return true;
    }
  } catch (error) {
    console.error('Logout error:', error);
    return false;
  }
}
```

---

### Vue 3 + Pinia Example

#### Auth Store

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface User {
  email: string
  full_name: string
  user_type: string
}

interface Customer {
  name: string
  customer_name: string
}

interface Student {
  student_id: string
  student_name: string
  school_unit: string
  grade_level?: string
  is_active: number
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const customer = ref<Customer | null>(null)
  const students = ref<Student[]>([])
  const isAuthenticated = ref(false)

  async function register(userData: {
    name: string
    email: string
    phoneNumber: string
    password: string
    students?: any[]
  }) {
    const response = await fetch('/api/method/webshop.webshop.api.auth.register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: userData.name,
        email: userData.email,
        phone_number: userData.phoneNumber,
        password: userData.password,
        students: userData.students
      })
    })

    const data = await response.json()

    if (!data.message.success) {
      throw new Error(data.message.message)
    }

    return data.message
  }

  async function login(email: string, password: string) {
    const response = await fetch('/api/method/webshop.webshop.api.auth.login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    })

    const data = await response.json()

    if (!data.message.success) {
      throw new Error(data.message.message)
    }

    // Update store
    user.value = data.message.user
    customer.value = data.message.customer
    students.value = data.message.students
    isAuthenticated.value = true

    return data.message
  }

  async function logout() {
    const response = await fetch('/api/method/webshop.webshop.api.auth.logout', {
      method: 'POST',
      credentials: 'include'
    })

    // Clear store
    user.value = null
    customer.value = null
    students.value = []
    isAuthenticated.value = false
  }

  async function checkAuth() {
    try {
      const response = await fetch('/api/method/webshop.webshop.api.auth.get_current_user', {
        credentials: 'include'
      })

      const data = await response.json()

      if (data.message.success && data.message.user) {
        user.value = data.message.user
        customer.value = data.message.customer
        students.value = data.message.students
        isAuthenticated.value = true
        return true
      } else {
        isAuthenticated.value = false
        return false
      }
    } catch (error) {
      console.error('Auth check failed:', error)
      isAuthenticated.value = false
      return false
    }
  }

  return {
    user,
    customer,
    students,
    isAuthenticated,
    register,
    login,
    logout,
    checkAuth
  }
})
```

#### Vue Component Example

```vue
<template>
  <div class="register-form">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <input v-model="form.name" placeholder="Full Name" required />
      <input v-model="form.email" type="email" placeholder="Email" required />
      <input v-model="form.phoneNumber" placeholder="Phone Number" required />
      <input v-model="form.password" type="password" placeholder="Password" required />

      <h3>Students (Optional)</h3>
      <div v-for="(student, index) in form.students" :key="index">
        <input v-model="student.student_name" placeholder="Student Name" />
        <select v-model="student.school_unit">
          <option value="">Select School Unit</option>
          <option value="High School">High School</option>
          <option value="Elementary">Elementary</option>
        </select>
        <input v-model="student.grade_level" placeholder="Grade Level" />
      </div>

      <button type="button" @click="addStudent">Add Student</button>
      <button type="submit">Register</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  name: '',
  email: '',
  phoneNumber: '',
  password: '',
  students: [] as Array<{
    student_name: string
    school_unit: string
    grade_level: string
  }>
})

const error = ref('')

function addStudent() {
  form.value.students.push({
    student_name: '',
    school_unit: '',
    grade_level: ''
  })
}

async function handleRegister() {
  try {
    error.value = ''
    await authStore.register(form.value)

    // Optionally auto-login after registration
    await authStore.login(form.value.email, form.value.password)

    // Redirect to dashboard
    router.push('/dashboard')
  } catch (e: any) {
    error.value = e.message
  }
}
</script>
```

---

## Error Handling

All API endpoints return consistent error structure:

```json
{
  "message": {
    "success": false,
    "message": "Error description here"
  }
}
```

**HTTP Status Codes:**

| Code | Description | When |
|------|-------------|------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or missing required fields |
| 401 | Unauthorized | Invalid credentials or not authenticated |
| 403 | Forbidden | Access denied |
| 409 | Conflict | Duplicate entry (e.g., email already exists) |
| 500 | Internal Server Error | Server-side error |

**Common Error Messages:**

- `"Email and password are required"` - Missing login credentials
- `"Name, email, and password are required"` - Missing registration fields
- `"Invalid email format"` - Email validation failed
- `"User with email {email} already exists"` - Duplicate registration attempt
- `"Invalid email or password"` - Authentication failed
- `"Not authenticated"` - Session expired or user not logged in
- `"School Unit {unit} does not exist"` - Invalid school unit reference

---

## Security Considerations

1. **Password Storage**: Passwords are hashed using Frappe's built-in encryption
2. **Session Management**: Session cookies are HTTP-only and secure in production
3. **CSRF Protection**: Frappe handles CSRF tokens automatically
4. **Rate Limiting**: Consider implementing rate limiting on login/register endpoints
5. **Password Strength**: Enforce strong password requirements on frontend
6. **Email Validation**: Always validate email format on both frontend and backend
7. **HTTPS**: Always use HTTPS in production to protect credentials

---

## Testing

### Test User Registration

```bash
# Using curl
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.auth.register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone_number": "+1234567890",
    "password": "TestPassword123",
    "students": [
      {
        "student_name": "Test Student",
        "school_unit": "High School",
        "grade_level": "Grade 10"
      }
    ]
  }'
```

### Test Login

```bash
curl -X POST http://localhost:8080/api/method/webshop.webshop.api.auth.login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

### Test Get Current User (with session)

```bash
curl -X GET http://localhost:8080/api/method/webshop.webshop.api.auth.get_current_user \
  -b cookies.txt
```

---

## Integration Checklist

- [ ] Install webshop app with student management features
- [ ] Create School Unit records via ERPNext UI
- [ ] Test registration endpoint with Postman/curl
- [ ] Test login endpoint and verify session cookie
- [ ] Implement frontend registration form
- [ ] Implement frontend login form
- [ ] Add session verification on app initialization
- [ ] Handle authentication errors gracefully
- [ ] Add loading states during API calls
- [ ] Implement logout functionality
- [ ] Test email availability checker
- [ ] Add validation for all form fields
- [ ] Secure password requirements on frontend
- [ ] Test student creation during registration
- [ ] Verify students appear in Customer record
- [ ] Test complete user journey: Register → Login → Browse → Logout

---

## Troubleshooting

### Issue: "User already exists" on registration
**Solution**: Check if email is already registered. Use `/check_email_availability` endpoint first.

### Issue: Login returns success but session not persisted
**Solution**: Ensure `credentials: 'include'` is set in fetch requests. Check CORS settings.

### Issue: "School Unit does not exist" error
**Solution**: Create School Unit records via ERPNext UI first: Desk → School Unit → New

### Issue: Students not appearing after registration
**Solution**: Check if `students` array is properly formatted. Verify School Unit names match exactly.

### Issue: 401 on get_current_user
**Solution**: User session expired or not logged in. Redirect to login page.

### Issue: CORS errors in frontend
**Solution**: Configure `allowed_origins` in `site_config.json` or use proxy in development.

---

## Support

For issues or questions:
1. Check error logs: `bench logs`
2. Review Frappe documentation: https://frappeframework.com/docs
3. Check webshop app issues: [Repository URL]

---

## Changelog

**Version 1.0.0** (2024-12-20)
- Initial authentication API implementation
- Registration with student creation support
- Login/logout endpoints
- Session management
- Email availability checker
