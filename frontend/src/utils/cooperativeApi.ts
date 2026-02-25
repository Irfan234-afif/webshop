import { call } from 'frappe-ui'
import type { CheckoutPaymentDetails, PaymentMethod } from '@/types/checkout'
import type {
  CooperativeMemberFormData,
  CooperativeSettings,
  MembershipStatus,
  CooperativeRegistrationResponse,
  CooperativePaymentRequestResponse
} from '@/types/cooperative'

/**
 * Fetch cooperative registration settings (fees)
 */
export async function getRegistrationSettings(): Promise<CooperativeSettings> {
  const response = await call('webshop.webshop.api.cooperative.get_registration_settings')
  return response as CooperativeSettings
}

/**
 * Fetch current user's membership status
 */
export async function getMembershipStatus(): Promise<MembershipStatus> {
  const response = await call('webshop.webshop.api.cooperative.get_membership_status')
  return response as MembershipStatus
}

/**
 * Submit Cooperative Member registration form
 */
export async function registerMember(data: CooperativeMemberFormData): Promise<CooperativeRegistrationResponse> {
  const response = await call('webshop.webshop.api.cooperative.register_member', {
    data: data
  })
  return { success: true, message: 'Registration submitted successfully', member_name: response.name }
}

/**
 * Create a Payment Request for cooperative registration
 */
export async function createRegistrationPayment(
  memberName: string,
  paymentMethodType: string,
  paymentChannel?: string
): Promise<CooperativePaymentRequestResponse> {
  const response = await call('webshop.webshop.api.cooperative_payment.create_registration_payment_request', {
    member_name: memberName,
    payment_method_type: paymentMethodType,
    payment_channel: paymentChannel
  })
  return response as CooperativePaymentRequestResponse
}

/**
 * Get payment details disguised as CheckoutPaymentDetails to reuse Checkout components
 */
export async function getCooperativePaymentDetails(
  memberName: string
): Promise<CheckoutPaymentDetails> {
  const response = await call('webshop.webshop.api.cooperative.get_cooperative_payment_details', {
    member_name: memberName
  })
  return response as CheckoutPaymentDetails
}

/**
 * Upload payment proof for Cooperative Registration payment
 */
export async function uploadCoopPaymentProof(
  memberName: string,
  fileUrl: string,
  notes?: string
): Promise<{ status: string; message: string }> {
  const response = await call('webshop.webshop.api.cooperative.upload_cooperative_payment_proof', {
    member_name: memberName,
    file_url: fileUrl,
    notes: notes
  })
  return response as { status: string; message: string }
}
