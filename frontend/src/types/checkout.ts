import type { CartItem } from './cart'
import type { Student } from './student'

export interface CheckoutData {
  quotation_name: string
  items: CheckoutItem[]
  subtotal: number
  voucher_discount: number
  member_discount: number
  total: number
  student?: string
  pickup_type?: string
  payment_method_type?: string
  delivery_date?: string
  delivery_time?: string
  has_address: boolean
  shipping_address?: string
  billing_address?: string
}

export interface CreateAddressParams {
  address_title: string
  address_line1: string
  city: string
  phone: string
  email_id?: string
  student_name?: string
}

export interface CheckoutItem {
  item_code: string
  item_name: string
  qty: number
  rate: number
  amount: number
  image?: string
}

export interface BankAccountDetails {
  account_number: string
  bank_name: string
  account_holder: string
  branch_code?: string
}

export interface PaymentChannel {
  channel_code: string
  channel_name: string
  description?: string
  icon?: string
}

export interface PaymentMethod {
  name: string
  label: string
  description: string
  enabled: boolean
  icon: string
  need_admin_approval?: boolean
  payment_type?: 'Transfer Manual' | 'Payment Gateway'
  bank_account_details?: BankAccountDetails
  payment_channels?: PaymentChannel[]
}

export interface VirtualAccountDetails {
  number: string
  bank: string
  expiry: string
}

export interface OrderConfirmationResponse {
  sales_order: string
  payment_url: string
  redirect_type: 'gateway' | 'manual' | 'cash' | 'virtual_account'
  virtual_account?: VirtualAccountDetails
}

export interface CheckoutPaymentDetails {
  sales_order: {
    name: string
    customer: string
    grand_total: number
    delivery_date: string | null
    student_name: string | null
    pickup_type: string | null
    unit: string | null
  }
  payment_method: {
    name: string
    title: string
    payment_type: string
    need_admin_approval: boolean
  }
  bank_account_details: BankAccountDetails | null
  payment_approval: {
    name: string
    status: 'Pending' | 'Approved' | 'Rejected'
    payment_proof: string | null
    remarks: string | null
  } | null
  virtual_account?: VirtualAccountDetails
  payment_status?: string
}

export interface PickupInfo {
  pickup_type: string
  delivery_date?: string
  delivery_time?: string
}

export interface UpdatePickupTypeParams {
  pickup_type: string
  delivery_date?: string
  delivery_time?: string
}

export interface UpdatePaymentMethodParams {
  payment_method_type: string
}
