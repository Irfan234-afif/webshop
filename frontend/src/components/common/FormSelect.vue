<script setup lang="ts">
import { computed } from 'vue'

interface SelectOption {
    value: string
    label: string
}

interface Props {
    modelValue: string
    placeholder?: string
    disabled?: boolean
    required?: boolean
}

const props = withDefaults(defineProps<Props>(), {
    disabled: false,
    required: false
})

const emit = defineEmits<{
    (e: 'update:modelValue', value: string): void
}>()

const selectClasses = computed(() => {
    const base = 'w-full px-4 py-3 border rounded-lg text-sm text-gray-900 transition-all'

    const stateClasses = props.disabled
        ? 'bg-gray-50 border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition opacity-50 cursor-not-allowed'
        : 'bg-gray-50 border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition'

    return `${base} ${stateClasses}`
})

const handleChange = (event: Event) => {
    const target = event.target as HTMLSelectElement
    emit('update:modelValue', target.value)
}
</script>

<template>
    <select :value="modelValue" :disabled="disabled" :required="required" :class="selectClasses" @change="handleChange">
        <slot />
    </select>
</template>
