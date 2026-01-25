<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

export interface SelectOption {
    value: string | number
    label: string
    description?: string
    disabled?: boolean
    [key: string]: any // Allow additional custom properties
}

interface Props {
    modelValue: string | number | null
    options: SelectOption[] | [] | any
    label?: string
    placeholder?: string
    disabled?: boolean
    required?: boolean
    loading?: boolean
    error?: string | null
    searchable?: boolean
    clearable?: boolean
    optionLabel?: string
    optionValue?: string
    optionTemplate?: 'default' | 'detailed' // detailed shows description
}

const props = withDefaults(defineProps<Props>(), {
    placeholder: 'Pilih opsi...',
    disabled: false,
    required: false,
    loading: false,
    error: null,
    searchable: false, // Default false to match simple select behavior unless more power is needed
    clearable: false,
    optionTemplate: 'default',
    optionLabel: 'label',
    optionValue: 'value'
})

const emit = defineEmits<{
    'update:modelValue': [value: string | number | null]
    select: [option: SelectOption]
    clear: []
    focus: []
    blur: []
}>()

// Refs
const isOpen = ref(false)
const searchQuery = ref('')
const dropdownRef = ref<HTMLDivElement | null>(null)
const buttonRef = ref<HTMLButtonElement | null>(null)
const searchInputRef = ref<HTMLInputElement | null>(null)
const highlightedIndex = ref(-1)

// Computed
const selectedOption = computed(() => {
    return props.options.find(opt => opt[props.optionValue] === props.modelValue) || null
})

const filteredOptions = computed(() => {
    if (!props.searchable || !searchQuery.value) {
        return props.options
    }

    const query = searchQuery.value.toLowerCase()
    return props.options.filter(option =>
        option[props.optionLabel].toLowerCase().includes(query) ||
        option.description?.toLowerCase().includes(query)
    )
})

const inputClasses = computed(() => {
    const base = 'w-full px-4 py-3 pr-10 border rounded-lg text-sm text-left transition-all cursor-pointer'

    let stateClasses = ''

    if (props.disabled || props.loading) {
        stateClasses = 'bg-gray-100 border-gray-200 text-gray-500 cursor-not-allowed'
    } else if (props.error) {
        stateClasses = 'bg-white border-red-300 text-gray-900 hover:border-red-400 focus:ring-2 focus:ring-red-500 focus:border-transparent'
    } else if (isOpen.value) {
        stateClasses = 'bg-white border-primary text-gray-900 focus:ring-2 focus:ring-primary focus:border-transparent'
    } else if (selectedOption.value) {
        stateClasses = 'bg-white border-gray-300 text-gray-900 hover:border-gray-400 focus:ring-2 focus:ring-primary focus:border-transparent'
    } else {
        // Default state similar to FormInput
        stateClasses = 'bg-gray-50 border-gray-200 text-gray-500 hover:border-gray-300 focus:ring-2 focus:ring-primary focus:border-transparent'
    }

    return `${base} ${stateClasses} outline-none`
})

// Methods
const toggleDropdown = () => {
    if (props.disabled || props.loading) return

    if (isOpen.value) {
        closeDropdown()
    } else {
        openDropdown()
    }
}

const openDropdown = () => {
    isOpen.value = true
    highlightedIndex.value = -1
    searchQuery.value = ''
    emit('focus')

    // Auto-focus search input if searchable
    if (props.searchable) {
        nextTick(() => {
            searchInputRef.value?.focus()
        })
    }
}

const closeDropdown = () => {
    isOpen.value = false
    searchQuery.value = ''
    emit('blur')
}

const selectOption = (option: SelectOption) => {
    if (option.disabled) return

    emit('update:modelValue', option[props.optionValue])
    emit('select', option)
    closeDropdown()

    // Return focus to button
    buttonRef.value?.focus()
}

const clearSelection = (event: Event) => {
    event.stopPropagation()
    emit('update:modelValue', null)
    emit('clear')
}

const handleClickOutside = (event: MouseEvent) => {
    if (
        dropdownRef.value &&
        !dropdownRef.value.contains(event.target as Node) &&
        buttonRef.value &&
        !buttonRef.value.contains(event.target as Node)
    ) {
        closeDropdown()
    }
}

const handleKeydown = (event: KeyboardEvent) => {
    if (!isOpen.value) {
        // Open dropdown on Enter, Space, or Arrow Down
        if (['Enter', ' ', 'ArrowDown'].includes(event.key)) {
            event.preventDefault()
            openDropdown()
        }
        return
    }

    const options = filteredOptions.value.filter(opt => !opt.disabled)

    switch (event.key) {
        case 'Escape':
            event.preventDefault()
            closeDropdown()
            buttonRef.value?.focus()
            break

        case 'ArrowDown':
            event.preventDefault()
            if (highlightedIndex.value < options.length - 1) {
                highlightedIndex.value++
            } else {
                highlightedIndex.value = 0
            }
            scrollToHighlighted()
            break

        case 'ArrowUp':
            event.preventDefault()
            if (highlightedIndex.value > 0) {
                highlightedIndex.value--
            } else {
                highlightedIndex.value = options.length - 1
            }
            scrollToHighlighted()
            break

        case 'Enter':
        case ' ':
            // Allow space to select only if not searching (since space is needed for typing)
            if (event.key === ' ' && props.searchable && searchQuery.value.length > 0) {
                return;
            }
            event.preventDefault()
            if (highlightedIndex.value >= 0 && options[highlightedIndex.value]) {
                selectOption(options[highlightedIndex.value])
            }
            break

        case 'Home':
            event.preventDefault()
            highlightedIndex.value = 0
            scrollToHighlighted()
            break

        case 'End':
            event.preventDefault()
            highlightedIndex.value = options.length - 1
            scrollToHighlighted()
            break
    }
}

const scrollToHighlighted = () => {
    nextTick(() => {
        const listElement = dropdownRef.value?.querySelector('.overflow-y-auto');
        const optionElements = listElement?.querySelectorAll('[role="option"]')
        if (listElement && optionElements && highlightedIndex.value >= 0) {
            const element = optionElements[highlightedIndex.value] as HTMLElement
            // Simple scroll into view logic
            const elementTop = element.offsetTop
            const elementBottom = elementTop + element.offsetHeight
            const listTop = listElement.scrollTop
            const listBottom = listTop + listElement.clientHeight

            if (elementBottom > listBottom) {
                listElement.scrollTop = elementBottom - listElement.clientHeight
            } else if (elementTop < listTop) {
                listElement.scrollTop = elementTop
            }
        }
    })
}

// Lifecycle
onMounted(() => {
    document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutside)
})

// Watch for options change to reset highlighted index
watch(() => props.options, () => {
    highlightedIndex.value = -1
})
</script>

<template>
    <div class="flex flex-col gap-2">
        <!-- Label (Optional, matches FormInput structure used in other places or StudentSelector) -->
        <label v-if="label" class="text-sm font-semibold text-gray-900">
            {{ label }}
            <span v-if="required" class="text-red-500">*</span>
        </label>

        <div class="relative w-full">
            <!-- Main Select Button -->
            <button ref="buttonRef" type="button" :disabled="disabled || loading" :class="inputClasses"
                :aria-expanded="isOpen" :aria-haspopup="true" :aria-required="required" @click="toggleDropdown"
                @keydown="handleKeydown">
                <!-- Selected Value or Placeholder -->
                <span v-if="loading" class="text-gray-500">Memuat...</span>
                <span v-else-if="selectedOption" class="text-gray-900 font-medium truncate block">
                    {{ selectedOption[props.optionLabel] }}
                </span>
                <span v-else class="text-gray-500">{{ placeholder }}</span>

                <!-- Icons Container -->
                <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <!-- Clear Button -->
                    <button v-if="clearable && selectedOption && !disabled && !loading" type="button"
                        class="p-1 hover:bg-gray-200 rounded-full transition-colors z-10" @click="clearSelection"
                        @mousedown.stop title="Clear selection">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                            class="text-gray-400">
                            <path d="M18 6 6 18" />
                            <path d="m6 6 12 12" />
                        </svg>
                    </button>

                    <!-- Loading Spinner -->
                    <svg v-if="loading" class="animate-spin h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg"
                        fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                    </svg>

                    <!-- Dropdown Arrow -->
                    <svg v-else :class="[
                        'h-5 w-5 transition-transform duration-200',
                        isOpen ? 'rotate-180 text-primary' : 'text-gray-400'
                    ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                </div>
            </button>

            <!-- Dropdown Menu -->
            <Transition enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95" enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75" leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95">
                <div v-if="isOpen" ref="dropdownRef"
                    class="absolute z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white shadow-xl max-h-80 flex flex-col overflow-hidden"
                    role="listbox">
                    <!-- Search Input -->
                    <div v-if="searchable" class="p-2 border-b border-gray-100 flex-shrink-0">
                        <div class="relative">
                            <input ref="searchInputRef" v-model="searchQuery" type="text" placeholder="Cari..."
                                class="w-full px-3 py-2 pl-9 text-sm border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                                @keydown.stop="handleKeydown" />
                            <svg class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" fill="none"
                                stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </div>
                    </div>

                    <!-- Options List -->
                    <div class="overflow-y-auto custom-scrollbar flex-1">
                        <!-- Empty State -->
                        <div v-if="filteredOptions.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
                            {{ searchQuery ? 'Tidak ada hasil yang ditemukan' : 'Tidak ada opsi tersedia' }}
                        </div>

                        <!-- Options -->
                        <button v-for="(option, index) in filteredOptions" :key="option[props.optionValue]" type="button"
                            role="option" :disabled="option.disabled" :aria-selected="option[props.optionValue] === modelValue"
                            :class="[
                                'w-full px-4 py-3 text-left transition-colors border-b border-gray-50 last:border-0',
                                option.disabled
                                    ? 'opacity-50 cursor-not-allowed bg-gray-50'
                                    : 'cursor-pointer hover:bg-gray-50',
                                option[props.optionValue] === modelValue && !option.disabled
                                    ? 'bg-primary/5 text-primary'
                                    : 'text-gray-900',
                                highlightedIndex === index && !option.disabled
                                    ? 'bg-gray-100'
                                    : ''
                            ]" @click="selectOption(option)" @mouseenter="highlightedIndex = index">
                            <!-- Default Template -->
                            <div v-if="optionTemplate === 'default'" class="flex items-center justify-between">
                                <span class="font-medium truncate">{{ option[props.optionLabel] }}</span>

                                <!-- Check Icon for Selected -->
                                <svg v-if="option[props.optionValue] === modelValue" class="h-5 w-5 text-primary flex-shrink-0 ml-2"
                                    fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd"
                                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                        clip-rule="evenodd" />
                                </svg>
                            </div>

                            <!-- Detailed Template -->
                            <div v-else-if="optionTemplate === 'detailed'">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1 min-w-0">
                                        <div class="font-medium truncate">{{ option[props.optionLabel] }}</div>
                                        <div v-if="option.description"
                                            class="text-xs text-gray-500 mt-0.5 line-clamp-2">
                                            {{ option.description }}
                                        </div>
                                    </div>

                                    <!-- Check Icon for Selected -->
                                    <svg v-if="option[props.optionValue] === modelValue"
                                        class="h-5 w-5 text-primary flex-shrink-0 ml-2 mt-0.5" fill="currentColor"
                                        viewBox="0 0 20 20">
                                        <path fill-rule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clip-rule="evenodd" />
                                    </svg>
                                </div>
                            </div>
                        </button>
                    </div>
                </div>
            </Transition>
        </div>

        <!-- Error Message -->
        <p v-if="error" class="text-xs text-red-600">
            {{ error }}
        </p>

        <!-- Helper Text or other validations could go here -->
    </div>
</template>

<style scoped>
/* Custom Scrollbar for better UX within component */
.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: #cbd5e0;
    border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: #a0aec0;
}

/* Firefox */
.custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: #cbd5e0 transparent;
}
</style>
