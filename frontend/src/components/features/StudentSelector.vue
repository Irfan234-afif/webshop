<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import type { Student } from '@/types/cart'

interface Props {
  required?: boolean
  label?: string
  disabled?: boolean
  modelValue?: string | null
}

const props = withDefaults(defineProps<Props>(), {
  required: false,
  label: 'Pilih Siswa',
  disabled: false,
  modelValue: null
})

const emit = defineEmits<{
  'update:modelValue': [studentName: string | null]
  select: [student: Student]
}>()

const cartStore = useCartStore()
const isLoading = ref(false)
const error = ref<string | null>(null)

// Fetch students on mount
onMounted(async () => {
  if (cartStore.students.length === 0) {
    isLoading.value = true
    error.value = null
    try {
      await cartStore.fetchStudents()
    } catch (e) {
      error.value = 'Gagal memuat data siswa'
      console.error('Failed to fetch students:', e)
    } finally {
      isLoading.value = false
    }
  }
})

const handleSelectStudent = (student: Student) => {
  emit('update:modelValue', student.name)
  emit('select', student)
}

const selectedStudent = ref<Student | null>(null)
const isOpen = ref(false)

const selectStudent = (student: Student) => {
  selectedStudent.value = student
  isOpen.value = false
  handleSelectStudent(student)
}

const toggleDropdown = () => {
  if (!props.disabled && !isLoading.value) {
    isOpen.value = !isOpen.value
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Label -->
    <label class="text-sm font-semibold text-gray-900">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Loading State -->
    <div v-if="isLoading" class="rounded-lg border-2 border-gray-300 bg-gray-50 px-4 py-2.5 text-sm text-gray-500">
      Memuat data siswa...
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="rounded-lg border-2 border-red-300 bg-red-50 px-4 py-2.5 text-sm text-red-600">
      {{ error }}
    </div>

    <!-- Dropdown Selector -->
    <div v-else class="relative">
      <button
        type="button"
        :disabled="disabled"
        :class="[
          'w-full rounded-lg border-2 px-4 py-2.5 text-left text-sm font-medium transition-all',
          selectedStudent
            ? 'border-primary bg-white text-gray-900'
            : 'border-gray-300 bg-white text-gray-500',
          disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:border-gray-400',
          isOpen ? 'border-primary' : ''
        ]"
        @click="toggleDropdown"
        :aria-expanded="isOpen"
      >
        <span v-if="selectedStudent">{{ selectedStudent.student_name }}</span>
        <span v-else>Pilih siswa...</span>

        <!-- Dropdown Arrow -->
        <svg
          :class="[
            'absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 transition-transform',
            isOpen ? 'rotate-180' : ''
          ]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- Dropdown List -->
      <div
        v-if="isOpen"
        class="absolute z-10 mt-2 w-full rounded-lg border border-gray-200 bg-white shadow-lg"
      >
        <div v-if="cartStore.students.length === 0" class="px-4 py-3 text-sm text-gray-500">
          Tidak ada data siswa
        </div>

        <button
          v-for="student in cartStore.students"
          :key="student.name"
          type="button"
          :class="[
            'w-full px-4 py-3 text-left text-sm transition-colors hover:bg-gray-50',
            selectedStudent?.name === student.name ? 'bg-primary/10 text-primary' : 'text-gray-900'
          ]"
          @click="selectStudent(student)"
        >
          <div class="font-medium">{{ student.student_name }}</div>
          <div class="text-xs text-gray-500">{{ student.school_unit }}</div>
        </button>
      </div>
    </div>

    <!-- Required Validation Message -->
    <p v-if="required && !selectedStudent && !disabled && !isLoading" class="text-xs text-gray-500">
      Silakan pilih siswa terlebih dahulu
    </p>

    <!-- Active Student Indicator -->
    <p v-if="selectedStudent && selectedStudent.name === cartStore.activeStudent" class="text-xs text-green-600">
      ✓ Siswa aktif saat ini
    </p>
  </div>
</template>
