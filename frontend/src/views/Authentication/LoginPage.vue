<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- Content Card -->
      <div class="bg-white rounded-2xl shadow-lg p-8 md:p-12 relative">
        <!-- Close Button -->
        <router-link
          to="/"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 transition-colors z-10"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </router-link>

        <!-- Header -->
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Masuk ke Akun</h2>
          <p class="text-gray-600">Silakan masukkan email dan kata sandi Anda</p>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleLogin">
          <!-- Email Field -->
          <div class="mb-6">
            <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              id="email"
              v-model="email"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
              placeholder="contoh@email.com"
            />
          </div>

          <!-- Password Field -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2">
              <label for="password" class="block text-sm font-medium text-gray-700">Kata Sandi</label>
              <router-link to="/forgot-password" class="text-sm text-primary hover:underline">Lupa kata sandi?</router-link>
            </div>
            <div class="relative">
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition pr-12"
                placeholder="••••••••"
                @keyup.enter="handleLogin"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
              >
                <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="isLoggingIn"
            class="w-full bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors flex items-center justify-center disabled:opacity-50"
          >
            <svg
              v-if="isLoggingIn"
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
            <span v-if="isLoggingIn">Memproses...</span>
            <span v-else>Masuk</span>
          </button>

          <!-- Divider -->
          <div class="my-6 flex items-center">
            <div class="flex-1 border-t border-gray-300"></div>
            <span class="px-4 text-gray-500 text-sm">atau</span>
            <div class="flex-1 border-t border-gray-300"></div>
          </div>

          <!-- Register Link -->
          <div class="text-center text-sm text-gray-600">
            Belum punya akun?
            <router-link
              to="/register"
              class="text-primary font-semibold hover:underline"
            >
              Daftar di sini
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const isLoggingIn = ref(false)

// Check for success message from registration
onMounted(() => {
  if (route.query.registered === 'true') {
    successMessage.value = 'Pendaftaran berhasil! Silakan masuk dengan akun Anda.'
  }
})

const handleLogin = async () => {
  errorMessage.value = ''
  isLoggingIn.value = true

  try {
    const result = await authStore.login(email.value, password.value)

    if (result.success) {
      // Redirect to home or intended page
      const redirectTo = (route.query.redirect as string) || '/'
      router.push(redirectTo)
    } else {
      errorMessage.value = result.message || 'Email atau kata sandi salah'
    }
  } catch (error) {
    errorMessage.value = 'Terjadi kesalahan saat login. Silakan coba lagi.'
    console.error('Login error:', error)
  } finally {
    isLoggingIn.value = false
  }
}
</script>
