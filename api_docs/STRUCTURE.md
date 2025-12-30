# API Documentation Structure

Complete organization of the Webshop API documentation for frontend developers.

---

## 📁 Folder Structure

```
api_docs/
│
├── README.md                              # Main documentation index
├── QUICK_REFERENCE.md                     # Cheat sheet for quick lookups
├── STRUCTURE.md                           # This file - documentation structure
├── Webshop_API.postman_collection.json    # Postman collection (import directly)
│
├── authentication/
│   └── AUTH_API.md                        # Login, register, logout, session
│
├── student_management/
│   └── STUDENT_API.md                     # Students, active student, carts
│
├── shopping_cart/
│   └── CART_API.md                        # Cart, checkout, orders
│
└── common/
    └── GETTING_STARTED.md                 # Setup, conventions, best practices
```

---

## 📄 File Descriptions

### Root Level

#### `README.md`
- **Purpose**: Main entry point for all API documentation
- **Contains**: Overview, quick start, API reference table, user journey
- **Audience**: All developers starting with the APIs
- **Read first**: ✅

#### `QUICK_REFERENCE.md`
- **Purpose**: Cheat sheet for quick lookups
- **Contains**: All endpoints in table format, common patterns, code snippets
- **Audience**: Developers who need quick reference
- **Read first**: After understanding basics

#### `STRUCTURE.md`
- **Purpose**: This file - explains documentation organization
- **Contains**: Folder structure, file descriptions, navigation guide
- **Audience**: New developers exploring the docs
- **Read first**: To understand documentation layout

#### `Webshop_API.postman_collection.json`
- **Purpose**: Ready-to-import Postman collection
- **Contains**: All API endpoints with example requests
- **Usage**: Import into Postman → Set base_url variable → Test APIs
- **Audience**: Developers who prefer Postman for testing

---

### `/authentication/`

#### `AUTH_API.md`
- **Purpose**: Complete authentication documentation
- **Endpoints Covered**:
  - `POST /auth.register` - User registration
  - `POST /auth.login` - User login
  - `POST /auth.logout` - User logout
  - `GET /auth.get_current_user` - Session verification
  - `GET /auth.check_email_availability` - Email validation
- **Contains**:
  - Request/response examples
  - Vue 3 + Pinia integration examples
  - Authentication flow diagrams
  - Error handling
  - Testing guide
- **Read when**: Implementing login/registration

---

### `/student_management/`

#### `STUDENT_API.md`
- **Purpose**: Student and multi-cart management
- **Endpoints Covered**:
  - `GET /student.get_students` - List all students
  - `POST /student.add_student` - Add new student
  - `POST /student.update_student` - Update student
  - `POST /student.delete_student` - Delete student
  - `POST /student_utils.set_active_student` - Select active student
  - `POST /student_utils.clear_active_student` - Clear selection
  - `GET /student.get_cart_by_student` - Get specific student cart
  - `GET /student.get_all_student_carts` - Get all carts overview
- **Contains**:
  - Per-student cart isolation explanation
  - Cookie persistence guide
  - Student selector component example
  - Multi-cart dashboard example
  - Best practices for student management
- **Read when**: Implementing student selection and management

---

### `/shopping_cart/`

#### `CART_API.md`
- **Purpose**: Shopping cart and checkout operations
- **Endpoints Covered**:
  - `GET /cart.get_cart_quotation` - Get current cart
  - `POST /cart.update_cart` - Add/update/remove items
  - `POST /cart.update_cart_address` - Set addresses
  - `POST /cart.place_order` - Checkout
  - `POST /cart.apply_coupon_code` - Apply coupons
- **Contains**:
  - How carts work (Quotation-based)
  - Cart identification logic
  - Complete cart store (Pinia)
  - Cart page component example
  - Product page integration
  - Checkout flow example
- **Read when**: Implementing cart and checkout features

---

### `/common/`

#### `GETTING_STARTED.md`
- **Purpose**: Foundation for all API integration
- **Contains**:
  - API conventions and standards
  - Authentication setup (session cookies)
  - CORS configuration (Vite proxy)
  - Error handling patterns
  - TypeScript types
  - Development setup guide
  - Testing guide (cURL, Postman, Browser)
  - Best practices
  - Troubleshooting common issues
- **Read when**: Starting new frontend project or debugging issues

---

## 🗺️ Navigation Guide

### For New Developers

**Recommended Reading Order:**

1. **Start**: `README.md` - Get overview
2. **Setup**: `common/GETTING_STARTED.md` - Understand conventions
3. **Implement**:
   - `authentication/AUTH_API.md` - Build login/register
   - `student_management/STUDENT_API.md` - Add student selection
   - `shopping_cart/CART_API.md` - Implement cart/checkout
4. **Reference**: `QUICK_REFERENCE.md` - Keep open while coding

### For Experienced Developers

**Quick Start:**

1. Import `Webshop_API.postman_collection.json` into Postman
2. Test all endpoints
3. Use `QUICK_REFERENCE.md` for endpoint reference
4. Refer to specific API docs as needed

---

## 🎯 Use Cases

### "I need to implement login"
→ Go to: `authentication/AUTH_API.md`
→ Section: "Login" + "Frontend Integration"

### "I need to manage students"
→ Go to: `student_management/STUDENT_API.md`
→ Section: "Frontend Integration" + "Complete Student Management Flow"

### "I need to build a cart"
→ Go to: `shopping_cart/CART_API.md`
→ Section: "Complete Cart Store (Pinia)"

### "I'm getting CORS errors"
→ Go to: `common/GETTING_STARTED.md`
→ Section: "CORS Configuration"

### "I'm getting 401 errors"
→ Go to: `common/GETTING_STARTED.md`
→ Section: "Troubleshooting" → "Issue: 401 Unauthorized"

### "I need quick endpoint reference"
→ Go to: `QUICK_REFERENCE.md`

### "I want to test APIs with Postman"
→ Import: `Webshop_API.postman_collection.json`

---

## 📊 Coverage Matrix

| Feature | API Docs | Code Examples | Tests | Postman |
|---------|----------|---------------|-------|---------|
| Authentication | ✅ | ✅ | ✅ | ✅ |
| Registration | ✅ | ✅ | ✅ | ✅ |
| Student Management | ✅ | ✅ | ✅ | ✅ |
| Student Selection | ✅ | ✅ | ✅ | ✅ |
| Shopping Cart | ✅ | ✅ | ✅ | ✅ |
| Checkout | ✅ | ✅ | ✅ | ✅ |
| Error Handling | ✅ | ✅ | ❌ | ✅ |
| TypeScript Types | ✅ | ✅ | N/A | N/A |

---

## 🔄 Update Process

### When to Update Documentation

- **New API endpoint added** → Add to relevant section + Postman collection
- **API signature changed** → Update all affected docs + examples
- **New feature added** → Create new section or file
- **Bug found in example** → Fix example + test
- **User feedback** → Clarify confusing sections

### Documentation Checklist

When adding new endpoint documentation:

- [ ] Endpoint description
- [ ] Request parameters table
- [ ] Example request body
- [ ] Success response example
- [ ] Error response examples
- [ ] Frontend integration example
- [ ] cURL test example
- [ ] Add to Postman collection
- [ ] Update QUICK_REFERENCE.md
- [ ] Update README.md API reference table

---

## 📞 Support

### Documentation Issues

If you find:
- **Unclear explanations** → Request clarification
- **Missing examples** → Request examples
- **Outdated information** → Report outdated section
- **Broken code** → Report with details

### Getting Help

1. Check relevant API documentation file
2. Check `common/GETTING_STARTED.md` troubleshooting section
3. Review `QUICK_REFERENCE.md` for quick answers
4. Test with Postman collection
5. Check backend logs: `bench logs`

---

## 📝 Version History

**v1.0.0** (2024-12-20)
- Initial comprehensive API documentation
- Authentication, Student Management, Shopping Cart APIs
- Complete frontend integration examples
- Postman collection
- Quick reference guide

---

## 🎓 Learning Path

### Beginner (No Frappe Experience)

```
Day 1: README.md + GETTING_STARTED.md
       Understand: Session auth, API conventions, CORS setup

Day 2: AUTH_API.md
       Build: Login and registration forms

Day 3: STUDENT_API.md
       Build: Student selector component

Day 4: CART_API.md
       Build: Cart page and add-to-cart functionality

Day 5: Integration testing with Postman
       Test: Complete user journey
```

### Intermediate (Some API Experience)

```
Day 1: README.md + Postman collection
       Test: All endpoints with Postman

Day 2: AUTH_API.md + STUDENT_API.md
       Build: Authentication and student stores

Day 3: CART_API.md
       Build: Cart store and checkout flow

Day 4: Integration and testing
       Test: Complete application flow
```

### Advanced (Ready to Build)

```
Hour 1: Import Postman collection, test all APIs
Hour 2: Copy store examples from docs
Hour 3: Build UI components
Hour 4: Integration testing
Hour 5: Production deployment
```

---

**[← Back to Main Documentation](./README.md)**
