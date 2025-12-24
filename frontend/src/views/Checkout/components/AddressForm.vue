<template>
  <div class="address-form p-6">
    <div class="mb-6">
      <h3 class="text-lg font-semibold text-gray-900 mb-2">Lengkapi Alamat Pengiriman</h3>
      <p class="text-sm text-gray-600">
        Kami memerlukan alamat Anda untuk mengirimkan pesanan. Alamat ini akan digunakan sebagai alamat pengiriman dan penagihan.
      </p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Address Title -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Nama Alamat <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.address_title"
          type="text"
          placeholder="Contoh: Rumah, Kantor"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          required
        />
      </div>

      <!-- Phone -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Nomor Telepon <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.phone"
          type="tel"
          placeholder="Contoh: 08123456789 atau +6281234567890"
          pattern="^(\+62|62|0)[0-9]{9,12}$"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          required
        />
        <p class="text-xs text-gray-500 mt-1">
          Format: 08xxxxxxxxxx atau +628xxxxxxxxxx
        </p>
      </div>

      <!-- Full Address -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Alamat Lengkap <span class="text-red-500">*</span>
        </label>
        <textarea
          v-model="form.address_line1"
          rows="3"
          placeholder="Jalan, nomor rumah, RT/RW, Kelurahan, Kecamatan"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          required
        ></textarea>
      </div>

      <!-- City -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Kota <span class="text-red-500">*</span>
        </label>
        <input
          v-model="form.city"
          type="text"
          placeholder="Contoh: Jakarta, Tangerang Selatan"
          class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
          required
        />
      </div>

      <!-- Error Message -->
      <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800 text-sm">{{ error }}</p>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        class="w-full px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-opacity-90 transition-all duration-200 disabled:bg-gray-300 disabled:cursor-not-allowed"
        :disabled="isLoading"
      >
        {{ isLoading ? 'Menyimpan...' : 'Simpan Alamat & Lanjutkan' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { createAddress } from '@/utils/checkoutApi'

interface Props {
  studentName: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  addressCreated: []
}>()

const form = ref({
  address_title: '',
  address_line1: '',
  city: '',
  phone: ''
})

const isLoading = ref(false)
const error = ref<string>('')

async function handleSubmit() {
  isLoading.value = true
  error.value = ''

  try {
    console.log('🔍 Creating address for student:', props.studentName)

    await createAddress({
      address_title: form.value.address_title,
      address_line1: form.value.address_line1,
      city: form.value.city,
      phone: form.value.phone,
      student_name: props.studentName
    })

    console.log('✅ Address created successfully for student:', props.studentName)
    emit('addressCreated')
  } catch (err: any) {
    // Extract error message from Frappe API response
    let errorMessage = 'Gagal menyimpan alamat. Silakan coba lagi.'

    if (err.messages && err.messages.length > 0) {
      // Frappe API error format
      errorMessage = err.messages[0]
    } else if (err.message) {
      errorMessage = err.message
    } else if (err.exception) {
      // Extract from exception string
      const match = err.exception.match(/: (.+)$/)
      if (match) {
        errorMessage = match[1]
      }
    }

    error.value = errorMessage
    console.error('❌ Failed to create address:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.address-form {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
