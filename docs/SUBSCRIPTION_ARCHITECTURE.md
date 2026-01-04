# Subscription System Architecture

**Last Updated:** 2025-12-30
**Scope:** Webshop & ERPNext Integration
**Purpose:** Technical reference for future AI agents and developers.

## 1. High-Level Concept: "Subscription Request" Flow

The Webshop uses a **Direct Subscription Checkout** model that is distinct from the standard product cart flow.

- **Trigger**: User clicks "Buy Now" on a Subscription Item's detail page.
- **Flow**: Bypasses the standard Cart. Enters a dedicated 2-step Subscription Checkout.
- **result**: Creates a `Subscription Request` document.
- **Approval**: Admin approves the `Subscription Request`, which then triggers the creation of the actual `Subscription` and/or `Sales Invoice` in ERPNext.

### Why this approach?

1.  **Approval Workflow**: Subscriptions require admin vetting before activation.
2.  **Simplified UX**: Removes cart complexity for simple service subscriptions.
3.  **Dedicated Data**: Captures specific subscription data (Start Date, Notes) that doesn't fit neatly into a standard mixed cart line item.

---

## 2. User Experience (Frontend)

### A. Product Detail Page

- **Subscription Items**: Identified by `is_subscription_item` flag.
- **Action**: "Add to Cart" is replaced/disabled. "Subscribe Now" (or similar) button takes user directly to Subscription Checkout.

### B. Subscription Checkout Flow

This is a dedicated route/flow, separate from the standard checkout.

**Step 1: Details**

- User inputs `Start Date`.
- User inputs `Notes` (Instructions, special requests).

**Step 2: Confirmation**

- Shows summary of the plan.
- Shows estimated costs.
- "Confirm_Request" button.

**Step 3: Success**

- "Thank you" page indicating the request has been submitted for approval.

---

## 3. Backend Architecture

### A. DocType: `Subscription Request`

**Status**: ✅ Implemented and Tested

A submittable DocType (`is_submittable = 1`) to capture subscription requests pending admin approval.

**Key Fields:**

- `naming_series`: `SR-.MM.-.YYYY.-.#####`
- `customer`: Link to Customer (auto-resolved via `get_party()`)
- `subscription_plan`: Link to Subscription Plan
- `item`: Link to Item (Read Only)
- `start_date`: Date (Required) - Subscription start date
- `end_date`: Date (Auto-calculated or Admin-editable) - Subscription end date
- `holiday_list`: Link to Holiday List (Optional) - For effective days calculation
- `effective_days`: Int (Read Only, Auto-calculated) - Working days excluding holidays
- `notes`: Small Text - Customer instructions/special requests
- `subscription_ref`: Link to Subscription (Read Only) - Populated on submit
- `amended_from`: Link to Subscription Request (Standard amend support)

**Technical Implementation:**

- Location: `webshop/webshop/doctype/subscription_request/`
- Module: Webshop
- Permissions: System Manager (create, submit, amend, cancel)

### B. Submission Workflow

**Draft State (User-Created)**:

- Created via `create_subscription_request` API
- Customer auto-resolved (creates if missing via `get_party()`)
- Accessible to System Managers in Frappe Desk

**Submission (Admin Action)**:

- Admin reviews and submits in Desk
- Triggers `on_submit()` hook:
  1. Validates required fields (`subscription_plan`, `item`, `start_date`)
  2. Calls `create_subscription_from_request()`
  3. **Consumption-Based Quantity Calculation** (for Post-Paid + Day-based plans):
     - Checks if `billing_timing = "Post-Paid"` AND `billing_interval = "Day"`
     - If true, calculates `qty = effective_days` (total days - holidays)
     - Otherwise, uses default `qty = 1`
  4. Creates ERPNext `Subscription` document:
     - Maps `start_date` and `end_date`
     - Adds plan via `append("plans", {"plan": ..., "qty": <calculated_qty>})`
     - Sets `generate_invoice_at` based on billing timing
     - Inserts and saves to activate
  5. Links Subscription via `subscription_ref`
  6. Displays success message

**No Sales Invoice Generation**: Focus on Post-Paid model - invoices generated automatically by ERPNext Subscription system at period end.

### C. Deprecated / Removed Logic

- _Old Flow_: Sales Order -> Subscription autogeneration hook is **DEPRECATED** for this specific flow, though it might remain for legacy or mixed-cart scenarios if needed. for now, we assume this replaces it for subscription items.

### D. Consumption-Based (Post-Paid Day-Based) Subscriptions

**Feature**: Automatic quantity calculation for consumption-based subscriptions.

**Applies To**: Subscription Plans with:

- `billing_timing = "Post-Paid"`
- `billing_interval = "Day"`

**How It Works**:

1. When a Subscription Request is created or updated, the system automatically:

   - Calculates `end_date` based on the plan's billing interval
   - Calculates `effective_days` = (end_date - start_date + 1) - holidays

2. When the request is submitted, the system:
   - Checks if the plan is Post-Paid AND Day-based
   - Uses `qty = effective_days` instead of default `qty = 1`
   - This allows the subscription price to scale based on actual working days

**Example**:

- Subscription Plan: "Internet Service - Daily Rate" @ IDR 50,000/day
- Start Date: 2026-01-06 (Monday)
- End Date: 2026-01-10 (Friday) - Auto-calculated for 5 days
- Holiday List: Contains 2026-01-08 (Wednesday - Public Holiday)
- **Effective Days**: 5 - 1 = 4 days
- **Result**: Subscription created with `qty = 4`, invoice will be 4 × 50,000 = IDR 200,000

**Benefits**:

- Fair billing based on actual service days
- Automatic exclusion of holidays
- No manual quantity adjustment needed

---

## 4. Schema Extensions

### `Item` (Standard)

- `is_subscription_item` (Check): Identifies items that trigger this specific flow.

---

## 5. API Endpoints

**File**: `webshop/webshop/api/subscription_checkout.py`

### `create_subscription_request(data)`

- **Method**: POST
- **Auth**: Required (checks `frappe.session.user`)
- **Endpoint**: `/api/method/webshop.webshop.api.subscription_checkout.create_subscription_request`
- **Payload**:
  ```json
  {
    "item_code": "SUB-ITEM-001",
    "start_date": "2025-01-15",
    "end_date": "2025-12-31", // Optional
    "notes": "Please start ASAP"
  }
  ```
- **Process**:
  1. Validates required fields
  2. Resolves customer via `get_party()` (auto-creates if missing)
  3. Fetches subscription plan from Item
  4. Creates Subscription Request (Draft)
  5. Returns document name
- **Returns**: `"SR-12-2024-00001"`

### `get_subscription_item_details(item_code)`

- **Method**: GET
- **Auth**: Guest allowed
- **Endpoint**: `/api/method/webshop.webshop.api.subscription_checkout.get_subscription_item_details`
- **Returns**:
  ```json
  {
    "item_name": "Monthly Subscription",
    "item_code": "SUB-001",
    "image": "/files/image.jpg",
    "description": "HTML content",
    "plan_name": "Basic Plan",
    "cost": 100000,
    "billing_interval": "Month",
    "billing_timing": "Post-Paid"
  }
  ```
- **Features**:
  - Image fallback: Item.image → Website Item.website_image
  - Returns null if not a subscription item

---

## 6. Testing & Verification

### Automated Tests ✅

**File**: `webshop/tests/test_subscription_request.py`  
**Status**: All 4 tests passing

1. **`test_create_request_api`**: API request creation with dates
2. **`test_submit_creates_subscription`**: Subscription generation on submit
3. **`test_get_item_details`**: Item details API accuracy
4. **`test_auto_create_customer`**: Customer auto-creation flow

**Run**: `bench run-tests --module webshop.tests.test_subscription_request`

### Frontend Testing Checklist

- [x] "Langganan Sekarang" button displays for subscription items
- [x] Button redirects to `/subscription-checkout/:item_code`
- [x] Item image displays (with fallback)
- [x] Description renders HTML correctly
- [x] Start Date and End Date pickers functional
- [x] Step navigation works (1 → 2)
- [x] Confirmation summary displays all data
- [x] Success popup appears after submission

### Backend Testing Checklist

- [x] Subscription Request creates in Draft state
- [x] All fields populate correctly (including end_date)
- [x] Customer links correctly (or auto-creates)
- [x] Admin can submit request
- [x] ERPNext Subscription creates and activates
- [x] `subscription_ref` links back correctly
- [x] Post-Paid configuration applies
- [x] Start/End dates propagate to Subscription

### Integration Points Verified

- ✅ Customer resolution via `webshop.shopping_cart.cart.get_party()`
- ✅ ERPNext Subscription DocType compatibility
- ✅ Subscription Plan field mapping
- ✅ Child table handling (plans)
- ✅ CSRF token validation
- ✅ Permission handling (`ignore_permissions=True` where needed)
