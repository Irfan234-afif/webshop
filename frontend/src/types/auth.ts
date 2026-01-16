export interface StudentData {
  student_name: string
  school_unit: string
  grade_level: string
  date_of_birth: string
  nisn: string
}

export interface AddressData {
  address_line1: string
  address_line2: string
  city: string
  state: string
  country: string
  postal_code: string
}

export interface RegistrationFormData {
  // Step 1: Account Information
  name: string
  email: string
  phoneNumber: string
  password: string
  confirmPassword: string
  
  // Step 1: Address Information
  address: AddressData

  // Step 2: Student Information
  students: StudentData[]
}

export interface RegistrationPayload {
  name: string
  email: string
  phone_number: string
  password: string
  address: AddressData
  students: StudentData[]
}

export interface User {
  email: string
  full_name: string
  user_type: string
}

export interface Customer {
  name: string
  customer_name: string
}

export interface Student {
  student_id: string
  student_name: string
  school_unit: string
  grade_level: string
  is_active: number
}
