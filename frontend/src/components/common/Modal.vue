<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'

interface Props {
  isOpen: boolean
  title?: string
  position?: 'bottom' | 'right'
}

const props = withDefaults(defineProps<Props>(), {
  position: 'bottom'
})

const emit = defineEmits<{
  close: []
}>()

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.isOpen) {
    emit('close')
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
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/50"
        @click="emit('close')"
        aria-hidden="true"
      />
    </Transition>

    <!-- Modal Content -->
    <Transition :name="position === 'bottom' ? 'slide-up' : 'slide-left'">
      <div
        v-if="isOpen"
        :class="[
          'fixed z-50 bg-white',
          position === 'bottom'
            ? 'bottom-0 left-0 right-0 max-h-[85vh] rounded-t-3xl'
            : 'right-0 top-0 h-full w-full max-w-md'
        ]"
        role="dialog"
        aria-modal="true"
        @click.stop
      >
        <!-- Header -->
        <div class="sticky top-0 z-10 bg-white px-6 py-4">
          <div class="flex items-center justify-between">
            <h2 v-if="title" class="text-lg font-bold text-gray-900">{{ title }}</h2>
            <button
              @click="emit('close')"
              class="flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-gray-100"
              aria-label="Close"
            >
              <svg
                class="h-6 w-6 text-gray-600"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div
          class="overflow-y-auto px-6 pb-6"
          :style="{
            maxHeight: position === 'bottom' ? 'calc(85vh - 72px)' : 'calc(100vh - 72px)'
          }"
        >
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
/* Fade transition for backdrop */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide up transition for bottom modal */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

/* Slide left transition for right modal */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.3s ease;
}

.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(100%);
}
</style>
