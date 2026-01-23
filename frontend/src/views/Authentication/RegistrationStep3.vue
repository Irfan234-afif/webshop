<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <span class="text-xl font-bold text-white">3</span>
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
        <div class="h-full bg-primary transition-all duration-300" style="width: 75%"></div>
      </div>
    </div>

    <!-- Student List -->
    <div class="mb-6">
      <div v-for="(student, index) in formData.students" :key="index" class="mb-8">
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
              <FormInput :id="`nisn_${index}`" v-model="student.nisn" type="text" placeholder="NIS / NISN" />
            </div>

            <!-- Nama Anak -->
            <div>
              <FormInput :id="`student_name_${index}`" v-model="student.student_name" type="text"
                placeholder="Nama Anak" />
            </div>

            <!-- Unit -->
            <div>
              <FormSelect :id="`school_unit_${index}`" v-model="student.school_unit">
                <option value="" disabled>{{ isLoadingUnits ? 'Memuat...' : 'Pilih Unit' }}</option>
                <option v-for="unit in schoolUnits" :key="unit.name" :value="unit.name">
                  {{ unit.unit_name || unit.name }}
                </option>
              </FormSelect>
            </div>

            <!-- Kelas -->
            <div>
              <FormSelect :id="`grade_level_${index}`" v-model="student.grade_level">
                <option value="" disabled>
                  {{ !student.school_unit ? 'Pilih Unit terlebih dahulu' : isLoadingGrades ? 'Memuat...' : 'Pilih Kelas'
                  }}
                </option>
                <option v-for="grade in getGradesForStudent(index)" :key="grade.name" :value="grade.name">
                  {{ grade.grade_name }}
                </option>
              </FormSelect>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Tambah Anak Button -->
    <button @click="registrationStore.addStudent()"
      class="w-full mb-8 flex items-center justify-center gap-2 py-4 px-6 border-2 border-dashed border-gray-300 rounded-xl text-primary font-medium hover:border-primary hover:bg-pink-50 transition-all">
      <div class="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </div>
      Tambah Anak
    </button>

    <!-- Navigation Buttons -->
    <div class="flex gap-4">
      <button @click="registrationStore.prevStep()"
        class="flex-1 border-2 border-primary text-primary font-bold py-4 px-6 rounded-xl hover:bg-pink-50 transition-colors">
        Kembali
      </button>
      <button @click="handleNext" :disabled="!isStep3Valid"
        class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        Konfirmasi Data
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRegistrationStore } from '@/stores/registration'
import { frappeRequest } from 'frappe-ui'
import FormInput from '@/components/common/FormInput.vue'
import FormSelect from '@/components/common/FormSelect.vue'

const registrationStore = useRegistrationStore()

const formData = computed(() => registrationStore.formData)
const isStep3Valid = computed(() => registrationStore.isStep3Valid)

// State for school units and grades
const schoolUnits = ref<{ name: string; unit_name: string; unit_code: string }[]>([])
const allGrades = ref<{ name: string; grade_name: string; school_unit: string }[]>([])
const isLoadingUnits = ref(false)
const isLoadingGrades = ref(false)

// Fetch school units from API
const fetchSchoolUnits = async () => {
  isLoadingUnits.value = true
  try {
    const response = await frappeRequest({
      url: 'webshop.webshop.api.products.get_school_units',
      method: 'GET'
    })
    schoolUnits.value = response || []
  } catch (error) {
    console.error('Error fetching school units:', error)
  } finally {
    isLoadingUnits.value = false
  }
}

// Fetch all grades from API
const fetchGrades = async () => {
  isLoadingGrades.value = true
  try {
    const response = await frappeRequest({
      url: 'webshop.webshop.api.products.get_grades',
      method: 'GET'
    })
    allGrades.value = response || []
  } catch (error) {
    console.error('Error fetching grades:', error)
  } finally {
    isLoadingGrades.value = false
  }
}

// Get filtered grades for a specific student based on their selected school unit
const getGradesForStudent = (studentIndex: number) => {
  const selectedUnit = formData.value.students[studentIndex]?.school_unit
  if (!selectedUnit) {
    return []
  }
  return allGrades.value.filter(grade => grade.school_unit === selectedUnit)
}

// Handle school unit change - clear grade if it doesn't belong to new unit
const handleSchoolUnitChange = (studentIndex: number) => {
  const student = formData.value.students[studentIndex]
  if (!student) return

  if (student.school_unit && student.grade_level) {
    // Check if current grade belongs to the new school unit
    const gradeExists = allGrades.value.find(
      grade => grade.name === student.grade_level && grade.school_unit === student.school_unit
    )
    if (!gradeExists) {
      student.grade_level = ''
    }
  }
}

const handleNext = () => {
  if (isStep3Valid.value) {
    registrationStore.nextStep()
  }
}

// Fetch data on component mount
onMounted(() => {
  fetchSchoolUnits()
  fetchGrades()
})
</script>
