<template>
  <div class="pickup-type-selector">
    <div class="space-y-4">
      <!-- Option 1: Ambil Di Koperasi -->
      <div
        class="pickup-option"
        :class="{ 'selected': selectedType === 'Ambil di koperasi' }"
        @click="selectPickupType('Ambil di koperasi')"
      >
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
            <!-- Date Time Picker -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tanggal & Waktu Pengambilan <span class="text-red-500">*</span>
              </label>
              <input
                v-model="selectedDateTime"
                type="datetime-local"
                :min="minDateTime"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                @click.stop
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Option 2: Ambil Secara Online -->
      <div
        class="pickup-option"
        :class="{ 'selected': selectedType === 'Ambil secara online' }"
        @click="selectPickupType('Ambil secara online')"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="font-semibold text-lg mb-2">Ambil Secara Online</h3>
            <p class="text-sm text-gray-600">
              Bintaro Permai, Bintaro Jaya Sektor 11, Sektor 12 (Melati, Anggrek), dan sekitarnya
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
            <!-- Date Time Picker -->
            <div class="md:col-span-2">
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Tanggal & Waktu Pengiriman <span class="text-red-500">*</span>
              </label>
              <input
                v-model="selectedDateTime"
                type="datetime-local"
                :min="minDateTime"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
                @click.stop
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'

const checkoutStore = useCheckoutStore()
const { pickupType, deliveryDate } = storeToRefs(checkoutStore)

const selectedType = ref<string>(pickupType.value || '')
const selectedDateTime = ref<string>(deliveryDate.value || '')

// Minimum date is tomorrow (+1 day) at 10:00 AM
const minDateTime = computed(() => {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(10, 0, 0, 0) // 10:00 AM
  return tomorrow.toISOString().slice(0, 16) // Format for datetime-local input
})

// Initialize with default date (tomorrow) and time (10:00)
onMounted(() => {
  if (!selectedDateTime.value) {
    // Set default to tomorrow at 10:00 AM
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(10, 0, 0, 0) // 10:00 AM
    selectedDateTime.value = tomorrow.toISOString().slice(0, 16) // Format for datetime-local input
  }
})

// Watch for changes from store
watch(pickupType, (newVal) => {
  selectedType.value = newVal || ''
})

watch(deliveryDate, (newVal) => {
  selectedDateTime.value = newVal || ''
})

// Watch for type changes and set defaults
watch(selectedType, (newType) => {
  if (newType && !selectedDateTime.value) {
    // Set default to tomorrow at 10:00 AM
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(10, 0, 0, 0) // 10:00 AM
    selectedDateTime.value = tomorrow.toISOString().slice(0, 16) // Format for datetime-local input
  }
  // Update store immediately when type changes
  if (newType) {
    checkoutStore.pickupType = newType
  }
})


function selectPickupType(type: string) {
  selectedType.value = type
  // Set default date and time if not already set
  if (!selectedDateTime.value) {
    // Set default to tomorrow at 10:00 AM
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(10, 0, 0, 0) // 10:00 AM
    selectedDateTime.value = tomorrow.toISOString().slice(0, 16) // Format for datetime-local input
  }
}

// Watch for local changes and sync to store
watch(selectedDateTime, (newVal) => {
  if (newVal) {
    checkoutStore.deliveryDate = newVal
  }
}, { immediate: true })

defineExpose({
  selectedType,
  selectedDateTime
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
