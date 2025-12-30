<script setup lang="ts">
import { useAlertStore } from '@/stores/alert'
import { storeToRefs } from 'pinia'

const alertStore = useAlertStore()
const { alerts } = storeToRefs(alertStore)



const getStyles = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-50 text-green-800 border-green-200'
    case 'error':
      return 'bg-red-50 text-red-800 border-red-200'
    case 'warning':
      return 'bg-yellow-50 text-yellow-800 border-yellow-200'
    case 'info':
      return 'bg-blue-50 text-blue-800 border-blue-200'
    default:
      return 'bg-gray-50 text-gray-800 border-gray-200'
  }
}
</script>

<template>
  <div class="fixed bottom-4 right-4 z-[9999] flex flex-col gap-3 w-full max-w-sm px-4 sm:px-0">
    <TransitionGroup name="toast">
      <div
        v-for="alert in alerts"
        :key="alert.id"
        class="relative flex items-start gap-3 rounded-xl border p-4 shadow-lg transition-all"
        :class="getStyles(alert.type)"
        role="alert"
      >
        <!-- Icon -->
        <div class="flex-shrink-0">
          <svg v-if="alert.type === 'success'" class="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <svg v-else-if="alert.type === 'error'" class="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <svg v-else-if="alert.type === 'warning'" class="h-5 w-5 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
          </svg>
          <svg v-else class="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- Content -->
        <div class="flex-1 min-w-0">
          <h3 v-if="alert.title" class="text-sm font-medium">
            {{ alert.title }}
          </h3>
          <div class="text-sm opacity-90 break-words">
            {{ alert.message }}
          </div>
        </div>

        <!-- Close Button -->
        <button
          @click="alertStore.removeAlert(alert.id)"
          class="flex-shrink-0 -mr-1 -mt-1 p-1 rounded-full opacity-60 hover:opacity-100 transition-opacity focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="alert.type === 'error' ? 'focus:ring-red-500' : 'focus:ring-blue-500'"
        >
          <svg class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
