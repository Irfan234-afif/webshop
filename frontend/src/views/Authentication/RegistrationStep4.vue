<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <span class="text-xl font-bold text-white">4</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Konfirmasi Data</h2>
      </div>
      <p class="text-gray-600">
        Masukkan data siswa untuk menghubungkan layanan sekolah seperti seminar, buku, catering, dan antar jemput.
      </p>
    </div>

    <!-- Progress Bar for Step 3 -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 100%"></div>
      </div>
    </div>

    <!-- Account Information -->
    <div class="mb-6 bg-white border border-gray-200 rounded-xl p-6">
      <h3 class="font-bold text-gray-900 mb-4">Akun</h3>
      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Nama Lengkap</span>
          <span class="text-gray-900 font-medium">{{ formData.name }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Email Sekolah</span>
          <span class="text-gray-900 font-medium">{{ formData.email }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-600">No. HP</span>
          <span class="text-gray-900 font-medium">{{ formData.phoneNumber }}</span>
        </div>
      </div>
    </div>

    <!-- Student Information -->
    <div v-for="(student, index) in formData.students" :key="index"
      class="mb-6 bg-white border border-gray-200 rounded-xl p-6">
      <h3 class="font-bold text-gray-900 mb-4">Data Siswa {{ index + 1 }}</h3>
      <div class="space-y-3">
        <div class="flex justify-between items-center">
          <span class="text-gray-600">NIS / NISN</span>
          <span class="text-gray-900 font-medium">{{ student.nisn || '-' }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Nama Anak</span>
          <span class="text-gray-900 font-medium">{{ student.student_name }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Unit</span>
          <span class="text-gray-900 font-medium">{{ getSchoolUnitLabel(student.school_unit) }}</span>
        </div>
        <div class="flex justify-between items-center">
          <span class="text-gray-600">Kelas</span>
          <span class="text-gray-900 font-medium">{{ student.grade_level || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- Terms and Conditions Checkbox -->
    <div class="mb-8">
      <label class="flex items-center gap-3 cursor-pointer py-2">
        <input v-model="agreedToTerms" type="checkbox"
          class="w-5 h-5 text-primary border-gray-300 rounded focus:ring-2 focus:ring-primary" />
        <span class="text-sm text-gray-600">
          Saya telah menyetujui
          <a href="#" class="text-primary hover:underline font-medium">Syarat & Ketentuan</a>
          serta
          <a href="#" class="text-primary hover:underline font-medium">Kebijakan Privasi</a>
          tersebut koperasi ini
        </span>
      </label>
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
      <p class="text-red-600 text-sm">{{ errorMessage }}</p>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex gap-4">
      <button @click="registrationStore.prevStep()" :disabled="isRegistering"
        class="flex-1 border-2 border-primary text-primary font-bold py-4 px-6 rounded-xl hover:bg-pink-50 transition-colors disabled:opacity-50">
        Kembali
      </button>
      <button @click="handleSubmit" :disabled="!agreedToTerms || isRegistering"
        class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
        <svg v-if="isRegistering" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
          fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
          </path>
        </svg>
        <span v-if="isRegistering">Memproses...</span>
        <span v-else>Daftarkan Akun</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRegistrationStore } from '@/stores/registration'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const registrationStore = useRegistrationStore()
const authStore = useAuthStore()

const formData = computed(() => registrationStore.formData)
const isRegistering = computed(() => registrationStore.isRegistering)

const agreedToTerms = ref(false)
const errorMessage = ref('')

const getSchoolUnitLabel = (unit: string): string => {
  const labels: Record<string, string> = {
    'SD': 'SD (Sekolah Dasar)',
    'SMP': 'SMP (Sekolah Menengah Pertama)',
    'SMA': 'SMA (Sekolah Menengah Atas)',
    'SMK': 'SMK (Sekolah Menengah Kejuruan)'
  }
  return labels[unit] || unit
}

const handleSubmit = async () => {
  if (!agreedToTerms.value) {
    errorMessage.value = 'Anda harus menyetujui Syarat & Ketentuan dan Kebijakan Privasi'
    return
  }

  errorMessage.value = ''

  const result = await registrationStore.submitRegistration()

  if (result.success) {
    // Redirect to login page with success message
    router.push({ path: '/login', query: { registered: 'true' } })
  } else {
    errorMessage.value = result.message || 'Terjadi kesalahan saat pendaftaran. Silakan coba lagi.'
  }
}
</script>
