<template>
  <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
    <div class="p-6 border-b border-gray-100">
      <h2 class="text-xl font-bold text-gray-900">Keamanan Akun</h2>
      <p class="text-sm text-gray-500 mt-1">Perbarui kata sandi akun Anda</p>
    </div>

    <div class="p-6">
      <form @submit.prevent="handleSubmit">
        <!-- Old Password Field -->
        <div class="mb-6">
          <label for="old_password" class="block text-sm font-medium text-gray-700 mb-2">Kata Sandi Saat Ini</label>
          <div class="relative">
            <FormInput
              id="old_password"
              v-model="oldPassword"
              :type="showOldPassword ? 'text' : 'password'"
              required
              class="pr-12"
              placeholder="••••••••"
            />
            <button
              type="button"
              @click="showOldPassword = !showOldPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              <EyeSlashIcon v-if="!showOldPassword" class="w-5 h-5" />
              <EyeIcon v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- New Password Field -->
        <div class="mb-6">
          <label for="new_password" class="block text-sm font-medium text-gray-700 mb-2">Kata Sandi Baru</label>
          <div class="relative">
            <FormInput
              id="new_password"
              v-model="newPassword"
              :type="showNewPassword ? 'text' : 'password'"
              required
              class="pr-12"
              placeholder="••••••••"
            />
            <button
              type="button"
              @click="showNewPassword = !showNewPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              <EyeSlashIcon v-if="!showNewPassword" class="w-5 h-5" />
              <EyeIcon v-else class="w-5 h-5" />
            </button>
          </div>
          <p class="text-xs text-gray-500 mt-1">Gunakan kombinasi huruf, angka, dan simbol (min. 5 karakter).</p>
        </div>

        <!-- Confirm Password Field -->
        <div class="mb-8">
          <label for="confirm_password" class="block text-sm font-medium text-gray-700 mb-2">Konfirmasi Kata Sandi Baru</label>
          <div class="relative">
            <FormInput
              id="confirm_password"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              class="pr-12"
              placeholder="••••••••"
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              <EyeSlashIcon v-if="!showConfirmPassword" class="w-5 h-5" />
              <EyeIcon v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3">
          <XCircleIcon class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <p class="text-red-600 text-sm">{{ errorMessage }}</p>
        </div>

        <div v-if="successMessage" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3">
            <CheckCircleIcon class="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            <p class="text-green-600 text-sm">{{ successMessage }}</p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end">
          <PrimaryButton
            type="submit"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            {{ isLoading ? 'Menyimpan...' : 'Simpan Perubahan' }}
          </PrimaryButton>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { EyeIcon, EyeSlashIcon, XCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import FormInput from '@/components/common/FormInput.vue'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

const authStore = useAuthStore()

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

const showOldPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const errorMessage = ref('')
const successMessage = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  errorMessage.value = ''
  successMessage.value = ''
  
  if (newPassword.value !== confirmPassword.value) {
    errorMessage.value = 'Konfirmasi kata sandi baru tidak cocok.'
    return
  }

  if (newPassword.value.length < 5) {
     errorMessage.value = 'Kata sandi baru harus minimal 5 karakter.'
     return
  }

  isLoading.value = true

  try {
    const result = await authStore.updateUserPassword(
      newPassword.value,
      undefined,
      oldPassword.value
    )

    if (result.success) {
      successMessage.value = result.message || 'Kata sandi berhasil diperbarui.'
      // Reset form
      oldPassword.value = ''
      newPassword.value = ''
      confirmPassword.value = ''
    } else {
      errorMessage.value = result.message || 'Gagal memperbarui kata sandi.'
    }
  } catch (error) {
    errorMessage.value = 'Terjadi kesalahan sistem. Silakan coba lagi.'
  } finally {
    isLoading.value = false
  }
}
</script>
