<script setup lang="ts">
import { RouterView, useRouter } from 'vue-router'
import { useModalStore } from '@/stores/modal'
import DynamicModal from '@/components/common/DynamicModal.vue'
import LoginModal from '@/components/common/LoginModal.vue'
import RegistrationModal from '@/components/common/RegistrationModal.vue'
import GlobalAlert from '@/components/common/GlobalAlert.vue'
import { getCookie, setCookie } from '@/utils/storage'
import { onMounted } from 'vue'

const router = useRouter()
const modalStore = useModalStore()

// Listen for global event to show login modal
onMounted(() => {
  // Set default language to Indonesian if not set
  if (!getCookie('preferred_language')) {
    setCookie('preferred_language', 'id')
  }

  window.addEventListener('showLoginModal', () => {
    modalStore.showModal({
      component: LoginModal,
      props: {},
      showCloseButton: true,
      closeOnBackdrop: true,
      closeOnEscape: true
    })
  })
})

// Method to navigate to registration page
const showRegistrationModal = () => {
  // Close current modal first
  modalStore.closeModal()
  // Navigate to registration page
  router.push('/register')
}
</script>

<template>
  <div id="app">
    <RouterView v-slot="{ Component, route }">
      <template v-if="route.meta.keepAlive">
        <KeepAlive>
          <component :is="Component" />
        </KeepAlive>
      </template>
      <template v-else>
        <component :is="Component" />
      </template>
    </RouterView>

    <!-- Dynamic Modal -->
    <DynamicModal :is-open="modalStore.isOpen" :component="modalStore.options.component"
      :component-props="modalStore.options.props" :show-close-button="modalStore.options.showCloseButton"
      :close-on-backdrop="modalStore.options.closeOnBackdrop" :close-on-escape="modalStore.options.closeOnEscape"
      @close="modalStore.closeModal" @login-success="modalStore.handleLoginSuccess"
      @showRegistrationModal="showRegistrationModal" />

    <!-- Global Alert / Toast System -->
    <GlobalAlert />
  </div>
</template>

<style scoped>
/* Remove default app container constraints for full width */
:deep(#app) {
  max-width: 100%;
  margin: 0;
  padding: 0;
  display: block;
}
</style>
