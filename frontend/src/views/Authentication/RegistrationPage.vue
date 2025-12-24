<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full">
      <!-- Progress Indicator -->
      <div class="mb-8">
        <div class="flex items-center justify-center">
          <div
            v-for="step in totalSteps"
            :key="step"
            class="flex items-center"
          >
            <!-- Step Circle -->
            <div class="flex flex-col items-center">
              <div
                :class="[
                  'w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold transition-colors',
                  step <= currentStep
                    ? 'bg-primary text-white'
                    : 'bg-gray-200 text-gray-500'
                ]"
              >
                {{ step }}
              </div>
            </div>
            <!-- Connector Line -->
            <div
              v-if="step < totalSteps"
              :class="[
                'w-24 h-1 mx-2 transition-colors',
                step < currentStep ? 'bg-primary' : 'bg-gray-200'
              ]"
            ></div>
          </div>
        </div>
      </div>

      <!-- Content Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative">
        <!-- Close Button -->
        <router-link
          to="/"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition-colors z-10"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </router-link>

        <!-- Step Content -->
        <transition name="fade" mode="out-in">
          <component
            :is="currentStepComponent"
            :key="currentStep"
          />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRegistrationStore } from '@/stores/registration'
import RegistrationStep1 from './RegistrationStep1.vue'
import RegistrationStep2 from './RegistrationStep2.vue'
import RegistrationStep3 from './RegistrationStep3.vue'

const registrationStore = useRegistrationStore()

const currentStep = computed(() => registrationStore.currentStep)
const totalSteps = registrationStore.totalSteps

const currentStepComponent = computed(() => {
  switch (currentStep.value) {
    case 1:
      return RegistrationStep1
    case 2:
      return RegistrationStep2
    case 3:
      return RegistrationStep3
    default:
      return RegistrationStep1
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
