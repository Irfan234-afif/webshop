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
  items?: Array<{ 
    item_code: string; 
    item_name: string; 
    qty: number;
    image?: string;
    amount?: number 
  }>
  per_billed: number
  payment_method_type?: string
  payment_request_status?: string
}