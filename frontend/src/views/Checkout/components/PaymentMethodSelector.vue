<template>
  <div class="payment-method-selector">
    <div class="space-y-4">
      <!-- Payment Methods -->
      <div
        v-for="method in paymentMethods"
        :key="method.name"
        class="payment-option"
        :class="{
          'selected': selectedMethod === method.name,
          'disabled': !method.enabled
        }"
        @click="method.enabled && selectPaymentMethod(method.name)"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start flex-1">
            <!-- Icon -->
            <div class="payment-icon" :class="{ 'disabled': !method.enabled }">
              <component :is="getIcon(method.icon)" class="w-6 h-6" />
            </div>

            <!-- Content -->
            <div class="flex-1 ml-4">
              <div class="flex items-center gap-2">
                <h3 class="font-semibold text-lg">{{ method.label }}</h3>
                <svg
                  v-if="!method.enabled"
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-5 h-5 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <p class="text-sm text-gray-600 mt-1">
                {{ method.description }}
                <span v-if="!method.enabled && method.name === 'Cicilan Koperasi'" class="text-primary font-medium">
                  Syarat & Ketentuan.
                </span>
              </p>

              <!-- Channels Grid -->
              <div v-if="method.payment_channels && method.payment_channels.length > 0 && selectedMethod === method.name" class="mt-4 grid grid-cols-2 gap-3">
                <div
                  v-for="channel in method.payment_channels"
                  :key="channel.channel_code"
                  class="channel-option p-3 border rounded-lg flex items-center gap-3 cursor-pointer transition-all"
                  :class="{
                    'border-primary bg-purple-50 ring-1 ring-primary': selectedChannel === channel.channel_code,
                    'border-gray-200 hover:border-blue-300': selectedChannel !== channel.channel_code
                  }"
                  @click.stop="selectChannel(channel.channel_code)"
                >
                   <!-- Channel Icon -->
                   <img 
                      v-if="channel.icon" 
                      :src="channel.icon" 
                      :alt="channel.channel_name"
                      class="w-8 h-8 object-contain"
                   />
                   <div v-else class="w-8 h-8 bg-gray-100 rounded flex items-center justify-center text-xs text-gray-500">
                      {{ channel.channel_code }}
                   </div>

                   <div class="flex-1 min-w-0">
                      <p class="font-medium text-sm truncate">{{ channel.channel_name }}</p>
                      <p v-if="channel.description" class="text-xs text-gray-500 truncate">{{ channel.description }}</p>
                   </div>
                   
                   <!-- Checkmark -->
                  <div v-if="selectedChannel === channel.channel_code" class="text-primary">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Radio Button -->
          <div class="ml-4">
            <div
              class="radio-button"
              :class="{
                'checked': selectedMethod === method.name,
                'disabled': !method.enabled
              }"
            >
              <div v-if="selectedMethod === method.name" class="radio-dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, h } from 'vue'
import { useCheckoutStore } from '@/stores/checkout'
import { storeToRefs } from 'pinia'

const checkoutStore = useCheckoutStore()
const { paymentMethods, paymentMethodType, paymentChannel } = storeToRefs(checkoutStore)

const selectedMethod = ref<string>(paymentMethodType.value || '')
const selectedChannel = ref<string>(paymentChannel.value || '')

// Watch for changes from store to local
watch([paymentMethodType, paymentChannel], ([newType, newChannel]) => {
  selectedMethod.value = newType || ''
  selectedChannel.value = newChannel || ''
})

// Watch for local changes and sync to store
watch(selectedMethod, (newVal) => {
  if (newVal) {
    checkoutStore.paymentMethodType = newVal
  }
})

onMounted(async () => {
  if (paymentMethods.value.length === 0) {
    await checkoutStore.fetchPaymentMethods()
  }
})

function selectPaymentMethod(methodName: string) {
  selectedMethod.value = methodName
  checkoutStore.paymentMethodType = methodName
  
  // If method has channels, don't clear channel yet unless switching methods
  // But strictly, if we switch method, we should clear channel
  // EXCEPT if we are re-clicking the same method
  
  const method = paymentMethods.value.find(m => m.name === methodName)
  if (method && (!method.payment_channels || method.payment_channels.length === 0)) {
     selectedChannel.value = ''
     checkoutStore.paymentChannel = ''
  }
  
  console.log('✅ Payment method selected:', methodName)
}

function selectChannel(channelCode: string) {
  selectedChannel.value = channelCode
  checkoutStore.paymentChannel = channelCode
  console.log('✅ Payment channel selected:', channelCode)
}

// Icon components as simple SVG elements
function getIcon(iconName: string) {
  const icons: Record<string, any> = {
    'receipt': () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      class: 'w-6 h-6'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
      })
    ]),
    'credit-card': () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      class: 'w-6 h-6'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z'
      })
    ]),
    'dollar-sign': () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      class: 'w-6 h-6'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
      })
    ]),
    'calculator': () => h('svg', {
      xmlns: 'http://www.w3.org/2000/svg',
      fill: 'none',
      viewBox: '0 0 24 24',
      stroke: 'currentColor',
      class: 'w-6 h-6'
    }, [
      h('path', {
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round',
        'stroke-width': '2',
        d: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z'
      })
    ])
  }

  return icons[iconName] || icons['receipt']
}

defineExpose({
  selectedMethod,
  selectedChannel
})
</script>

<style scoped>
.payment-option {
  @apply border-2 border-gray-200 rounded-lg p-6 cursor-pointer transition-all duration-200;
}

.payment-option:hover:not(.disabled) {
  @apply border-primary;
}

.payment-option.selected {
  @apply border-primary bg-purple-50;
}

.payment-option.disabled {
  @apply bg-gray-50 cursor-not-allowed opacity-75;
}

.payment-icon {
  @apply w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center flex-shrink-0;
}

.payment-icon.disabled {
  @apply bg-gray-400;
}

.radio-button {
  @apply w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center;
}

.radio-button.checked {
  @apply border-primary;
}

.radio-button.disabled {
  @apply border-gray-300 bg-gray-100;
}

.radio-dot {
  @apply w-3 h-3 rounded-full bg-primary;
}
</style>
