declare module 'vue-tel-input' {
  import { DefineComponent } from 'vue'
  
  export interface VueTelInputOptions {
    placeholder?: string
    required?: boolean
    styleClasses?: string
  }
  
  export interface VueTelInputDropdownOptions {
    showDialCodeInList?: boolean
    showDialCodeInSelection?: boolean
    showFlags?: boolean
    showSearchBox?: boolean
  }
  
  export interface VueTelInputValidation {
    valid: boolean
    country?: {
      name: string
      iso2: string
      dialCode: string
    }
  }
  
  export const VueTelInput: DefineComponent<{
    modelValue?: string
    mode?: 'auto' | 'international' | 'national'
    defaultCountry?: string
    preferredCountries?: string[]
    inputOptions?: VueTelInputOptions
    dropdownOptions?: VueTelInputDropdownOptions
    onValidate?: (validation: VueTelInputValidation) => void
  }>
}
