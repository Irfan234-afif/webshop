import { call } from 'frappe-ui'
import type {
  CheckoutData,
  PaymentMethod,
  OrderConfirmationResponse,
  UpdatePickupTypeParams,
  UpdatePaymentMethodParams,
  CheckoutPaymentDetails
} from '@/types/checkout'

export async function getCheckoutData(studentName?: string): Promise<CheckoutData> {
  const response = await call('webshop.webshop.api.checkout.get_checkout_data', {
    student_name: studentName
  })
  return response as CheckoutData
}

export async function updatePickupType(params: UpdatePickupTypeParams & { quotation_name: string }): Promise<{ success: boolean; message: string; quotation_name: string }> {
  const response = await call('webshop.webshop.api.checkout.update_pickup_type', {
    quotation_name: params.quotation_name,
    pickup_type: params.pickup_type,
    delivery_date: params.delivery_date,
    delivery_time: params.delivery_time
  })
  return response as { success: boolean; message: string; quotation_name: string }
}

export async function updatePaymentMethod(params: UpdatePaymentMethodParams & { quotation_name: string }): Promise<{ success: boolean; message: string; quotation_name: string }> {
  const response = await call('webshop.webshop.api.checkout.update_payment_method', {
    quotation_name: params.quotation_name,
    payment_method_type: params.payment_method_type,
    payment_channel: params.payment_channel
  })
  return response as { success: boolean; message: string; quotation_name: string }
}

export async function getPaymentMethods(): Promise<PaymentMethod[]> {
  const response = await call('webshop.webshop.api.checkout.get_payment_methods')
  return response as PaymentMethod[]
}

export async function placeOrderWithPayment(quotationName: string, paymentChannel?: string): Promise<OrderConfirmationResponse> {
  const response = await call('webshop.webshop.api.checkout.place_order_with_payment', {
    quotation_name: quotationName,
    payment_channel: paymentChannel
  })
  return response as OrderConfirmationResponse
}

export async function setActiveStudent(studentName: string): Promise<{ success: boolean; student_name: string }> {
  const response = await call('webshop.webshop.shopping_cart.student_utils.set_active_student', {
    student_name: studentName
  })
  return response as { success: boolean; student_name: string }
}

export async function createAddress(params: import('@/types/checkout').CreateAddressParams): Promise<{ success: boolean; address_name: string; address_title: string; display: string }> {
  const response = await call('webshop.webshop.api.checkout.create_customer_address', {
    address_title: params.address_title,
    address_line1: params.address_line1,
    city: params.city,
    phone: params.phone,
    email_id: params.email_id,
    student_name: params.student_name
  })
  return response as { success: boolean; address_name: string; address_title: string; display: string }
}

export async function getCheckoutPaymentDetails(
  salesOrderName: string
): Promise<CheckoutPaymentDetails> {
  const response = await call('webshop.webshop.api.checkout.get_checkout_payment_details', {
    sales_order_name: salesOrderName
  })
  return response as CheckoutPaymentDetails
}

export async function uploadPaymentProof(
  salesOrder: string,
  fileUrl: string,
  notes?: string
): Promise<{ status: string; message: string; approval_id: string }> {
  const response = await call('webshop.webshop.api.checkout.upload_payment_proof', {
    sales_order: salesOrder,
    file_url: fileUrl,
    notes
  })
  return response as { status: string; message: string; approval_id: string }
}
