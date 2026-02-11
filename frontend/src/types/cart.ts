// Shopping cart type definitions

/**
 * Student interface
 * Represents a student associated with parent account
 */
export interface Student {
  name: string // Student DocType name (unique identifier)
  student_name: string // Student's display name e.g., "DAKD"
  school_unit: string // School unit e.g., "High School", "Elementary"
  grade_level?: string // Grade level
  date_of_birth?: string // Date of birth
  is_active: number // 1 if active, 0 if inactive
  is_primary: number // 1 if primary student, 0 otherwise
  notes?: string // Additional notes
}

/**
 * Student interface
 * Represents a student associated with parent account
 */
export interface StudentCart {
  name: string // Student DocType name (unique identifier)
  student_name: string // Student's display name e.g., "DAKD"
  school_unit: string // School unit e.g., "High School", "Elementary"
  is_active: number // 1 if active, 0 if inactive
  total: number // Total cart amount for the student
  itemCount: number // Total cart amount for the student
  quotation_name: string // Quotation name for the student's cart
  items: CartItem[] // Items in the student's cart
  coupon_code?: string // Applied coupon code
  discount_amount?: number // Discount amount from coupon
  original_total?: number // Total before discount
}

/**
 * Variant attribute interface
 * Represents a product variant attribute (e.g., Size: M, Color: Red)
 */
export interface VariantAttribute {
  attribute: string // Attribute name (e.g., "Size", "Color")
  value: string // Attribute value (e.g., "M", "Red")
  label: string // Display label for the attribute
  displayValue: string // Formatted display value
}

/**
 * Cart item interface
 * Represents a single item in the shopping cart
 */
export interface CartItem {
  id: string // Unique cart item ID (Quotation Item name)
  item_code: string // ERPNext item code
  productId: string // Reference to product (route or item_code)
  productType?: 'product' | 'service'
  title: string // Product title
  image: string // Product image URL
  price: number // Item price (Original Price)
  net_price: number // Item net price (Discounted Price)
  quantity: number // Item quantity
  amount: number // Total amount (price * quantity)
  net_amount?: number // Total net amount (net_price * quantity)
  description?: string // Product description
  route?: string // Website item route
  warehouse?: string // Warehouse location
  service_start_date?: string
  service_end_date?: string
  isSubscription?: number

  // Variant information
  variant_attributes?: VariantAttribute[] // Complete variant attributes array
  selectedSize?: string // Quick access to size attribute
  selectedColor?: string // Quick access to color attribute
  selectedVariant?: string // Variant ID if applicable

  // Stock information
  inStock?: boolean // Is item in stock
  stockQuantity?: number // Available stock quantity

  // Student information (for student-based carts)
  student?: string // Student DocType name (link to Student)
}

/**
 * Payload for adding item to cart
 */
export interface AddToCartPayload {
  item_code: string // ERPNext item code
  qty: number // Quantity to add
  service_start_date?: string // Required for service items
  additional_notes?: string // Optional notes
  student?: string // Optional student name to add item to specific student's cart
}

/**
 * Cart state interface
 */
export interface CartState {
  items: CartItem[]
  isLoading: boolean
  error: Error | null
}

/**
 * Cart response from backend API
 */
export interface CartResponse {
  items: CartItem[]
  total: number
  itemCount: number
  quotation_name?: string
  shipping_addresses?: any[]
  billing_addresses?: any[]
  error?: string
}
