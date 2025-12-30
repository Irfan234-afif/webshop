# Dynamic Payment Method System Documentation

## Overview
This document describes the implementation of a dynamic payment method system for the webshop application, replacing the previously hardcoded payment methods. The system allows administrators to manage payment methods dynamically without code changes.

## System Architecture

### Core Components

#### 1. Webshop Payment Method Doctype
**Purpose:** Stores all available payment methods with their configurations.

**Fields:**
- `payment_method_name` (Data, Required, Unique): Internal identifier for the payment method
- `title` (Data, Required): Display name for the payment method
- `description` (Text): Detailed description of the payment method
- `payment_type` (Select, Required): Type of payment method
  - Options: "Transfer Manual", "Payment Gateway"
- `payment_gateway_account` (Link): Payment gateway account (for Payment Gateway type)
- `bank_account` (Link): Bank account (for Transfer Manual type)
- `account_holder_name` (Data): Account holder name (for Transfer Manual type)
- `need_admin_approval` (Check): Whether admin approval is required
- `enabled` (Check): Whether the payment method is active
- `icon` (Data): Icon identifier for the payment method
- `sort_order` (Int): Display order of the payment method

**Validation:**
- For Transfer Manual: `bank_account` and `account_holder_name` are required
- For Payment Gateway: `payment_gateway_account` is required

#### 2. Payment Request Approval Workflow
**Purpose:** Uses ERPNext's standard Payment Request DocType for manual payment approvals with custom fields.

**Custom Fields Added to Payment Request:**
- `payment_proof` (Attach): Customer upload of payment proof
- `remarks` (Text): Admin notes or rejection reasons
- `admin_approval_by` (Link to User, Read-only): Who approved/rejected
- `admin_approval_time` (Datetime, Read-only): When approved/rejected

**Approval Status (docstatus-based):**
- `docstatus = 0` (Draft): Pending approval
- `docstatus = 1` (Submitted): Approved - payment marked as paid
- `docstatus = 2` (Cancelled): Rejected

## Data Flow

### Payment Method Selection Flow
```
Customer → Checkout Page → Payment Method Selection → 
API: get_payment_methods() → Filter by enabled methods → 
Display available payment methods → Customer selects method → 
API: update_payment_method() → Validate against doctype → 
Save to Quotation/Sales Order
```

### Payment Processing Flow
```
Customer places order → Payment method selected →
If Payment Gateway type → Create Payment Request → Redirect to gateway
If Transfer Manual type →
  If need_admin_approval → Create Payment Request (Draft) →
  Customer uploads proof → Admin submits/cancels Payment Request →
  On Submit: Payment marked as paid via set_as_paid()
  If no admin approval → Direct to manual transfer instructions
```

### Admin Approval Flow
```
Admin → Payment Request List → Filter by Draft status →
Select Payment Request → Review payment proof →
Click "Approve Payment" (Submit) → Payment marked as paid OR
Click "Reject Payment" (Cancel) → Adds rejection reason to remarks
```

## Database Tables

### New Tables Created

#### 1. `tabWebshop Payment Method`
| Column | Type | Description |
|--------|------|-------------|
| name | varchar(140) | Primary key, auto-generated from payment_method_name |
| payment_method_name | varchar(140) | Internal identifier |
| title | varchar(140) | Display title |
| description | text | Payment method description |
| payment_type | varchar(140) | "Transfer Manual" or "Payment Gateway" |
| payment_gateway_account | varchar(140) | Reference to Payment Gateway Account |
| bank_account | varchar(140) | Reference to Bank Account |
| account_holder_name | varchar(140) | Account holder name |
| need_admin_approval | int(1) | 1 if admin approval needed, 0 otherwise |
| enabled | int(1) | 1 if enabled, 0 if disabled |
| icon | varchar(140) | Icon identifier |
| sort_order | int(11) | Display order |

#### 2. Payment Request Custom Fields
Custom fields added to `tabPayment Request`:
| Field | Type | Description |
|-------|------|-------------|
| payment_proof | varchar(140) | File path to payment proof |
| remarks | text | Admin notes or rejection reasons |
| admin_approval_by | varchar(140) | User who approved/rejected |
| admin_approval_time | datetime | Time of approval/rejection |

**Status Mapping:**
- Frontend receives status as string: "Pending" / "Approved" / "Rejected"
- Backend stores as docstatus: 0 / 1 / 2
- API handles mapping automatically

### Modified Tables
The `tabQuotation` and `tabSales Order` tables have their custom fields updated:
- `payment_method_type` field now references `Webshop Payment Method` instead of being a select field
- `pickup_date` and `pickup_time_slot` fields were removed
- Uses the default `delivery_date` field in Sales Order (no custom field needed)

## API Endpoints

### 1. `get_payment_methods()`
**Purpose:** Fetches available payment methods from the database.
**Returns:** List of payment methods with name, title, description, enabled status, icon, need_admin_approval, and payment_type.

### 2. `update_payment_method(quotation_name, payment_method_type)`
**Purpose:** Updates the payment method for a quotation.
**Validation:** Checks if the payment method exists and is enabled.

### 3. `get_payment_gateway_url(sales_order_name, payment_method_type)`
**Purpose:** Generates payment URL based on payment method type.
**Logic:**
- For Payment Gateway: Creates Payment Request and returns gateway URL
- For Transfer Manual: Creates Payment Request (Draft) if admin approval needed

### 4. `create_payment_request_for_manual_approval(sales_order, payment_method)`
**Purpose:** Creates Payment Request in Draft status for manual approvals.
**Returns:** Payment Request document (docstatus=0)

## Frontend Components

### 1. Payment Method Selector
**Location:** `/frontend/src/views/Checkout/components/PaymentMethodSelector.vue`
**Functionality:** Dynamically displays payment methods fetched from the backend.

### 2. Checkout Store
**Location:** `/frontend/src/stores/checkout.ts`
**Changes:**
- Uses `deliveryDate` instead of separate `pickupDate` and `pickupTimeSlot`
- Updated validation logic for step progression
- Modified API calls to match backend changes

## Migration Process

### 1. Payment Method Migration
**Patch:** `migrate_payment_methods_to_new_doctype`
- Converts hardcoded payment methods to records in the new doctype
- Preserves existing configurations and settings

### 2. Custom Fields Update
**Patch:** `update_checkout_custom_fields_for_dynamic_payment`
- Replaces select field with Link field referencing the new doctype
- Updates both Quotation and Sales Order forms

### 3. Date/Time Fields Update
**Patch:** `update_checkout_custom_fields_for_delivery_date`
- Removes `pickup_date` and `pickup_time_slot` fields
- Adds `delivery_date` datetime field
- Updates both Quotation and Sales Order forms

## Admin Interface

### Payment Request Form
**Location:** Payment Request DocType
**Features for Manual Payment Approval:**
- **Approve Payment** button (visible on Draft status)
  - Submits Payment Request (docstatus=1)
  - Calls `set_as_paid()` to create Payment Entry
  - Captures admin user and timestamp
- **Reject Payment** button (visible on Draft status)
  - Prompts for rejection reason
  - Adds reason to remarks field
  - Cancels Payment Request (docstatus=2)
  - Captures admin user and timestamp
- View payment proof uploaded by customer
- Standard ERPNext document permissions and workflow

## Usage Examples

### Creating a New Payment Method
1. Go to Webshop Payment Method list in ERPNext
2. Click "New"
3. Fill in the details:
   - Payment Method Name: Unique identifier
   - Title: Display name
   - Description: Explanation for customers
   - Payment Type: "Transfer Manual" or "Payment Gateway"
   - Based on type, fill in either bank account details or payment gateway account
   - Check "Need Admin Approval" if required
   - Set "Enabled" to make it available
4. Save the record

### Handling Manual Payments Requiring Approval
1. Customer selects the payment method during checkout
2. System creates a Payment Request in Draft status (docstatus=0)
3. Customer uploads payment proof
4. Admin navigates to Payment Request List
5. Admin filters by Draft status and reviews payment proof
6. Admin clicks:
   - **Approve Payment**: Submits document, marks payment as paid
   - **Reject Payment**: Enters reason, cancels document
7. Frontend automatically displays updated status to customer

## Benefits

1. **Flexibility:** Add, modify, or remove payment methods without code changes
2. **Scalability:** Easy to introduce new payment types
3. **Control:** Admin approval workflow for manual payments
4. **Maintainability:** Centralized payment method management
5. **User Experience:** Consistent and dynamic payment options

## Security Considerations

1. **Permission Control:** Payment Approval actions require appropriate permissions
2. **Validation:** Backend validation ensures only valid payment methods are used
3. **Audit Trail:** All approval actions are tracked with user and timestamp
4. **Data Integrity:** Foreign key constraints ensure data consistency

## Testing Points

1. Payment methods display correctly in frontend
2. Payment method selection updates quotation properly
3. Payment gateway flows work as expected
4. Manual payment approval workflow functions correctly
5. Admin approval interface works properly
6. Migration preserves existing data
7. Delivery date field works correctly in checkout flow