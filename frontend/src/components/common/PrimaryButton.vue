<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'success'
  size?: 'small' | 'medium' | 'large'
  icon?: string
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false,
  type: 'button'
})

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center gap-3 font-bold rounded-md transition-all duration-300 cursor-pointer'

  const variants = {
    primary: 'bg-secondary-alt text-white hover:opacity-90',
    secondary: 'bg-primary text-white hover:opacity-90',
    outline: 'border-2 border-primary text-primary hover:bg-white hover:text-primary',
    success: 'bg-success text-white hover:opacity-90',
  }

  const sizes = {
    small: 'px-6 py-2 text-sm',
    medium: 'px-8 py-4 text-base',
    large: 'px-10 py-5 text-lg'
  }

  const disabled = props.disabled ? 'opacity-50 cursor-not-allowed' : ''

  return `${base} ${variants[props.variant]} ${sizes[props.size]} ${disabled}`
})
</script>

<template>
  <button :class="buttonClasses" :disabled="disabled" :type="type">
    <slot />
    <span v-if="icon" class="w-5 h-5">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14.43 5.93L20.5 12L14.43 18.07" stroke="currentColor" stroke-width="2" stroke-linecap="round"
          stroke-linejoin="round" />
        <path d="M4 12H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </span>
  </button>
</template>
