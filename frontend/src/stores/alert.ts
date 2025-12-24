import { defineStore } from 'pinia'
import { ref } from 'vue'

export type AlertType = 'success' | 'error' | 'warning' | 'info'

export interface Alert {
  id: string
  type: AlertType
  title?: string
  message: string
  timeout?: number
}

export const useAlertStore = defineStore('alert', () => {
  const alerts = ref<Alert[]>([])

  const addAlert = (alert: Omit<Alert, 'id'>) => {
    const id = Date.now().toString() + Math.random().toString(36).substring(2)
    const newAlert = { ...alert, id }
    alerts.value.push(newAlert)

    if (alert.timeout !== 0) {
      setTimeout(() => {
        removeAlert(id)
      }, alert.timeout || 3000)
    }
  }

  const removeAlert = (id: string) => {
    const index = alerts.value.findIndex((a) => a.id === id)
    if (index !== -1) {
      alerts.value.splice(index, 1)
    }
  }

  const success = (message: string, title?: string, timeout?: number) => {
    addAlert({ type: 'success', message, title, timeout })
  }

  const error = (message: string, title?: string, timeout?: number) => {
    addAlert({ type: 'error', message, title, timeout })
  }

  const warning = (message: string, title?: string, timeout?: number) => {
    addAlert({ type: 'warning', message, title, timeout })
  }

  const info = (message: string, title?: string, timeout?: number) => {
    addAlert({ type: 'info', message, title, timeout })
  }

  return {
    alerts,
    addAlert,
    removeAlert,
    success,
    error,
    warning,
    info
  }
})
