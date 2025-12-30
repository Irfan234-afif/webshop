<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: number
  min?: number
  max?: number
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  min: 1,
  disabled: false
})

const emit = defineEmits<{
  'update:modelValue': [value: number]
}>()

// Computed properties for button states
const canDecrement = computed(() => !props.disabled && props.modelValue > props.min)
const canIncrement = computed(() => !props.disabled && (!props.max || props.modelValue < props.max))

// Handlers
const handleDecrement = () => {
  if (canDecrement.value) {
    emit('update:modelValue', props.modelValue - 1)
  }
}

const handleIncrement = () => {
  if (canIncrement.value) {
    emit('update:modelValue', props.modelValue + 1)
  }
}

const handleInput = (event: Event) => {
  const input = event.target as HTMLInputElement
  const value = parseInt(input.value, 10)

  if (isNaN(value) || value < props.min) {
    emit('update:modelValue', props.min)
  } else if (props.max && value > props.max) {
    emit('update:modelValue', props.max)
  } else {
    emit('update:modelValue', value)
  }
}

const handleBlur = (event: Event) => {
  const input = event.target as HTMLInputElement
  const value = parseInt(input.value, 10)

  // Validate on blur - ensure value is within bounds
  if (isNaN(value) || value < props.min) {
    emit('update:modelValue', props.min)
  } else if (props.max && value > props.max) {
    emit('update:modelValue', props.max)
  }
}
</script>

<template>
  <div class="flex items-center gap-3">
    <!-- Decrement Button -->
    <button
      type="button"
      class="flex h-12 w-12 items-center justify-center rounded-lg border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
      :disabled="!canDecrement"
      @click="handleDecrement"
      aria-label="Decrease quantity"
    >
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
      </svg>
    </button>

    <!-- Quantity Input -->
    <input
      type="number"
      :value="modelValue"
      :min="min"
      :max="max"
      :disabled="disabled"
      class="h-12 w-16 rounded-lg border border-gray-300 bg-white text-center text-base font-semibold text-gray-900 focus:border-secondary-alt focus:outline-none focus:ring-2 focus:ring-secondary-alt focus:ring-opacity-20 disabled:cursor-not-allowed disabled:opacity-50"
      @input="handleInput"
      @blur="handleBlur"
      aria-label="Quantity"
    />

    <!-- Increment Button -->
    <button
      type="button"
      class="flex h-12 w-12 items-center justify-center rounded-lg border border-gray-300 bg-white text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
      :disabled="!canIncrement"
      @click="handleIncrement"
      aria-label="Increase quantity"
    >
      <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
      </svg>
    </button>
  </div>
</template>
