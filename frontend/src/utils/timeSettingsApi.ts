import { call } from 'frappe-ui'

export interface PickupTimeSettings {
  // Time settings
  morning_start: string
  morning_end: string
  afternoon_start: string
  afternoon_end: string
  interval: number
  // Date settings
  minimum_days_ahead: number
  weekdays_only: number
  disabled_date_ranges: DisabledDateRange[]
}

export interface DisabledDateRange {
  from_date: string | null
  to_date: string | null
  reason: string
}

/**
 * Fetch pickup time settings from Webshop Settings
 */
export async function getPickupTimeSettings(): Promise<PickupTimeSettings> {
  try {
    const response = await call('/api/method/webshop.webshop.doctype.webshop_settings.webshop_settings.get_pickup_time_settings')
    
    return response as PickupTimeSettings
  } catch (error) {
    throw error
  }
}
