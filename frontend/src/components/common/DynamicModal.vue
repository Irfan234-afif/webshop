<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-50 bg-black/50"
      @click="handleBackdropClick"
      aria-hidden="true"
    />

    <!-- Modal Content -->
    <Transition name="modal-slide">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        @click.stop
      >
        <div
          ref="modalRef"
          class="relative bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden"
        >
          <!-- Close Button -->
          <button
            v-if="showCloseButton"
            @click="closeModal"
            class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-20"
            aria-label="Close"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- Dynamic Content -->
          <div class="p-8">
            <component
              :is="component"
              v-bind="componentProps"
              @close="closeModal"
              @loginSuccess="handleLoginSuccess"
              @showRegistrationModal="handleShowRegistrationModal"
            />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

interface Props {
  isOpen: boolean
  component: any
  componentProps?: Record<string, any>
  showCloseButton?: boolean
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  componentProps: () => ({}),
  showCloseButton: true,
  closeOnBackdrop: true,
  closeOnEscape: true
})

const emit = defineEmits<{
  close: []
  loginSuccess: []
  showRegistrationModal: []
}>()

const modalRef = ref<HTMLElement | null>(null)

// Handle escape key to close modal
const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.closeOnEscape) {
    closeModal()
  }
}

// Prevent body scroll when modal is open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleEscape)
    } else {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleEscape)
    }
  }
)

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleEscape)
})

const closeModal = () => {
  emit('close')
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    closeModal()
  }
}

const handleLoginSuccess = () => {
  emit('loginSuccess')
  closeModal()
}

const handleShowRegistrationModal = () => {
  emit('showRegistrationModal')
}
</script>

<style scoped>
/* Slide up transition for modal */
.modal-slide-enter-active,
.modal-slide-leave-active {
  transition: all 0.3s ease;
}

.modal-slide-enter-from,
.modal-slide-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>