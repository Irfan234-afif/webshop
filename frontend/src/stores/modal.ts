import { defineStore } from 'pinia'
import { ref, shallowRef } from 'vue'

interface ModalOptions {
  component: any
  props?: Record<string, any>
  showCloseButton?: boolean
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
}

export const useModalStore = defineStore('modal', () => {
  const currentModal = shallowRef<{ component: any; props: Record<string, any> } | null>(null)
  const isOpen = ref(false)
  const options = shallowRef<ModalOptions>({
    component: null,
    props: {},
    showCloseButton: true,
    closeOnBackdrop: true,
    closeOnEscape: true
  })

  const showModal = (modalOptions: ModalOptions) => {
    options.value = {
      component: modalOptions.component,
      props: modalOptions.props || {},
      showCloseButton: modalOptions.showCloseButton ?? true,
      closeOnBackdrop: modalOptions.closeOnBackdrop ?? true,
      closeOnEscape: modalOptions.closeOnEscape ?? true
    }
    isOpen.value = true
  }

  const closeModal = () => {
    isOpen.value = false
    currentModal.value = null
  }

  const handleLoginSuccess = () => {
    closeModal()
    // Optionally emit a login success event
  }

  return {
    currentModal,
    isOpen,
    options,
    showModal,
    closeModal,
    handleLoginSuccess
  }
})