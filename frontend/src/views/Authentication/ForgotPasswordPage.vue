<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- Content Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative">
        <!-- Close/Back Button -->
        <router-link
          to="/login"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition-colors z-10"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </router-link>

        <!-- Header -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Lupa Kata Sandi</h2>
          <p class="text-gray-600">Masukkan email Anda untuk menerima link reset kata sandi</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit">
          <!-- Email Field -->
          <div class="mb-6">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
              placeholder="contoh@email.com"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-600 text-sm">{{ errorMessage }}</p>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p class="text-green-600 text-sm">{{ successMessage }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading || !!successMessage"
            class="w-full bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors flex items-center justify-center disabled:opacity-50"
          >
            <svg
              v-if="isLoading"
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
            <span v-if="isLoading">Memproses...</span>
            <span v-else>Kirim Link Reset</span>
          </button>

          <!-- Back to Login Link -->
          <div class="mt-6 text-center text-sm text-gray-600">
            Kembali ke 
            <router-link
              to="/login"
              class="text-primary font-semibold hover:underline"
            >
              Halaman Login
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  isLoading.value = true

  try {
    const result = await authStore.forgotPassword(email.value)

    if (result.success) {
      successMessage.value = result.message || 'Link reset kata sandi telah dikirim ke email Anda.'
      // Clear email specifically if successful? Maybe keep it so they know where it went.
    } else {
      errorMessage.value = result.message || 'Gagal mengirim link reset kata sandi.'
    }
  } catch (error) {
    errorMessage.value = 'Terjadi kesalahan sistem. Silakan coba lagi.'
    console.error('Forgot password error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
