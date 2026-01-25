<template>
  <DefaultLayout>
    <div class="bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div class="max-w-2xl w-full">
        <!-- Back Button -->
        <button
          @click="router.back()"
          class="mb-6 flex items-center gap-2 text-sm font-medium text-gray-500 hover:text-gray-700 transition"
        >
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Kembali
        </button>

        <!-- Content Card -->
        <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative">
          
          <!-- Progress Bar -->
          <div class="mb-10">
            <div class="flex items-center justify-between">
              <div 
                v-for="n in totalSteps" 
                :key="n" 
                class="flex flex-col items-center flex-1 relative"
              >
                <!-- Connector Line -->
                <div 
                  v-if="n < totalSteps"
                  class="absolute top-4 left-1/2 w-full h-1 -z-0"
                  :class="n < currentStep ? 'bg-primary' : 'bg-gray-200'"
                ></div>

                <div 
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold z-10 transition-colors duration-300',
                    n <= currentStep ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'
                  ]"
                >
                  {{ n }}
                </div>
                <span class="mt-2 text-xs font-medium text-gray-500 hidden md:block">
                  {{ getStepLabel(n) }}
                </span>
              </div>
            </div>
          </div>

          <!-- Step Content -->
          <transition name="fade" mode="out-in">
            <div :key="currentStep" class="min-h-[300px]">
              
              <!-- Step 1: Address Details -->
              <div v-if="currentStep === 1">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Lokasi Survey</h2>
                <p class="text-gray-600 mb-8">Masukkan alamat lengkap lokasi survey untuk produk {{ productTitle }}</p>

                <form @submit.prevent="nextStep">
                  <!-- Full Address -->
                  <div class="mb-5">
                    <label for="full_address" class="block text-sm font-bold text-gray-700 mb-2">Alamat Lengkap (Nama Jalan, No. Rumah)</label>
                    <textarea
                      id="full_address"
                      v-model="formData.full_address"
                      rows="3"
                      required
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                      placeholder="Jl. Contoh No. 123, RT/RW 01/02"
                    ></textarea>
                  </div>

                  <!-- Province & City -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
                    <div>
                      <label for="province" class="block text-sm font-bold text-gray-700 mb-2">Provinsi</label>
                      <input
                        id="province"
                        v-model="formData.province"
                        type="text"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                        placeholder="Jawa Barat"
                      />
                    </div>
                    <div>
                      <label for="city" class="block text-sm font-bold text-gray-700 mb-2">Kota/Kabupaten</label>
                      <input
                        id="city"
                        v-model="formData.city"
                        type="text"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                        placeholder="Bandung"
                      />
                    </div>
                  </div>

                  <!-- Subdistrict & Village -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
                    <div>
                      <label for="subdistrict" class="block text-sm font-bold text-gray-700 mb-2">Kecamatan</label>
                      <input
                        id="subdistrict"
                        v-model="formData.subdistrict"
                        type="text"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                        placeholder="Coblong"
                      />
                    </div>
                    <div>
                      <label for="village" class="block text-sm font-bold text-gray-700 mb-2">Kelurahan/Desa</label>
                      <input
                        id="village"
                        v-model="formData.village"
                        type="text"
                        required
                        class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                        placeholder="Dago"
                      />
                    </div>
                  </div>

                  <!-- Postal Code -->
                  <div class="mb-8">
                    <label for="postal_code" class="block text-sm font-bold text-gray-700 mb-2">Kode Pos</label>
                    <input
                      id="postal_code"
                      v-model="formData.postal_code"
                      type="text"
                      required
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                      placeholder="40135"
                    />
                  </div>

                  <button
                    type="submit"
                    :disabled="!isStep1Valid"
                    class="w-full bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                  >
                    Lanjutkan
                  </button>
                </form>
              </div>

              <!-- Step 2: Date & Time -->
              <div v-else-if="currentStep === 2">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Jadwal Survey</h2>
                <p class="text-gray-600 mb-8">Pilih waktu yang sesuai untuk survey</p>

                <form @submit.prevent="nextStep">
                  <!-- Date -->
                  <div class="mb-6">
                    <label for="survey_date" class="block text-sm font-bold text-gray-700 mb-2">Tanggal Survey</label>
                    <input
                      id="survey_date"
                      v-model="formData.date"
                      type="date"
                      required
                      :min="minDate"
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                    />
                  </div>

                  <!-- Time -->
                  <div class="mb-8">
                    <label for="survey_time" class="block text-sm font-bold text-gray-700 mb-2">Waktu Survey</label>
                    <input
                      id="survey_time"
                      v-model="formData.time"
                      type="time"
                      required
                      class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                    />
                  </div>

                  <!-- Navigation Buttons -->
                  <div class="flex gap-4">
                    <button
                      type="button"
                      @click="prevStep"
                      class="flex-1 border border-gray-300 text-gray-700 font-bold py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      Kembali
                    </button>
                    <button
                      type="submit"
                      :disabled="!isStep2Valid"
                      class="flex-1 bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                    >
                      Lanjutkan
                    </button>
                  </div>
                </form>
              </div>

              <!-- Step 3: Confirmation -->
              <div v-else-if="currentStep === 3">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Konfirmasi Survey</h2>
                <p class="text-gray-600 mb-8">Pastikan data berikut sudah benar sebelum mengajukan</p>

                <!-- Address Summary -->
                <div class="mb-4 p-5 bg-blue-50 rounded-xl border border-blue-100">
                  <h3 class="font-bold text-blue-900 mb-3 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Lokasi
                  </h3>
                  <div class="space-y-1 ml-7">
                    <p class="text-sm text-blue-800">{{ formData.full_address }}</p>
                    <p class="text-sm text-blue-800">{{ formData.village }}, {{ formData.subdistrict }}</p>
                    <p class="text-sm text-blue-800">{{ formData.city }}, {{ formData.province }} {{ formData.postal_code }}</p>
                  </div>
                </div>

                <!-- Schedule Summary -->
                <div class="mb-8 p-5 bg-green-50 rounded-xl border border-green-100">
                  <h3 class="font-bold text-green-900 mb-3 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Jadwal
                  </h3>
                  <div class="space-y-1 ml-7">
                    <p class="text-sm text-green-800"><span class="font-semibold">Tanggal:</span> {{ formatDate(formData.date) }}</p>
                    <p class="text-sm text-green-800"><span class="font-semibold">Jam:</span> {{ formData.time }}</p>
                  </div>
                </div>

                <!-- Navigation Buttons -->
                <div class="flex gap-4">
                  <button
                    @click="prevStep"
                    class="flex-1 border border-gray-300 text-gray-700 font-bold py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors"
                  >
                    Kembali
                  </button>
                  <button
                    @click="submitSurvey"
                    :disabled="isSubmitting"
                    class="flex-1 bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors flex items-center justify-center disabled:opacity-50 shadow-lg hover:shadow-xl"
                  >
                    <svg
                      v-if="isSubmitting"
                      class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        class="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        stroke-width="4"
                      ></circle>
                      <path
                        class="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    <span v-if="isSubmitting">Memproses...</span>
                    <span v-else>Ajukan Survey</span>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useAlertStore } from '@/stores/alert'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import { call } from 'frappe-ui'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const alertStore = useAlertStore()

const webItemCode = computed(() => route.params.webItemCode as string)
const productTitle = ref('Loading...') // Could fetch product details to get usage

const currentStep = ref(1)
const totalSteps = 3
const isSubmitting = ref(false)

// Form Data with default empty values
const formData = ref({
  full_address: '',
  province: '',
  city: '',
  subdistrict: '',
  village: '',
  postal_code: '',
  date: '',
  time: ''
})

onMounted(() => {
  if (!webItemCode.value) {
    alertStore.error('Produk tidak valid', 'Error')
    router.push('/products')
  }
  
  // Optionally fetch product details here to show title
  fetchProductTitle(webItemCode.value)
})

const fetchProductTitle = async (code: string) => {
  try {
     // reuse existing api or create lightweight one
     // For now just using generic or fetching from store if available
     // But store might not be populated if landing directly.
     // Let's assume user came from product page for now.
  } catch (e) {
    // ignore
  }
}

// Validation for Step 1
const isStep1Valid = computed(() => {
  return (
    formData.value.full_address &&
    formData.value.province &&
    formData.value.city &&
    formData.value.subdistrict &&
    formData.value.village &&
    formData.value.postal_code
  )
})

// Validation for Step 2
const isStep2Valid = computed(() => {
  return formData.value.date && formData.value.time
})

// Minimum date calculation (today)
const minDate = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const getStepLabel = (step: number) => {
  switch(step) {
    case 1: return 'Lokasi'
    case 2: return 'Jadwal'
    case 3: return 'Konfirmasi'
    default: return ''
  }
}

const nextStep = () => {
  if (currentStep.value < totalSteps) currentStep.value++
}

const prevStep = () => {
  if (currentStep.value > 1) currentStep.value--
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const options: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString('id-ID', options)
}

const submitSurvey = async () => {
  isSubmitting.value = true
  try {
    const students = cartStore.activeStudent 
      ? [{ student_id: cartStore.activeStudent }] 
      : [] 

    // Ensure we have active student
    if (!students.length) {
       alertStore.error('Pilih siswa terlebih dahulu', 'Gagal')
       return
    }

    const payload = {
      web_item_code: webItemCode.value,
      date: formData.value.date,
      time: formData.value.time,
      address: {
        full_address: formData.value.full_address,
        province: formData.value.province,
        city: formData.value.city,
        subdistrict: formData.value.subdistrict,
        village: formData.value.village,
         postal_code: formData.value.postal_code
      },
      students: students
    }

    const response = await call('/api/method/webshop.webshop.api.survey.create_survey_request', payload)
    
    router.replace(`/products/${response.web_item_route}`)

  } catch (error) {
    alertStore.error('Terjadi kesalahan sistem', 'Error')
  } finally {
    isSubmitting.value = false
  }
}
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
