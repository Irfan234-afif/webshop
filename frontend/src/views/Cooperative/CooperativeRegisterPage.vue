<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-2xl w-full">

      <!-- Content Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative min-h-[500px]">
        <!-- Close Button -->
        <router-link to="/member" class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition-colors z-10">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </router-link>

        <!-- Loading State -->
        <div v-if="cooperativeStore.isLoading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 rounded-2xl z-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>

        <!-- Step Content -->
        <transition name="fade" mode="out-in">
          <component :is="currentStepComponent" :key="currentStep" />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCooperativeStore } from '@/stores/cooperative'
import CoopRegisterStep1 from './CoopRegisterStep1.vue'
import CoopRegisterStep2 from './CoopRegisterStep2.vue'
import CoopRegisterStep3 from './CoopRegisterStep3.vue'
import CoopRegisterStep4 from './CoopRegisterStep4.vue'
import CoopRegisterStep5 from './CoopRegisterStep5.vue'

const router = useRouter()
const cooperativeStore = useCooperativeStore()

const currentStep = computed(() => cooperativeStore.currentStep)

const currentStepComponent = computed(() => {
  switch (currentStep.value) {
    case 1:
      return CoopRegisterStep1
    case 2:
      return CoopRegisterStep2
    case 3:
      return CoopRegisterStep3
    case 4:
      return CoopRegisterStep4
    case 5:
      return CoopRegisterStep5
    default:
      return CoopRegisterStep1
  }
})

onMounted(async () => {
  // Reset form state on load
  cooperativeStore.resetForm()
  
  // Check membership status first
  await cooperativeStore.fetchMembershipStatus()
  
  if (cooperativeStore.membershipStatus?.is_member) {
    // If already a member or has a pending registration, redirect to the membership dashboard
    router.replace('/member')
    return
  }

  // Pre-fetch settings for fee calculation
  await cooperativeStore.fetchSettings()
})

onUnmounted(() => {
  cooperativeStore.resetForm()
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
