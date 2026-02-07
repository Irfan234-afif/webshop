<template>
  <div class="pickup-type-selector">
    <template v-if="isLoading">
      <div class="flex items-center justify-center py-12">
        <div class="spinner"></div>
      </div>
    </template>
    <template v-else>
    <div class="space-y-4">
      <!-- Option 1: Ambil Di Koperasi -->
      <div class="pickup-option" :class="{ 'selected': selectedType === 'Ambil di koperasi' }"
        @click="selectPickupType('Ambil di koperasi')">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-lg mb-2">Ambil Di Koperasi</h3>
            <p class="text-sm text-gray-600">
              Pengambilan dapat di lakukan +1 hari setelah pembayaran oleh orang tua, anak pemesan & saudara di koperasi
            </p>
          </div>
          <div class="ml-4">
            <div class="radio-button" :class="{ 'checked': selectedType === 'Ambil di koperasi' }">
              <div v-if="selectedType === 'Ambil di koperasi'" class="radio-dot"></div>
            </div>
          </div>
        </div>

        <!-- Delivery Date & Time Selection (shown when Ambil di koperasi is selected) -->
        <div v-if="selectedType === 'Ambil di koperasi'" class="mt-4 pt-4 border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Date Picker -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tanggal Pengambilan <span class="text-red-500">*</span>
              </label>
              <DatePicker
                class="custom-datepicker"
                v-model="selectedDate"
                placeholder="Pilih tanggal pengambilan"
                @change="handleDateChange"
                @click.stop
              />
            </div>
            <!-- Time Picker -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Waktu Pengambilan <span class="text-red-500">*</span>
              </label>
              <TimePicker
                class="custom-timepicker"
                v-model="selectedTime"
                placeholder="Pilih waktu pengambilan"
                :use12-hour="false"
                :options="timeOptions"
                :allowCustom="false"
                @change="handleTimeChange"
                @click.stop
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Option 2: Ambil Secara Online -->
      <div class="pickup-option" :class="{ 'selected': selectedType === 'Ambil secara online' }"
        @click="selectPickupType('Ambil secara online')">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-lg mb-2">Ambil Secara Online</h3>
            <p class="text-sm text-gray-600">
              Pesanan akan diambil menggunakan layanan GoSend/GrabSend yang dipesan oleh wali murid. Biaya pengiriman
              mengikuti tarif layanan masing-masing dan dibayar terpisah.
            </p>
          </div>
          <div class="ml-4">
            <div class="radio-button" :class="{ 'checked': selectedType === 'Ambil secara online' }">
              <div v-if="selectedType === 'Ambil secara online'" class="radio-dot"></div>
            </div>
          </div>
        </div>

        <!-- Delivery Date & Time Selection (shown when Ambil secara online is selected) -->
        <div v-if="selectedType === 'Ambil secara online'" class="mt-4 pt-4 border-t border-gray-200">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Date Picker -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tanggal Pengiriman <span class="text-red-500">*</span>
              </label>
              <DatePicker
                class="custom-datepicker"
                v-model="selectedDate"
                placeholder="Pilih tanggal pengiriman"
                @change="handleDateChange"
                @click.stop
              />
            </div>
            <!-- Time Picker -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Waktu Pengiriman <span class="text-red-500">*</span>
              </label>
              <TimePicker
                class="custom-timepicker"
                v-model="selectedTime"
                placeholder="Pilih waktu pengiriman"
                :use12-hour="false"
                :options="timeOptions"
                :allowCustom="false"
                @change="handleTimeChange"
                @click.stop
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { DatePicker, TimePicker } from 'frappe-ui'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'
import { getPickupTimeSettings, type PickupTimeSettings } from '@/utils/timeSettingsApi'
import { useAlertStore } from '@/stores/alert'
import { debounce } from 'frappe-ui'

const checkoutStore = useCheckoutStore()
const { pickupType, deliveryDate, deliveryTime } = storeToRefs(checkoutStore)

const selectedType = ref<string>(pickupType.value || '')
const isLoading = ref<boolean>(true)
const selectedDate = ref<string>(deliveryDate.value || '')
const selectedTime = ref<string>(deliveryTime.value || '')
const timeSettings = ref<PickupTimeSettings | null>(null)

// Minimum date based on configured minimum_days_ahead
const minDate = computed(() => {
  const daysAhead = timeSettings.value?.minimum_days_ahead || 1
  const minDate = new Date()
  minDate.setDate(minDate.getDate() + daysAhead)
  return minDate.toISOString().slice(0, 10) // Format: YYYY-MM-DD
})

// Helper function to check if a date is disabled
const isDateDisabled = (dateStr: string): boolean => {
  if (!timeSettings.value) return false
  
  // Check if date is before minimum date (string comparison is safe for YYYY-MM-DD format)
  if (dateStr < minDate.value) {
    return true
  }
  
  const date = new Date(dateStr)
  
  // Check if weekdays only is enabled and date is weekend
  if (timeSettings.value.weekdays_only) {
    const dayOfWeek = date.getDay()
    // 0 = Sunday, 6 = Saturday
    if (dayOfWeek === 0 || dayOfWeek === 6) {
      return true
    }
  }
  
  // Check if date falls within any disabled range
  if (timeSettings.value.disabled_date_ranges) {
    for (const range of timeSettings.value.disabled_date_ranges) {
      if (!range.from_date || !range.to_date) continue
      
      // Use string comparison for YYYY-MM-DD format
      if (dateStr >= range.from_date && dateStr <= range.to_date) {
        return true
      }
    }
  }
  
  return false
}

// Available time slots: 09:00-12:00 and 13:00-16:00 with configurable intervals
const timeOptions = computed(() => {
  if (!timeSettings.value) {
    return []
  }
  const options = []
  
  // Use time settings from backend or fallback to defaults
  const settings = timeSettings.value
  console.log("timeSettings", settings)
  
  // Helper function to convert HH:MM to minutes
  const timeToMinutes = (time: string): number => {
    const parts = time.split(':').map(Number)
    const hours = parts[0] ?? 0
    const minutes = parts[1] ?? 0
    return hours * 60 + minutes
  }
  
  // Helper function to convert minutes to HH:MM
  const minutesToTime = (minutes: number): string => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`
  }
  
  const morningStart = timeToMinutes(settings.morning_start)
  const morningEnd = timeToMinutes(settings.morning_end)
  const afternoonStart = timeToMinutes(settings.afternoon_start)
  const afternoonEnd = timeToMinutes(settings.afternoon_end)
  const interval = settings.interval
  
  // Generate morning slots
  for (let m = morningStart; m <= morningEnd; m += interval) {
    if (m > morningEnd) break
    options.push({ value: minutesToTime(m) })
  }
  
  // Generate afternoon slots
  for (let m = afternoonStart; m <= afternoonEnd; m += interval) {
    if (m > afternoonEnd) break
    options.push({ value: minutesToTime(m) })
  }
  
  return options
})

// Initialize with default date and time based on settings
onMounted(async () => {
  // Fetch time settings from backend
  try {
    timeSettings.value = await getPickupTimeSettings()
  } catch (error) {
    useAlertStore().error('Gagal memuat pengaturan waktu pengambilan')
  } finally {
    isLoading.value = false
  }
  
  if (!selectedDate.value && timeSettings.value) {
    // Set default to minimum days ahead
    const daysAhead = timeSettings.value.minimum_days_ahead || 1
    let defaultDate = new Date()
    defaultDate.setDate(defaultDate.getDate() + daysAhead)
    
    // Skip disabled dates to find the first available date
    let attempts = 0
    const maxAttempts = 90 // Look ahead up to 90 days
    while (isDateDisabled(defaultDate.toISOString().slice(0, 10)) && attempts < maxAttempts) {
      defaultDate.setDate(defaultDate.getDate() + 1)
      attempts++
    }
    
    selectedDate.value = defaultDate.toISOString().slice(0, 10)
  }

  if (!selectedTime.value) {
    // Set default time to 10:00
    selectedTime.value = "10:00"
  }
})

// Watch for changes from store
watch(pickupType, (newVal) => {
  selectedType.value = newVal || ''
})

watch(deliveryDate, (newVal) => {
  selectedDate.value = newVal || ''
})

watch(deliveryTime, (newVal) => {
  selectedTime.value = newVal || ''
})

// Watch for type changes and set defaults
watch(selectedType, (newType) => {
  if (newType) {
    // Set defaults if missing
    if (!selectedDate.value) {
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      selectedDate.value = tomorrow.toISOString().slice(0, 10)
    }
    if (!selectedTime.value) {
      selectedTime.value = "10:00"
    }

    // Update store immediately when type changes
    checkoutStore.setPickupType(newType, selectedDate.value, selectedTime.value)
  }
})

function selectPickupType(type: string) {
  selectedType.value = type
}

// Debounced function to update store - prevents rapid API calls and database conflicts
const debouncedStoreUpdate = debounce((type: string, date: string, time: string) => {
  checkoutStore.setPickupType(type, date, time)
}, 500)

// Handle date change with validation
function handleDateChange(newDate: string) {
  if (!newDate) return
  
  // Check if selected date is disabled
  if (isDateDisabled(newDate)) {
    useAlertStore().error('Tanggal yang dipilih tidak tersedia.')
    
    // Find the next available date
    let nextDate = new Date(newDate)
    nextDate.setDate(nextDate.getDate() + 1) // Start from the next day
    let attempts = 0
    const maxAttempts = 90
    
    while (isDateDisabled(nextDate.toISOString().slice(0, 10)) && attempts < maxAttempts) {
      nextDate.setDate(nextDate.getDate() + 1)
      attempts++
    }
    
    if (attempts < maxAttempts) {
      // Set to the next available date
      setTimeout(() => {
        selectedDate.value = nextDate.toISOString().slice(0, 10)
      }, 100)
    } else {
      // Fallback to minimum date if no available date found
      setTimeout(() => {
        selectedDate.value = minDate.value
      }, 100)
      useAlertStore().error('Tidak ada tanggal tersedia dalam 90 hari ke depan')
    }
    return
  }
  
  // Date is valid, update the store with debounce
  if (selectedType.value && selectedTime.value) {
    debouncedStoreUpdate(selectedType.value, newDate, selectedTime.value)
  }
}

// Handle time change
function handleTimeChange(newTime: string) {
  if (selectedType.value && selectedDate.value && newTime) {
    debouncedStoreUpdate(selectedType.value, selectedDate.value, newTime)
  }
}

// Watch for date/time changes - no API calls here, only done via change handlers
watch([selectedDate, selectedTime], ([newDate, newTime]) => {
  // Just ensure we have valid values, no store updates
  // The change handlers will update the store with debouncing
})


defineExpose({
  selectedType,
  selectedDate,
  selectedTime
})
</script>

<style scoped>
.pickup-option {
  @apply border-2 border-gray-200 rounded-lg p-6 cursor-pointer transition-all duration-200;
}

.pickup-option:hover {
  @apply border-primary;
}

.pickup-option.selected {
  @apply border-primary bg-purple-50;
}

.radio-button {
  @apply w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center;
}

.radio-button.checked {
  @apply border-primary;
}

.radio-dot {
  @apply w-3 h-3 rounded-full bg-primary;
}
</style>
