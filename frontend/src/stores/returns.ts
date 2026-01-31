import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { call } from 'frappe-ui'
import type {
  ReturnReason,
  RefundPaymentMethod,
  EligibleOrder,
  ReturnRequest,
  ReturnRequestFormData,
  WebshopSettings,
  UploadedFile
} from '@/types/returns'

export const useReturnsStore = defineStore('returns', () => {
  // State
  const returnReasons = ref<ReturnReason[]>([])
  const refundPaymentMethods = ref<RefundPaymentMethod[]>([])
  const eligibleOrders = ref<EligibleOrder[]>([])
  const returnRequests = ref<ReturnRequest[]>([])
  const currentReturnRequest = ref<ReturnRequestFormData | null>(null)
  const webshopSettings = ref<WebshopSettings | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isOrderEligibleForReturn = computed(() => {
    return (orderId: string) => {
      return eligibleOrders.value.some(order => order.sales_order === orderId)
    }
  })

  const getReturnRequestById = computed(() => {
    return (requestId: string) => {
      return returnRequests.value.find(req => req.name === requestId)
    }
  })

  // Actions
  async function fetchReturnReasons() {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('webshop.webshop.api.returns.get_return_reasons')
      
      if (response) {
        returnReasons.value = response
      }
    } catch (err) {
      console.error('Error fetching return reasons:', err)
      error.value = 'Gagal memuat alasan pengembalian'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchRefundPaymentMethods() {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('webshop.webshop.api.returns.get_refund_payment_methods')
      
      if (response) {
        refundPaymentMethods.value = response
      }
    } catch (err) {
      console.error('Error fetching refund payment methods:', err)
      error.value = 'Gagal memuat metode pembayaran'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchEligibleOrders() {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('webshop.webshop.api.returns.get_eligible_orders_for_return')
      
      if (response) {
        eligibleOrders.value = response
      }
    } catch (err) {
      console.error('Error fetching eligible orders:', err)
      error.value = 'Gagal memuat pesanan yang dapat dikembalikan'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchReturnRequests(filters?: { status?: string; start?: number; page_length?: number }) {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('webshop.webshop.api.returns.get_customer_return_requests', {
        filters
      })
      
      if (response) {
        returnRequests.value = response
      }
    } catch (err) {
      console.error('Error fetching return requests:', err)
      error.value = 'Gagal memuat daftar pengembalian'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchReturnRequestDetail(requestId: string) {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('webshop.webshop.api.returns.get_return_request_detail', {
        name: requestId
      })
      
      return response
    } catch (err) {
      console.error('Error fetching return request detail:', err)
      error.value = 'Gagal memuat detail pengembalian'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function fetchWebshopSettings() {
    try {
      isLoading.value = true
      error.value = null

      const response = await call('frappe.client.get', {
        doctype: 'Webshop Settings',
        name: 'Webshop Settings'
      })
      
      if (response) {
        webshopSettings.value = response
      }
    } catch (err) {
      console.error('Error fetching webshop settings:', err)
      error.value = 'Gagal memuat pengaturan'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function uploadSupportingDocument(file: File): Promise<UploadedFile> {
    try {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
      if (!allowedTypes.includes(file.type)) {
        throw new Error('Hanya file JPG, PNG, atau PDF yang diperbolehkan')
      }

      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024 // 5MB in bytes
      if (file.size > maxSize) {
        throw new Error('Ukuran file maksimal 5MB')
      }

      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_private', '0')

      const response = await fetch('/api/method/upload_file', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
          'X-Frappe-CSRF-Token': (window as any).csrf_token || ''
        }
      })

      if (!response.ok) {
        throw new Error('Upload gagal')
      }

      const data = await response.json()
      
      if (data.message) {
        return {
          file_url: data.message.file_url,
          file_name: data.message.file_name,
          file_size: file.size
        }
      } else {
        throw new Error('Response upload tidak valid')
      }
    } catch (err) {
      console.error('Error uploading file:', err)
      throw err
    }
  }

  async function createReturnRequest(data: ReturnRequestFormData) {
    try {
      isLoading.value = true
      error.value = null

      // Convert array of file URLs to comma-separated string for backend
      const requestData = {
        ...data,
        supporting_documents: data.supporting_documents
      }

      const response = await call('webshop.webshop.api.returns.create_return_request', {
        data: requestData
      })
      
      if (response) {
        // Refresh the return requests list
        // await fetchReturnRequests()
        return response
      }
    } catch (err: any) {
      console.error('Error creating return request:', err)
      
      // Extract user-friendly error message
      if (err.exc_type === 'ValidationError' || err._server_messages) {
        try {
          const messages = JSON.parse(err._server_messages || '[]')
          if (messages.length > 0) {
            const message = JSON.parse(messages[0])
            error.value = message.message || 'Gagal membuat pengembalian'
          }
        } catch {
          error.value = err.message || 'Gagal membuat pengembalian'
        }
      } else {
        error.value = 'Gagal membuat pengembalian. Silakan coba lagi.'
      }
      
      throw err
    } finally {
      isLoading.value = false
    }
  }

  function initReturnRequest(salesOrder: string) {
    currentReturnRequest.value = {
      sales_order: salesOrder,
      return_reason: '',
      other_reason: '',
      supporting_documents: [],
      refund_payment_mode: '',
      bank_name: '',
      account_number: '',
      account_holder_name: ''
    }
  }

  function clearReturnRequest() {
    currentReturnRequest.value = null
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    returnReasons,
    refundPaymentMethods,
    eligibleOrders,
    returnRequests,
    currentReturnRequest,
    webshopSettings,
    isLoading,
    error,
    
    // Getters
    isOrderEligibleForReturn,
    getReturnRequestById,
    
    // Actions
    fetchReturnReasons,
    fetchRefundPaymentMethods,
    fetchEligibleOrders,
    fetchReturnRequests,
    fetchReturnRequestDetail,
    fetchWebshopSettings,
    uploadSupportingDocument,
    createReturnRequest,
    initReturnRequest,
    clearReturnRequest,
    clearError
  }
})
