<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- Content Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative">
        <!-- Header -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">
            Reset Kata Sandi
          </h2>
          <p class="text-gray-600">
            Silakan buat kata sandi baru Anda
          </p>
        </div>

        <!-- Missing Key State -->
        <div v-if="!hasKey" class="text-center">
            <div class="mb-4 p-4 bg-yellow-50 text-yellow-700 rounded-lg">
                Link tidak valid atau kadaluarsa. Pastikan Anda menggunakan link dari email reset kata sandi.
            </div>
            <router-link to="/login" class="text-primary font-semibold hover:underline">
                Kembali ke Login
            </router-link>
        </div>

        <!-- Form (Only shown if key exists) -->
        <form v-else @submit.prevent="handleSubmit">
          
          <!-- New Password Field -->
          <div class="mb-6">
            <label for="new_password" class="block text-sm font-medium text-gray-700 mb-2">Kata Sandi Baru</label>
            <div class="relative">
              <input
                id="new_password"
                v-model="newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition pr-12"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <svg v-if="!showNewPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
            <!-- Simple password strength hint -->
             <p class="text-xs text-gray-500 mt-1">Gunakan kombinasi huruf, angka, dan simbol.</p>
          </div>

          <!-- Confirm Password Field -->
          <div class="mb-6">
            <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">Konfirmasi Kata Sandi</label>
            <div class="relative">
              <input
                id="confirm_password"
                v-model="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition pr-12"
                placeholder="••••••••"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <svg v-if="!showConfirmPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
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
            :disabled="isLoading"
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
            <span v-else>Reset Kata Sandi</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const newPassword = ref('')
const confirmPassword = ref('')

const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

// Check if we are in reset mode (key query param exists)
const hasKey = computed(() => !!route.query.key)

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Konfirmasi kata sandi tidak cocok.'
    return
  }

  if (newPassword.value.length < 5) {
     errorMessage.value = 'Kata sandi harus minimal 5 karakter.'
     return
  }

  isLoading.value = true

  try {
    const key = route.query.key as string
    
    // Call API with key only (updateUserPassword handles this)
    const result = await authStore.updateUserPassword(
      newPassword.value,
      key
    )

    if (result.success) {
      successMessage.value = result.message || 'Kata sandi berhasil direset.'
      // Redirect to login after a delay
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    } else {
      errorMessage.value = result.message || 'Gagal mereset kata sandi.'
    }
  } catch (error) {
    errorMessage.value = 'Terjadi kesalahan sistem. Silakan coba lagi.'
    console.error('Update password error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>
