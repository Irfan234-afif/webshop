import { call } from 'frappe-ui'

export interface BillPaymentResponse {
  sales_invoice: string
  payment_request: string
  payment_url: string
  redirect_type: 'gateway' | 'manual' | 'virtual_account'
  virtual_account?: {
    number: string
    bank: string
    expiry: string
  }
}

export interface BillPaymentDetails {
  sales_invoice: {
    name: string
    customer: string
    grand_total: number
    outstanding_amount: number
    due_date: string
    posting_date: string
    subscription: string
    student_name: string
  }
  payment_method: {
    name: string
    title: string
    payment_type: string
    need_admin_approval: boolean
    payment_duration?: number
  } | null
  bank_account_details: {
    account_number: string
    bank_name: string
    account_holder: string
    branch_code?: string
  } | null
  payment_request: {
    name: string
    status: 'Pending' | 'Approved' | 'Rejected' | 'Paid'
    payment_proof: string | null
    remarks: string | null
  } | null
  virtual_account?: {
    number: string
    bank: string
    expiry: string
  }
}

export async function initiateBillPayment(
  salesInvoiceName: string,
  paymentMethodType: string,
  paymentChannel?: string
): Promise<BillPaymentResponse> {
  const response = await call('webshop.webshop.api.pay_bill_request.initiate_bill_payment', {
    sales_invoice_name: salesInvoiceName,
    payment_method_type: paymentMethodType,
    payment_channel: paymentChannel
  })
  return response as BillPaymentResponse
}

export async function getBillPaymentDetails(
  salesInvoiceName: string
): Promise<BillPaymentDetails> {
  const response = await call('webshop.webshop.api.billing.get_bill_payment_details', {
    sales_invoice_name: salesInvoiceName
  })
  return response as BillPaymentDetails
}


// Upload payment proof for bill
export async function uploadBillPaymentProof(
  salesInvoiceName: string,
  fileUrl: string,
  notes?: string
): Promise<{ status: string; message: string; payment_request_id: string }> {
  const response = await call('webshop.webshop.api.pay_bill_request.upload_payment_proof', {
    sales_invoice: salesInvoiceName,
    file_url: fileUrl,
    notes
  })
  return response as { status: string; message: string; payment_request_id: string }
}

