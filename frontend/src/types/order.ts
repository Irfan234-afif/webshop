export interface OrderItem {
  item_code: string; 
  item_name: string; 
  qty: number;
  image?: string;
  amount?: number 
}

export interface OrderTax {
  description: string
  tax_amount: number
  idx?: number
}

export interface Order {
  name: string
  grand_total: number
  total_qty: number
  transaction_date: string
  status: string
  student: string
  student_status?: string
  student_class?: string
  order_type: string
  delivery_estimate?: string
  delivery_date?: string
  shipping_cost?: number
  recipient_name?: string
  recipient_phone?: string
  is_completed?: boolean
  school_unit?: string
  pickup_type?: string
  pickup_schedule?: string
  voucher_amount?: number
  discount_amount?: number
  virtual_account?: string
  payment_gateway?: string
  items?: OrderItem[]
  per_billed: number
  payment_method_type?: string
  payment_type?: string
  delivery_image?: string
  coupon_code?: string
  taxes?: OrderTax[]
  payment_request_status?: string
  ecommerce_delivery_status?: string
  shipped_date?: string
  delivered_date?: string
}

export interface SubscriptionRequest {
  name: string
  type: 'request'
  customer: string
  subscription_plan: string
  plan_name: string
  item: string
  item_name: string
  start_date: string
  end_date?: string
  notes?: string
  status: 'Draft' | 'Submitted' | 'Active' | 'Approved' | 'Cancelled'
  docstatus: number
  subscription_ref?: string
  image?: string
  cost?: number
  billing_interval?: string
  creation?: string
  modified?: string
}

export interface SubscriptionPlan {
  plan: string
  plan_name: string
  qty: number
}

export interface ActiveSubscription {
  name: string
  type: 'subscription'
  customer: string
  status: 'Active' | 'Past Due Date' | 'Cancelled' | 'Unpaid'
  start_date: string
  end_date?: string
  current_invoice_start?: string
  current_invoice_end?: string
  plans: SubscriptionPlan[]
  plan_name?: string
  image?: string
  item_name?: string
  cost?: number
  billing_interval?: string
  creation?: string
  modified?: string
}

export type SubscriptionItem = SubscriptionRequest | ActiveSubscription