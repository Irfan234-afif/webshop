<script setup lang="ts">
import { ref, computed } from 'vue'

const emit = defineEmits(['select-date'])

const selectedDate = ref<string>('')

// Get today's date in YYYY-MM-DD format for min attribute
const today = computed(() => {
  const date = new Date()
  return date.toISOString().split('T')[0]
})

// Format date for display (e.g., "25 Desember 2025")
const formattedDate = computed(() => {
  if (!selectedDate.value) return ''
  
  const date = new Date(selectedDate.value + 'T00:00:00')
  const months = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
  ]
  
  const day = date.getDate()
  const month = months[date.getMonth()]
  const year = date.getFullYear()
  
  return `${day} ${month} ${year}`
})

const handleDateChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  selectedDate.value = target.value
  emit('select-date', target.value)
}
</script>

<template>
  <div class="mb-6">
    <h3 class="mb-4 text-sm font-semibold text-gray-900">Pilih Tanggal Layanan</h3>
    
    <div class="relative date-picker-wrapper">
      <!-- Custom styled display (visual only) -->
      <div
        class="flex w-full items-center justify-between gap-3 rounded-lg border-2 px-4 py-3 text-left transition-all pointer-events-none"
        :class="[
          selectedDate
            ? 'border-secondary bg-secondary-surface text-secondary-alt'
            : 'border-gray-200 bg-white text-gray-500'
        ]"
      >
        <div class="flex items-center gap-3">
          <!-- Calendar Icon -->
          <svg 
            class="h-5 w-5 flex-shrink-0" 
            :class="selectedDate ? 'text-secondary-alt' : 'text-gray-400'"
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" 
            />
          </svg>
          
          <!-- Date Text -->
          <span class="text-sm font-semibold">
            {{ selectedDate ? formattedDate : 'Pilih tanggal layanan' }}
          </span>
        </div>
        
        <!-- Chevron Icon -->
        <svg 
          class="h-5 w-5 flex-shrink-0 transition-transform" 
          :class="selectedDate ? 'text-secondary-alt' : 'text-gray-400'"
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M19 9l-7 7-7-7" 
          />
        </svg>
      </div>
      
      <!-- Actual date input overlaid on top -->
      <input
        id="service-date-input"
        type="date"
        :value="selectedDate"
        :min="today"
        @change="handleDateChange"
        class="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
    </div>
    
    <!-- Helper Text -->
    <p v-if="!selectedDate" class="mt-2 text-xs text-gray-500">
      Silakan pilih tanggal untuk memulai layanan
    </p>
    <p v-else class="mt-2 text-xs text-secondary-alt font-medium">
      ✓ Tanggal layanan telah dipilih
    </p>
  </div>
</template>

<style scoped>
.date-picker-wrapper {
  position: relative;
}

/* Ensure the date input is clickable and covers the entire area */
#service-date-input {
  z-index: 10;
}

/* Remove default date input styling */
#service-date-input::-webkit-calendar-picker-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: auto;
  height: auto;
  color: transparent;
  background: transparent;
  cursor: pointer;
}

/* Firefox */
#service-date-input::-moz-calendar-picker-indicator {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: auto;
  height: auto;
  color: transparent;
  background: transparent;
  cursor: pointer;
}
</style>
