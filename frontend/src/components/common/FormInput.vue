<script setup lang="ts">
import { computed } from 'vue'

interface Props {
    modelValue: string
    type?: 'text' | 'tel' | 'email' | 'password' | 'date'
    placeholder?: string
    disabled?: boolean
    readonly?: boolean
    icon?: boolean
    required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    type: 'text',
    disabled: false,
    readonly: false,
    icon: false
})

const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void
}>()

const inputClasses = computed(() => {
    const base = 'w-full px-4 py-3 border rounded-lg text-sm text-gray-900 transition-all'

    const stateClasses = props.readonly || props.disabled
        ? 'bg-gray-100 border-gray-200 text-gray-500 cursor-not-allowed'
        : 'bg-gray-50 border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition'

    return `${base} ${stateClasses}`
})

const handleInput = (event: Event) => {
    const target = event.target as HTMLInputElement
    emit('update:modelValue', target.value)
}
</script>

<template>
    <input :type="type" :value="modelValue" :placeholder="placeholder" :disabled="disabled" :readonly="readonly"
        :class="inputClasses" @input="handleInput" />
</template>
