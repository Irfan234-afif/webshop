<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <span class="text-xl font-bold text-white">2</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Data Siswa</h2>
      </div>
      <p class="text-gray-600">
        Masukkan data siswa untuk menghubungkan layanan sekolah seperti seminar, buku, catering, dan antar jemput.
      </p>
    </div>

    <!-- Progress Bar for Step 2 -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 66.66%"></div>
      </div>
    </div>

    <!-- Student List -->
    <div class="mb-6">
      <div
        v-for="(student, index) in formData.students"
        :key="index"
        class="mb-8"
      >
        <!-- Student Header -->
        <div class="bg-white border border-gray-200 rounded-xl p-6">
          <div class="flex items-start gap-3 mb-4">
            <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
              <span class="text-lg font-bold text-white">{{ index + 1 }}</span>
            </div>
            <div class="flex-1">
              <h3 class="font-bold text-gray-900 text-lg mb-1">Data Siswa {{ index + 1 }}</h3>
              <p class="text-sm text-gray-600">
                Isi identitas siswa pertama yang akan terhubung dengan akun wali dan dipantau dalam layanan sekolah.
              </p>
            </div>
          </div>

          <!-- Student Fields -->
          <div class="space-y-4">
            <!-- NIS/NISN -->
            <div>
              <input
                :id="`nisn_${index}`"
                v-model="student.nisn"
                type="text"
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="NIS / NISN"
              />
            </div>

            <!-- Nama Anak -->
            <div>
              <input
                :id="`student_name_${index}`"
                v-model="student.student_name"
                type="text"
                required
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="Nama Anak"
              />
            </div>

            <!-- Unit -->
            <div>
              <select
                :id="`school_unit_${index}`"
                v-model="student.school_unit"
                required
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition appearance-none"
              >
                <option value="" disabled>Unit</option>
                <option value="SD">SD (Sekolah Dasar)</option>
                <option value="SMP">SMP (Sekolah Menengah Pertama)</option>
                <option value="SMA">SMA (Sekolah Menengah Atas)</option>
                <option value="SMK">SMK (Sekolah Menengah Kejuruan)</option>
              </select>
            </div>

            <!-- Kelas -->
            <div>
              <input
                :id="`grade_level_${index}`"
                v-model="student.grade_level"
                type="text"
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition"
                placeholder="Kelas"
              />
            </div>

            <!-- Date of Birth (hidden in Figma but keeping for data integrity) -->
            <input
              :id="`dob_${index}`"
              v-model="student.date_of_birth"
              type="date"
              class="hidden"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Tambah Anak Button -->
    <button
      @click="registrationStore.addStudent()"
      class="w-full mb-8 flex items-center justify-center gap-2 py-4 px-6 border-2 border-dashed border-gray-300 rounded-xl text-primary font-medium hover:border-primary hover:bg-pink-50 transition-all"
    >
      <div class="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </div>
      Tambah Anak
    </button>

    <!-- Navigation Buttons -->
    <div class="flex gap-4">
      <button
        @click="registrationStore.prevStep()"
        class="flex-1 border-2 border-primary text-primary font-bold py-4 px-6 rounded-xl hover:bg-pink-50 transition-colors"
      >
        Kembali
      </button>
      <button
        @click="handleNext"
        :disabled="!isStep2Valid"
        class="flex-1 bg-gray-700 text-white font-bold py-4 px-6 rounded-xl hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Konfirmasi Data
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRegistrationStore } from '@/stores/registration'

const registrationStore = useRegistrationStore()

const formData = computed(() => registrationStore.formData)
const isStep2Valid = computed(() => registrationStore.isStep2Valid)

const handleNext = () => {
  if (isStep2Valid.value) {
    registrationStore.nextStep()
  }
}
</script>
