<template>
  <DefaultLayout>
    <Container class="py-6 !max-w-2xl mx-auto">
      <!-- Breadcrumb -->
      <Breadcrumb :items="[
        { label: 'Home', to: '/' },
        { label: 'Pesanan', to: '/orders' },
        { label: 'Beri Penilaian' }
      ]" class="mb-6" />

      <!-- Page Title -->
      <div class="mb-8">
        <h1 class="text-xl font-bold text-gray-900 mb-2">Beri Penilaian</h1>
        <p class="text-gray-500 font-semibold" v-if="orderResource.data">
          Pesanan #{{ orderResource.data.name }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="orderResource.loading" class="flex justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>

      <!-- Items List -->
      <div v-else-if="orderResource.data" class="space-y-6 max-w-3xl">
        <div v-for="item in visibleItems" :key="item.item_code" 
          class="bg-white border border-gray-200 rounded-xl p-6 transition-all hover:shadow-md">
          <div class="flex gap-4">
            <!-- Product Image -->
            <div class="w-20 h-20 bg-gray-50 rounded-lg flex-shrink-0 border border-gray-100 overflow-hidden">
              <img v-if="item.image" :src="item.image" :alt="item.item_name" class="w-full h-full object-cover">
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <span class="text-xs">No Img</span>
              </div>
            </div>

            <!-- Product Details & Review Form -->
            <div class="flex-1">
              <h3 class="font-bold text-gray-900 mb-1">{{ item.item_name }}</h3>
              <p class="text-sm text-gray-500 mb-4">{{ item.item_code }}</p>

              <!-- Already Reviewed State (Simplified for now, just check local state or if we want to confirm from backend) -->
              <div v-if="item.isReviewed" class="bg-green-50 text-green-700 p-4 rounded-lg flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <span class="font-medium">Ulasan Anda telah dikirim</span>
              </div>

              <!-- Review Form -->
              <div v-else class="space-y-4">
                <!-- Rating -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Berikan rating</label>
                  <div class="flex gap-2">
                    <button v-for="star in 5" :key="star" 
                      @click="setRating(item.item_code, star)"
                      type="button"
                      class="focus:outline-none transition-transform active:scale-95"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" 
                        class="h-8 w-8 transition-colors" 
                        :class="star <= (ratings[item.item_code] || 0) ? 'text-yellow-400 fill-current' : 'text-gray-300'"
                        fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Review Title -->
                <div>
                   <label class="block text-sm font-medium text-gray-700 mb-2">Judul Ulasan</label>
                   <input 
                    v-model="titles[item.item_code]"
                    type="text" 
                    placeholder="Contoh: Sangat puas dengan barangnya!"
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors"
                   />
                </div>

                <!-- Comment -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Tulis ulasan Anda</label>
                  <textarea 
                    v-model="comments[item.item_code]"
                    rows="3"
                    placeholder="Bagikan pengalaman Anda menggunakan produk ini..."
                    class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary/20 focus:border-primary transition-colors resize-none"
                  ></textarea>
                </div>

                <!-- Submit Button -->
                <div class="flex justify-end">
                  <button 
                    @click="submitReview(item)"
                    :disabled="!isValid(item.item_code) || submitting[item.item_code]"
                    class="bg-primary text-white font-bold py-2 px-6 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  >
                    <span v-if="submitting[item.item_code]" class="animate-spin h-4 w-4 border-2 border-white border-b-transparent rounded-full"></span>
                    <span>{{ submitting[item.item_code] ? 'Mengirim...' : 'Kirim Ulasan' }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import { call } from 'frappe-ui'
import { useAlertStore } from '@/stores/alert'
import { extractErrorMessage } from '@/utils/errorHandler'

const route = useRoute()
const alertStore = useAlertStore()
const router = useRouter()
const orderId = route.params.id as string

if (!orderId) {
  router.push('/orders')
}

// State for form inputs
const ratings = reactive<Record<string, number>>({})
const titles = reactive<Record<string, string>>({})
const comments = reactive<Record<string, string>>({})
const submitting = reactive<Record<string, boolean>>({})

// Helper to check validity
const isValid = (itemCode: string) => {
  return (ratings[itemCode] || 0) > 0 && (titles[itemCode] || '').trim().length > 0 && (comments[itemCode] || '').trim().length > 0
}

const setRating = (itemCode: string, rating: number) => {
  ratings[itemCode] = rating
}

// Review Submission Resource
// We use frappe.call directly via createResource logic or manual fetch to handle per-item submission
const submitReview = async (item: any) => {
  if (!isValid(item.item_code)) return

  submitting[item.item_code] = true

  try {
    const response = await call('webshop.webshop.doctype.item_review.item_review.add_item_review', {
      web_item: item.website_item,
      title: titles[item.item_code],
      rating: (ratings[item.item_code] || 0) / 5, // Normalize 1-5 to 0-1
      comment: comments[item.item_code],
      sales_order: orderId
    })

    // Mark as reviewed visually
    item.isReviewed = true
    
  } catch (error: any) {
    const message = extractErrorMessage(error)
    alertStore.error(message)
  } finally {
    submitting[item.item_code] = false
  }
}

const orderResource = createResource({
  url: 'webshop.webshop.api.orders.get_order_details',
  params: { order_name: orderId },
  auto: true
})

const visibleItems = computed(() => {
  if (!orderResource.data || !orderResource.data.items) return []
  // We can filter out items that don't have a website_item if needed, but they should generally have one if they are products
  return orderResource.data.items.map((item: any) => ({
    ...item,
    isReviewed: item.is_reviewed || false // Use backend flag
  }))
})

// Initialize form state when items are loaded
// This isn't strictly necessary with reactive objects but good for explicit defaults if needed
</script>
