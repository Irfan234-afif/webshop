<template>
  <div class="space-y-6">
    <!-- Loading state -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <p class="text-red-700">{{ error }}</p>
    </div>

    <!-- Reason selection -->
    <div v-else class="space-y-4">
      <div
        v-for="reason in returnReasons"
        :key="reason.name"
        @click="selectReason(reason.name)"
        class="bg-white border-2 rounded-xl p-4 cursor-pointer transition-all hover:shadow-md"
        :class="{
          'border-primary bg-primary/5': selectedReason === reason.name,
          'border-gray-200': selectedReason !== reason.name
        }"
      >
        <div class="flex items-center">
          <div class="flex-1">
            <h3 class="font-semibold text-gray-900">{{ reason.reason_name }}</h3>
            <p v-if="reason.description" class="text-sm text-gray-500 mt-1">
              {{ reason.description }}
            </p>
          </div>
          <div class="ml-4">
            <div 
              class="w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all"
              :class="{
                'border-primary bg-primary': selectedReason === reason.name,
                'border-gray-300': selectedReason !== reason.name
              }"
            >
              <div 
                v-if="selectedReason === reason.name"
                class="w-2 h-2 bg-white rounded-full"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Other reason textarea -->
      <div 
        v-if="isOtherReasonSelected" 
        class="bg-gray-50 border border-gray-200 rounded-xl p-4"
      >
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Jelaskan alasan pengembalian Anda
        </label>
        <textarea
          v-model="otherReasonText"
          rows="4"
          class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
          placeholder="Mohon jelaskan alasan Anda ingin mengembalikan barang ini..."
          :class="{ 'border-red-500': otherReasonError }"
        ></textarea>
        <p v-if="otherReasonError" class="text-sm text-red-600 mt-1">
          {{ otherReasonError }}
        </p>
      </div>

      <!-- Validation error -->
      <div v-if="validationError" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p class="text-yellow-800">{{ validationError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useReturnsStore } from '@/stores/returns'
import type { ReturnReason } from '@/types/returns'

interface Emits {
  (e: 'update:selectedReason', value: string): void
  (e: 'update:otherReason', value: string): void
  (e: 'update:isValid', value: boolean): void
}

const emit = defineEmits<Emits>()

const returnsStore = useReturnsStore()

const selectedReason = ref('')
const otherReasonText = ref('')
const validationError = ref('')
const otherReasonError = ref('')

const isLoading = computed(() => returnsStore.isLoading)
const error = computed(() => returnsStore.error)
const returnReasons = computed(() => returnsStore.returnReasons)

const isOtherReasonSelected = computed(() => {
  const selectedReasonObj = returnReasons.value.find(r => r.name === selectedReason.value)
  return selectedReasonObj?.reason_name === 'Other' || selectedReasonObj?.reason_name === 'Alasan Lainnya'
})

const isValid = computed(() => {
  if (!selectedReason.value) {
    return false
  }

  if (isOtherReasonSelected.value && !otherReasonText.value.trim()) {
    return false
  }

  return true
})

watch(selectedReason, () => {
  validationError.value = ''
  emit('update:selectedReason', selectedReason.value)
  validateForm()
})

watch(otherReasonText, () => {
  otherReasonError.value = ''
  emit('update:otherReason', otherReasonText.value)
  validateForm()
})

watch(isValid, (newVal) => {
  emit('update:isValid', newVal)
})

onMounted(async () => {
  await loadReturnReasons()
})

async function loadReturnReasons() {
  try {
    await returnsStore.fetchReturnReasons()
  } catch (err) {
    console.error('Error loading return reasons:', err)
  }
}

function selectReason(reasonId: string) {
  selectedReason.value = reasonId
  
  // Clear other reason text if switching away from "Other"
  if (!isOtherReasonSelected.value) {
    otherReasonText.value = ''
  }
}

function validateForm() {
  validationError.value = ''
  otherReasonError.value = ''

  if (!selectedReason.value) {
    validationError.value = 'Silakan pilih alasan pengembalian'
    return false
  }

  if (isOtherReasonSelected.value && !otherReasonText.value.trim()) {
    otherReasonError.value = 'Mohon isi alasan pengembalian'
    return false
  }

  return true
}

// Expose validation method for parent component
defineExpose({
  validateForm
})
</script>
