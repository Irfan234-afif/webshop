<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Buat Akun Wali Murid</h2>
      </div>
      <p class="text-gray-600">
        Daftarkan akun wali untuk mengelola pesanan, layanan sekolah, dan kebutuhan anak dalam satu sistem terpadu.
      </p>
    </div>

    <!-- Progress Bar for Step 1 -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 33.33%"></div>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleNext">
      <!-- Nama Lengkap -->
      <div class="mb-6">
        <label for="name" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Nama Lengkap
        </label>
        <input id="name" v-model="formData.name" type="text" required
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
          placeholder="Nama Lengkap" />
      </div>

      <!-- Email Sekolah -->
      <div class="mb-6">
        <label for="email" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Email Sekolah
        </label>
        <input id="email" v-model="formData.email" type="email" required @blur="registrationStore.validateEmail()"
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
          placeholder="Email Sekolah" />
        <div v-if="emailError" class="mt-2 text-red-500 text-sm">{{ emailError }}</div>
      </div>

      <!-- No. HP -->
      <div class="mb-6">
        <label for="phone" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          No. HP
        </label>
        <input id="phone" v-model="formData.phoneNumber" type="tel" required
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
          placeholder="No. HP" />
      </div>

      <!-- Password -->
      <div class="mb-6">
        <label for="password" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Password
        </label>
        <div class="relative">
          <input id="password" v-model="formData.password" :type="showPassword ? 'text' : 'password'" required
            @input="registrationStore.validatePasswordMatch()"
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition pr-12"
            placeholder="Password" />
          <button type="button" @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700">
            <svg v-if="!showPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Konfirmasi Password -->
      <div class="mb-8">
        <label for="confirmPassword" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
          <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          Konfirmasi Password
        </label>
        <div class="relative">
          <input id="confirmPassword" v-model="formData.confirmPassword"
            :type="showConfirmPassword ? 'text' : 'password'" required
            @input="registrationStore.validatePasswordMatch()"
            class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition pr-12"
            placeholder="Konfirmasi Password" />
          <button type="button" @click="showConfirmPassword = !showConfirmPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700">
            <svg v-if="!showConfirmPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
        <div v-if="passwordError" class="mt-2 text-red-500 text-sm">{{ passwordError }}</div>
      </div>

      <!-- Submit Button -->
      <button type="submit" :disabled="!isStep1Valid"
        class="w-full bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        Isi Data Siswa
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRegistrationStore } from '@/stores/registration'

const registrationStore = useRegistrationStore()

const formData = computed(() => registrationStore.formData)
const emailError = computed(() => registrationStore.emailError)
const passwordError = computed(() => registrationStore.passwordError)
const isStep1Valid = computed(() => registrationStore.isStep1Valid)

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const handleNext = () => {
  if (isStep1Valid.value) {
    registrationStore.nextStep()
  }
}
</script>
