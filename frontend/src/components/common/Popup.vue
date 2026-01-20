<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

interface Props {
  isOpen: boolean
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'center'
  width?: string
  maxHeight?: string
  closeOnClickOutside?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  position: 'top-right',
  width: '400px',
  maxHeight: '80vh',
  closeOnClickOutside: true
})

const emit = defineEmits<{
  close: []
}>()

const popupRef = ref<HTMLElement | null>(null)

const positionClasses = computed(() => {
  const positions = {
    'top-right': 'top-full right-0 mt-2',
    'top-left': 'top-full left-0 mt-2',
    'bottom-right': 'bottom-full right-0 mb-2',
    'bottom-left': 'bottom-full left-0 mb-2',
    'center': 'top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2'
  }
  return positions[props.position]
})

const handleClickOutside = (event: MouseEvent) => {
  if (!props.closeOnClickOutside) return
  if (popupRef.value && !popupRef.value.contains(event.target as Node)) {
    emit('close')
  }
}

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    emit('close')
  }
}

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    // Prevent body scroll
    document.body.style.overflow = 'hidden'

    setTimeout(() => {
      document.addEventListener('click', handleClickOutside)
      document.addEventListener('keydown', handleEscape)
    }, 0)
  } else {
    // Restore body scroll
    document.body.style.overflow = ''

    document.removeEventListener('click', handleClickOutside)
    document.removeEventListener('keydown', handleEscape)
  }
})

onUnmounted(() => {
  // Cleanup: restore body scroll and remove event listeners
  document.body.style.overflow = ''
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <Transition name="popup">
    <div v-if="isOpen" ref="popupRef" :class="[
      'absolute z-50 bg-white rounded-xl shadow-2xl overflow-y-auto',
      positionClasses
    ]" :style="{
      width: width,
      maxHeight: maxHeight
    }" @click.stop>
      <slot />
    </div>
  </Transition>
</template>

<style scoped>
.popup-enter-active,
.popup-leave-active {
  transition: all 0.2s ease;
}

.popup-enter-from,
.popup-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.popup-enter-to,
.popup-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Custom scrollbar styles */
div[class*="overflow-y-auto"]::-webkit-scrollbar {
  width: 6px;
}

div[class*="overflow-y-auto"]::-webkit-scrollbar-track {
  background: transparent;
  margin: 0.5rem 0;
}

div[class*="overflow-y-auto"]::-webkit-scrollbar-thumb {
  background-color: #d1d5db;
  border-radius: 3px;
}

div[class*="overflow-y-auto"]::-webkit-scrollbar-thumb:hover {
  background-color: #9ca3af;
}

/* Firefox scrollbar */
div[class*="overflow-y-auto"] {
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
}
</style>
