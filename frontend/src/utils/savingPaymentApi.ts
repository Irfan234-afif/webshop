import { call } from 'frappe-ui'
import type { CheckoutPaymentDetails } from '@/types/checkout'
import type { SavingsHistoryResponse, SavingsHistorySavingType, SavingsHistoryTransactionKind } from '@/types/cooperative'

/**
 * Create a Payment Request for Mandatory Savings
 */
export async function createSavingPayment(
  savingName: string,
  rowNames: string[],
  paymentMethodType: string,
  paymentChannel?: string
): Promise<{ payment_request: string }> {
  const response = await call('webshop.webshop.api.cooperative_payment.create_mandatory_saving_payment_request', {
    saving_name: savingName,
    row_names: JSON.stringify(rowNames),
    payment_method_type: paymentMethodType,
    payment_channel: paymentChannel
  })
  return response as { payment_request: string }
}

/**
 * Get payment details disguised as CheckoutPaymentDetails to reuse Checkout components
 */
export async function getSavingPaymentDetails(
  prName: string
): Promise<CheckoutPaymentDetails> {
  const response = await call('webshop.webshop.api.cooperative_payment.get_saving_payment_details', {
    pr_name: prName
  })
  return response as CheckoutPaymentDetails
}

/**
 * Upload payment proof for Saving payment
 */
export async function uploadSavingPaymentProof(
  prName: string,
  fileUrl: string,
  notes?: string
): Promise<{ status: string; message: string }> {
  const response = await call('webshop.webshop.api.cooperative_payment.upload_saving_payment_proof', {
    pr_name: prName,
    file_url: fileUrl,
    notes: notes
  })
  return response as { status: string; message: string }
}

/**
 * Create a Payment Request for Voluntary Savings Deposit
 */
export async function createVoluntarySavingPayment(
  amount: number,
  paymentMethodType: string,
  paymentChannel?: string
): Promise<{ payment_request: string }> {
  const response = await call('webshop.webshop.api.cooperative_payment.create_voluntary_saving_deposit_payment', {
    amount: amount,
    payment_method_type: paymentMethodType,
    payment_channel: paymentChannel
  })
  return response as { payment_request: string }
}

/**
 * Create a Voluntary Saving Withdrawal request
 */
export async function createVoluntarySavingWithdrawal(
  amount: number,
  paymentMethod: string,
  bankDetails?: {
    bank_name: string,
    account_number: string,
    account_holder_name: string
  }
): Promise<{ status: string; name: string }> {
  const response = await call('webshop.webshop.api.cooperative_payment.create_voluntary_saving_withdrawal', {
    amount: amount,
    payment_method: paymentMethod,
    bank_details: bankDetails ? JSON.stringify(bankDetails) : null
  })
  return response as { status: string; name: string }
}

/**
 * Fetch unified savings transaction history
 */
export async function getSavingsHistory(
  page = 1,
  pageLength = 20,
  savingType?: SavingsHistorySavingType,
  transactionKind?: SavingsHistoryTransactionKind
): Promise<SavingsHistoryResponse> {
  const response = await call('webshop.webshop.api.cooperative_payment.get_savings_history', {
    page,
    page_length: pageLength,
    saving_type: savingType || null,
    transaction_kind: transactionKind || null
  })
  return response as SavingsHistoryResponse
}
