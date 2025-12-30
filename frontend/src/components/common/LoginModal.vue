<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div 
      class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
      @click="emit('close')"
    ></div>

    <!-- Modal Content -->
    <div 
      class="relative bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden z-10 transform transition-transform"
      @click.stop
    >
      <!-- Close Button -->
      <button
        @click="emit('close')"
        class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-20"
        aria-label="Close"
      >
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      <!-- Modal Body -->
      <div class="p-8">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Masuk ke Akun</h2>
          <p class="text-gray-600">Silakan masukkan email dan kata sandi Anda</p>
        </div>

        <form @submit.prevent="handleLogin">
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

          <!-- Password Field -->
          <div class="mb-6">
            <div class="flex items-center justify-between mb-2">
              <label for="password" class="block text-sm font-medium text-gray-700">Kata Sandi</label>
              <a href="/forgot-password" class="text-sm text-primary hover:underline">Lupa kata sandi?</a>
            </div>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
              placeholder="••••••••"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="mb-4 text-red-500 text-sm text-center">
            {{ errorMessage }}
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="isLoggingIn"
            class="w-full bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors flex items-center justify-center"
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
            <button
              @click="showRegistration"
              class="text-primary font-semibold hover:underline"
            >
              Daftar di sini
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits<{
  close: []
  loginSuccess: []
  showRegistrationModal: []
}>()

const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoggingIn = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  isLoggingIn.value = true

  try {
    const result = await authStore.login(email.value, password.value)
    
    if (result.success) {
      emit('loginSuccess')
      emit('close')
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

// Method to navigate to registration page
const showRegistration = () => {
  emit('close')
  router.push('/register')
}
</script>