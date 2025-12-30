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

      <!-- Progress Bar -->
      <div class="pt-8 px-8">
        <div class="flex items-center justify-between mb-6">
          <div 
            v-for="n in totalSteps" 
            :key="n" 
            class="flex flex-col items-center"
          >
            <div 
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium',
                n <= currentStep ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500'
              ]"
            >
              {{ n }}
            </div>
            <div 
              :class="[
                'mt-2 w-16 h-1',
                n < currentStep ? 'bg-primary' : 'bg-gray-200'
              ]"
              v-if="n < totalSteps"
            ></div>
          </div>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-8">
        <!-- Step 1: General/Parent Information -->
        <div v-if="currentStep === 1">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Daftar Akun</h2>
          <p class="text-gray-600 mb-8">Silakan masukkan informasi Anda</p>

          <form @submit.prevent="nextStep">
            <!-- Name Field -->
            <div class="mb-6">
              <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Nama Lengkap</label>
              <input
                id="name"
                v-model="formData.name"
                type="text"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="Nama lengkap Anda"
              />
            </div>

            <!-- Email Field -->
            <div class="mb-6">
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email</label>
              <input
                id="email"
                v-model="formData.email"
                type="email"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="contoh@email.com"
              />
              <div v-if="emailError" class="mt-1 text-red-500 text-sm">{{ emailError }}</div>
            </div>

            <!-- Phone Number Field -->
            <div class="mb-6">
              <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">Nomor Telepon</label>
              <input
                id="phone"
                v-model="formData.phoneNumber"
                type="tel"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="+6281234567890"
              />
            </div>

            <!-- Password Field -->
            <div class="mb-6">
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">Kata Sandi</label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="••••••••"
              />
            </div>

            <!-- Confirm Password Field -->
            <div class="mb-6">
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">Konfirmasi Kata Sandi</label>
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                type="password"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="••••••••"
              />
              <div v-if="passwordError" class="mt-1 text-red-500 text-sm">{{ passwordError }}</div>
            </div>

            <!-- Next Button -->
            <button
              type="submit"
              :disabled="!isStep1Valid"
              class="w-full bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Lanjutkan
            </button>
          </form>
        </div>

        <!-- Step 2: Student Information -->
        <div v-else-if="currentStep === 2">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Informasi Siswa</h2>
          <p class="text-gray-600 mb-8">Silakan masukkan informasi siswa</p>

          <!-- Student List -->
          <div class="mb-6">
            <div 
              v-for="(student, index) in formData.students" 
              :key="index"
              class="mb-6 p-4 border border-gray-200 rounded-lg"
            >
              <div class="flex justify-between items-center mb-3">
                <h3 class="font-medium text-gray-800">Siswa {{ index + 1 }}</h3>
                <button 
                  v-if="formData.students.length > 1"
                  @click="removeStudent(index)"
                  class="text-red-500 hover:text-red-700"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
              
              <div class="grid grid-cols-1 gap-4">
                <!-- Student Name -->
                <div>
                  <label :for="`student_name_${index}`" class="block text-sm font-medium text-gray-700 mb-2">Nama Siswa</label>
                  <input
                    :id="`student_name_${index}`"
                    v-model="student.student_name"
                    type="text"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                    :placeholder="`Nama siswa ke-${index + 1}`"
                  />
                </div>

                <!-- School Unit -->
                <div>
                  <label :for="`school_unit_${index}`" class="block text-sm font-medium text-gray-700 mb-2">Unit Sekolah</label>
                  <select
                    :id="`school_unit_${index}`"
                    v-model="student.school_unit"
                    required
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                  >
                    <option value="" disabled>Pilih Unit Sekolah</option>
                    <option value="SD">Sekolah Dasar (SD)</option>
                    <option value="SMP">Sekolah Menengah Pertama (SMP)</option>
                    <option value="SMA">Sekolah Menengah Atas (SMA)</option>
                    <option value="SMK">Sekolah Menengah Kejuruan (SMK)</option>
                  </select>
                </div>

                <!-- Grade Level -->
                <div>
                  <label :for="`grade_level_${index}`" class="block text-sm font-medium text-gray-700 mb-2">Tingkat Kelas</label>
                  <select
                    :id="`grade_level_${index}`"
                    v-model="student.grade_level"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                  >
                    <option value="" disabled>Pilih Tingkat Kelas</option>
                    <option value="Kelas 1">Kelas 1</option>
                    <option value="Kelas 2">Kelas 2</option>
                    <option value="Kelas 3">Kelas 3</option>
                    <option value="Kelas 4">Kelas 4</option>
                    <option value="Kelas 5">Kelas 5</option>
                    <option value="Kelas 6">Kelas 6</option>
                    <option value="Kelas 7">Kelas 7</option>
                    <option value="Kelas 8">Kelas 8</option>
                    <option value="Kelas 9">Kelas 9</option>
                    <option value="Kelas 10">Kelas 10</option>
                    <option value="Kelas 11">Kelas 11</option>
                    <option value="Kelas 12">Kelas 12</option>
                  </select>
                </div>

                <!-- Date of Birth -->
                <div>
                  <label :for="`dob_${index}`" class="block text-sm font-medium text-gray-700 mb-2">Tanggal Lahir</label>
                  <input
                    :id="`dob_${index}`"
                    v-model="student.date_of_birth"
                    type="date"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                  />
                </div>
                
                <!-- NISN -->
                <div>
                  <label :for="`nisn_${index}`" class="block text-sm font-medium text-gray-700 mb-2">NISN (Nomor Induk Siswa Nasional)</label>
                  <input
                    :id="`nisn_${index}`"
                    v-model="student.nisn"
                    type="text"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                    placeholder="Nomor Induk Siswa Nasional"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Add Student Button -->
          <button
            @click="addStudent"
            class="w-full border border-dashed border-gray-300 text-gray-500 font-medium py-3 px-4 rounded-lg hover:border-primary hover:text-primary transition-colors mb-6"
          >
            + Tambah Siswa
          </button>

          <!-- Navigation Buttons -->
          <div class="flex gap-3">
            <button
              @click="prevStep"
              class="flex-1 border border-gray-300 text-gray-700 font-bold py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors"
            >
              Kembali
            </button>
            <button
              @click="nextStep"
              :disabled="!isStep2Valid"
              class="flex-1 bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Lanjutkan
            </button>
          </div>
        </div>

        <!-- Step 3: Confirmation -->
        <div v-else-if="currentStep === 3">
          <h2 class="text-2xl font-bold text-gray-900 mb-2">Konfirmasi Pendaftaran</h2>
          <p class="text-gray-600 mb-8">Silakan periksa kembali informasi Anda</p>

          <!-- Parent Information Summary -->
          <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 class="font-medium text-gray-800 mb-3">Informasi Orang Tua/Wali</h3>
            <div class="space-y-2 text-sm">
              <p><span class="font-medium">Nama:</span> {{ formData.name }}</p>
              <p><span class="font-medium">Email:</span> {{ formData.email }}</p>
              <p><span class="font-medium">Telepon:</span> {{ formData.phoneNumber }}</p>
            </div>
          </div>

          <!-- Student Information Summary -->
          <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 class="font-medium text-gray-800 mb-3">Informasi Siswa</h3>
            <div v-for="(student, index) in formData.students" :key="index" class="mb-3 last:mb-0">
              <p class="font-medium">Siswa {{ index + 1 }}</p>
              <div class="ml-3 space-y-1 text-sm">
                <p>Nama: {{ student.student_name }}</p>
                <p>Unit Sekolah: {{ student.school_unit }}</p>
                <p>Kelas: {{ student.grade_level || 'Belum ditentukan' }}</p>
                <p>Tanggal Lahir: {{ student.date_of_birth || 'Belum ditentukan' }}</p>
                <p>NISN: {{ student.nisn || 'Belum ditentukan' }}</p>
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="flex gap-3">
            <button
              @click="prevStep"
              class="flex-1 border border-gray-300 text-gray-700 font-bold py-3 px-4 rounded-xl hover:bg-gray-50 transition-colors"
            >
              Kembali
            </button>
            <button
              @click="submitRegistration"
              :disabled="isRegistering"
              class="flex-1 bg-primary text-white font-bold py-3 px-4 rounded-xl hover:bg-[#8B1A73] transition-colors flex items-center justify-center disabled:opacity-50"
            >
              <svg
                v-if="isRegistering"
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
              <span v-if="isRegistering">Memproses...</span>
              <span v-else>Daftar</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits<{
  close: []
  registerSuccess: []
}>()

const authStore = useAuthStore()
const currentStep = ref(1)
const totalSteps = 3
const isRegistering = ref(false)
const emailError = ref('')
const passwordError = ref('')

// Form data
const formData = ref({
  name: '',
  email: '',
  phoneNumber: '',
  password: '',
  confirmPassword: '',
  students: [
    {
      student_name: '',
      school_unit: '',
      grade_level: '',
      date_of_birth: '',
      nisn: ''
    }
  ]
})

// Validate email function
const validateEmail = async () => {
  if (!formData.value.email) {
    emailError.value = ''
    return
  }

  // Basic email format validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(formData.value.email)) {
    emailError.value = 'Format email tidak valid'
    return
  }

  // Check email availability via API
  try {
    const response = await fetch(`/api/method/webshop.webshop.api.auth.check_email_availability?email=${formData.value.email}`)
    const data = await response.json()

    if (!data.message.success || !data.message.available) {
      emailError.value = data.message.message || 'Email sudah terdaftar'
    } else {
      emailError.value = ''
    }
  } catch (error) {
    console.error('Error checking email availability:', error)
    emailError.value = 'Terjadi kesalahan saat memeriksa email'
  }
}

// Watch email changes to validate in real-time
const watchEmail = () => {
  if (formData.value.email) {
    // Debounce the email validation
    setTimeout(validateEmail, 500)
  } else {
    emailError.value = ''
  }
}

// Watch for password match
const watchPassword = () => {
  if (formData.value.password !== formData.value.confirmPassword) {
    passwordError.value = 'Kata sandi tidak cocok'
  } else {
    passwordError.value = ''
  }
}

// Watch for email changes
watch(() => formData.value.email, watchEmail)

// Watch for password changes to validate match
watch(() => [formData.value.password, formData.value.confirmPassword], watchPassword)

// Validation
const isStep1Valid = computed(() => {
  return (
    formData.value.name.trim() !== '' &&
    formData.value.email.trim() !== '' &&
    formData.value.phoneNumber.trim() !== '' &&
    formData.value.password.trim() !== '' &&
    formData.value.password === formData.value.confirmPassword &&
    !emailError.value
  )
})

const isStep2Valid = computed(() => {
  return formData.value.students.every(student =>
    student.student_name.trim() !== '' &&
    student.school_unit.trim() !== ''
  )
})

// Methods
const nextStep = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const addStudent = () => {
  formData.value.students.push({
    student_name: '',
    school_unit: '',
    grade_level: '',
    date_of_birth: '',
    nisn: ''
  })
}

const removeStudent = (index: number) => {
  if (formData.value.students.length > 1) {
    formData.value.students.splice(index, 1)
  }
}

// Submit registration
const submitRegistration = async () => {
  isRegistering.value = true
  emailError.value = ''
  passwordError.value = ''

  try {
    // Prepare registration data
    const registrationData = {
      name: formData.value.name,
      email: formData.value.email,
      phone_number: formData.value.phoneNumber,
      password: formData.value.password,
      students: formData.value.students
    }

    // Call registration API
    const response = await fetch('/api/method/webshop.webshop.api.auth.register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(registrationData)
    })

    const result = await response.json()

    if (result.message.success) {
      // Registration successful
      emit('registerSuccess')
      emit('close')
    } else {
      // Handle error from API
      emailError.value = result.message.message || 'Terjadi kesalahan saat pendaftaran'
    }
  } catch (error) {
    console.error('Registration error:', error)
    emailError.value = 'Terjadi kesalahan saat pendaftaran. Silakan coba lagi.'
  } finally {
    isRegistering.value = false
  }
}
</script>