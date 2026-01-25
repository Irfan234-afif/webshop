<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import type { Student } from '@/types/cart'
import FormSelect, { type SelectOption } from '@/components/common/FormSelect.vue'

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

// Computed options for the select component
const studentOptions = computed<SelectOption[]>(() => {
  return cartStore.students.map(student => ({
    value: student.name,
    label: student.student_name,
    description: student.school_unit, // Show school unit in the detailed view
    ...student // Spread original student data so we can emit it back
  }))
})

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

const handleUpdateValue = (value: string | number | null) => {
  emit('update:modelValue', value as string | null)
}

const handleSelect = (option: SelectOption) => {
  // Reconstruct student object or just use the extra props we spread into the option
  // Since we spread ...student into the option, we can cast it back to Student (mostly)
  // or retrieve it from the store if we want to be strictly type safe with references
  const student = cartStore.students.find(s => s.name === option.value)
  if (student) {
    emit('select', student)
  }
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Using the new reusable FormSelect component -->
    <FormSelect :model-value="modelValue" :options="studentOptions" :label="label" :required="required"
      :disabled="disabled" :loading="isLoading" :error="error" placeholder="Pilih siswa..." option-template="detailed"
      searchable @update:model-value="handleUpdateValue" @select="handleSelect" />

    <!-- Active Student Indicator -->
    <p v-if="modelValue && modelValue === cartStore.activeStudent" class="text-xs text-green-600 mt-1">
      ✓ Siswa aktif saat ini
    </p>
  </div>
</template>
