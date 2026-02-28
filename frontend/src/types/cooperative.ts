export interface CooperativeMemberFormData {
  nik: string
  full_name: string
  place_of_birth: string
  date_of_birth: string
  gender: string
  occupation: string
  marital_status: string
  email: string
  phone_number: string
  relationship_with_cooperative: string
  ktp_photo: string
  // KTP Address
  province: string
  city: string
  district: string
  sub_district: string
  postal_code: string
  full_address: string
  // Emergency Contact
  emergency_contact_name: string
  emergency_contact_phone: string
  emergency_contact_relationship: string
  emergency_contact_address: string
}

export interface CooperativeSettings {
  principal_saving_amount: number
  mandatory_saving_amount: number
  total_registration_amount: number
}

export interface MembershipStatus {
  is_member: boolean
  name?: string
  status?: string
  total_registration_amount?: number
  principal_saving_amount?: number
  mandatory_saving_amount?: number
  payment_request?: string
}

export interface CooperativeRegistrationResponse {
  success: boolean
  message: string
  member_name?: string
}

export interface CooperativePaymentRequestResponse {
  payment_request: string
}

export type SavingsHistoryType = 'registration' | 'mandatory' | 'voluntary_deposit' | 'voluntary_withdrawal'

export type SavingsHistorySavingType = 'Simpanan Pokok' | 'Simpanan Wajib' | 'Simpanan Sukarela'

export type SavingsHistoryTransactionKind = 'Pembayaran' | 'Setoran' | 'Pengambilan' | 'Simpanan Pokok'

export interface SavingsHistoryItem {
  date: string
  type: SavingsHistoryType
  period: string | null
  amount: number
  due_date: string | null
  saving_type: SavingsHistorySavingType
  transaction_kind: SavingsHistoryTransactionKind
  payment_date: string | null
  payment_method: string
  status: string
  reference_doctype: string
  reference_name: string
  payment_request: string | null
}

export interface SavingsHistoryResponse {
  items: SavingsHistoryItem[]
  total_count: number
  page: number
  page_length: number
  has_more: boolean
}
