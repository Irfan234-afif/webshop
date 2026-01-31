// Return Request Type Definitions

export interface ReturnReason {
  name: string
  reason_name: string
  description?: string
  enabled?: number
}

export interface RefundPaymentMethod {
  name: string
  title: string
  payment_type: 'Cash' | 'Transfer Manual'
  mode_of_payment: string
  description?: string
  bank_account?: string
}

export interface ReturnRequestFormData {
  sales_order: string
  return_reason: string
  other_reason?: string
  supporting_documents: string[] // Array of file URLs for multiple uploads
  refund_payment_mode: string
  bank_name?: string
  account_number?: string
  account_holder_name?: string
}

export interface ReturnRequest {
  name: string
  sales_order: string
  posting_date: string
  return_reason: string
  other_reason?: string
  supporting_documents?: string
  refund_payment_mode: string
  payment_method_title?: string
  payment_type?: string
  bank_name?: string
  account_number?: string
  account_holder_name?: string
  status: 'Draft' | 'Pending Approval' | 'Approved' | 'Processing' | 'Completed' | 'Rejected'
  return_delivery_note?: string
  credit_note?: string
  workflow_state?: string
  items?: ReturnRequestItem[]
  grand_total?: number
  transaction_date?: string
  student?: string
  student_name?: string
  pickup_type?: string
  pickup_schedule?: string
  virtual_account?: string
  payment_method_type?: string
  coupon_code?: string
  discount_amount?: number
}

export interface ReturnRequestItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  sales_order_item?: string
}

export interface EligibleOrder {
  sales_order: string
  transaction_date: string
  grand_total: number
  delivery_note: string
  delivery_date: string
  days_since_delivery: number
  eligible_until: string
  items: OrderItem[]
  customer?: string
  student_name?: string
  order_type?: string
}

export interface OrderItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  description?: string
  image?: string
}

export interface UploadedFile {
  file_url: string
  file_name: string
  file_size: number
}

export interface WebshopSettings {
  enable_returns?: number
  return_eligibility_days?: number
  return_policy_description?: string
}
