<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAlertStore } from '@/stores/alert'
import { validateCartStock } from '@/utils/cartApi'
import { extractErrorMessage } from '@/utils/errorHandler'
import CartItem from './components/CartItem.vue'
import CartSummary from './components/CartSummary.vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import Container from '@/components/layout/Container.vue'

import type { StudentCart } from '@/types/cart'

// Set component name for KeepAlive caching
defineOptions({
  name: 'CartPage'
})

const router = useRouter()
const cartStore = useCartStore()
const alertStore = useAlertStore()

// Checkout modal state
const isCheckoutProcessing = ref(false)


onMounted(async () => {
  await cartStore.fetchAllStudentCarts()
})

const breadcrumbItems = [
  { label: 'Home', to: '/' },
  { label: 'Keranjang Belanja' }
]


// Student cart sections expanded state
const studentCartsExpanded = ref<Record<string, boolean>>({})

// Initialize student selection after data loads
watch(() => cartStore.studentCarts, (studentCarts) => {
  if (studentCarts.length > 0) {

    studentCartsExpanded.value[cartStore.selectedStudentCart?.name || ''] = true
  }
}, { immediate: true })


const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0,
  }).format(amount)
}

const toggleStudentCart = (studentName: string) => {
  studentCartsExpanded.value[studentName] = !studentCartsExpanded.value[studentName]
}

const toggleStudentSelection = (studentName: StudentCart) => {
  cartStore.selectedStudentCart = studentName;
  toggleStudentCart(studentName.name)
}

const isStudentSelected = (studentName: string) => {
  return cartStore.selectedStudentCart?.name === studentName
}

const handleUpdateQuantity = (itemCode: string, quantity: number, quotationName: string) => {
  cartStore.updateQuantity(itemCode, quantity, quotationName)
}

const handleRemoveItem = (itemCode: string, quotationName: string) => {
  cartStore.removeItem(itemCode, quotationName)
}

const handleCheckout = async () => {
  // CRITICAL: Only allow checkout for exactly ONE student at a time
  // One student = one quotation = one checkout
  if (cartStore.selectedStudentCart === null) {
    alertStore.warning('Silakan pilih satu siswa untuk checkout', 'Peringatan')
    return
  }

  isCheckoutProcessing.value = true
  try {
    await validateCartStock(cartStore.selectedStudentCart.quotation_name)

    // Navigate to checkout page with selected student
    router.push({
      name: 'checkout',
      query: { student: cartStore.selectedStudentCart.student_name, quotation: cartStore.selectedStudentCart.quotation_name }
    })
  } catch (error: any) {
    const errorMessage = extractErrorMessage(error)
    alertStore.error(errorMessage, 'Gagal')
  } finally {
    isCheckoutProcessing.value = false
  }
}

const goHome = () => {
  router.push('/')
}

// Calculate items for selected students
// const selectedItems = computed(() => {
//   return cartStore.items.filter(item =>
//     item.student && selectedStudentIds.value.includes(item.student)
//   )
// })
</script>

<template>
  <DefaultLayout>
    <div class="min-h-screen">
      <Container class="py-4 md:py-6 lg:py-8">
        <!-- Breadcrumb -->
        <Breadcrumb :items="breadcrumbItems" class="mb-4 md:mb-6" />

        <!-- Main Content -->
        <div>
          <!-- Page Title -->
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-2">Keranjang Belanja</h1>
          </div>

          <!-- Two Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <!-- Left Column - Student Carts -->
            <div class="lg:col-span-2 space-y-4">
              <!-- Empty Cart State -->
              <div v-if="cartStore.selectedStudentCart?.items.length === 0"
                class="bg-white rounded-lg border border-gray-200 p-12 text-center">
                <svg class="w-20 h-20 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">Keranjang Belanja Kosong</h3>
                <p class="text-gray-500 mb-6">Belum ada produk di keranjang belanja</p>
                <button @click="goHome"
                  class="inline-flex items-center px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:bg-secondary-alt transition-colors">
                  Mulai Belanja
                </button>
              </div>

              <!-- Student Cart Groups -->
              <div v-for="student in cartStore.studentCarts" :key="student.name"
                class="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <!-- Student Cart Header -->
                <button @click="toggleStudentCart(student.name)"
                  class="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
                  <div class="flex items-center gap-3">
                    <input type="checkbox" :checked="isStudentSelected(student.name)"
                      class="w-5 h-5 text-primary rounded border-gray-300 focus:ring-primary"
                      @click.stop="toggleStudentSelection(student)" />
                    <div class="text-left">
                      <h3 class="font-bold text-gray-900">{{ student.student_name }}</h3>
                      <p class="text-xs text-gray-500">
                        {{ student.itemCount }} Produk
                      </p>
                    </div>
                  </div>
                  <div class="flex items-center gap-4">
                    <p class="text-sm">
                      <span class="font-bold text-primary">
                        {{ student.itemCount }} Produk
                      </span>
                      <span> - </span>
                      <span class="font-bold text-primary">
                        {{ formatCurrency(student.total) }}
                      </span>
                    </p>
                    <svg class="w-5 h-5 text-gray-400 transition-transform"
                      :class="{ 'rotate-180': studentCartsExpanded[student.name] }" fill="none" stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </button>

                <!-- Student's Items List -->
                <div v-if="studentCartsExpanded[student.name]" class="border-t border-gray-200 p-4 space-y-3">
                  <CartItem v-for="item in student.items" :key="item.id" :item="item"
                    :quotation_name="student.quotation_name" @update-quantity="handleUpdateQuantity"
                    @remove="handleRemoveItem" />
                </div>
              </div>
            </div>

            <!-- Right Column - Order Summary -->
            <div class="lg:col-span-1">
              <CartSummary :items="cartStore.selectedStudentCart ? cartStore.selectedStudentCart.items : []"
                :quotation-name="cartStore.selectedStudentCart?.quotation_name"
                :coupon-code="cartStore.selectedStudentCart?.coupon_code"
                :discount-amount="cartStore.selectedStudentCart?.discount_amount"
                :original-total="cartStore.selectedStudentCart?.total"
                :is-checkout-loading="isCheckoutProcessing" @checkout="handleCheckout" />
            </div>
          </div>
        </div>
      </Container>
    </div>


  </DefaultLayout>
</template>

<style scoped>
.rotate-180 {
  transform: rotate(180deg);
}
</style>
