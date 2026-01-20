<template>
    <Teleport to="body">
        <Transition name="modal">
            <div v-if="isOpen" class="modal-overlay" @click="handleClose">
                <div class="modal-container" @click.stop>
                    <!-- Header -->
                    <div class="modal-header">
                        <h2 class="text-xl font-bold text-gray-900">
                            {{ isEditMode ? 'Edit Data Siswa' : 'Tambah Data Siswa' }}
                        </h2>
                        <button @click="handleClose" class="close-button">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                    d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <!-- Form Body -->
                    <div class="modal-body">
                        <form @submit.prevent="handleSubmit" class="space-y-5">
                            <!-- Student Name -->
                            <div>
                                <FormLabel icon="custom">
                                    <template #icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
                                        </svg>
                                    </template>
                                    Nama Siswa
                                </FormLabel>
                                <FormInput v-model="formData.studentName" type="text" placeholder="Masukkan nama siswa"
                                    required />
                            </div>

                            <!-- NIS/NISN -->
                            <div>
                                <FormLabel icon="custom">
                                    <template #icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z" />
                                        </svg>
                                    </template>
                                    NIS / NISN
                                </FormLabel>
                                <FormInput v-model="formData.nisn" type="text" placeholder="Masukkan NIS/NISN" />
                            </div>

                            <!-- School Unit -->
                            <div>
                                <FormLabel icon="custom">
                                    <template #icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                                        </svg>
                                    </template>
                                    Unit Sekolah
                                </FormLabel>
                                <select v-model="formData.schoolUnit" required
                                    class="w-full px-4 py-3 border rounded-lg text-sm text-gray-900 transition-all bg-gray-50 border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition disabled:opacity-50 disabled:cursor-not-allowed">
                                    <option value="" disabled>Pilih unit sekolah</option>
                                    <option v-for="unit in schoolUnits" :key="unit.value" :value="unit.value">
                                        {{ unit.label }}
                                    </option>
                                </select>
                            </div>

                            <!-- Grade Level -->
                            <div>
                                <FormLabel icon="custom">
                                    <template #icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                                        </svg>
                                    </template>
                                    Kelas
                                </FormLabel>
                                <select v-model="formData.gradeLevel" :disabled="!formData.schoolUnit"
                                    class="w-full px-4 py-3 border rounded-lg text-sm text-gray-900 transition-all bg-gray-50 border-gray-200 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition disabled:opacity-50 disabled:cursor-not-allowed">
                                    <option value="">{{ gradePlaceholder }}</option>
                                    <option v-for="grade in grades" :key="grade.value" :value="grade.value">
                                        {{ grade.label }}
                                    </option>
                                </select>
                            </div>

                            <!-- Date of Birth -->
                            <div>
                                <FormLabel icon="custom">
                                    <template #icon>
                                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                            stroke-width="1.5" stroke="currentColor" class="w-4 h-4 text-primary">
                                            <path stroke-linecap="round" stroke-linejoin="round"
                                                d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                                        </svg>
                                    </template>
                                    Tanggal Lahir
                                </FormLabel>
                                <FormInput v-model="formData.dateOfBirth" type="date" />
                            </div>
                        </form>
                    </div>

                    <!-- Actions -->
                    <div class="modal-footer">
                        <PrimaryButton variant="outline" class="flex-1" @click="handleClose" :disabled="isProcessing">
                            Batal
                        </PrimaryButton>
                        <PrimaryButton class="flex-1" @click="handleSubmit" :disabled="!canSubmit || isProcessing">
                            <span v-if="isProcessing" class="flex items-center gap-2">
                                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                        stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                    </path>
                                </svg>
                                Menyimpan...
                            </span>
                            <span v-else>{{ isEditMode ? 'Simpan Perubahan' : 'Tambah Siswa' }}</span>
                        </PrimaryButton>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onUnmounted } from 'vue'
import { useAlertStore } from '@/stores/alert'
import FormLabel from '@/components/common/FormLabel.vue'
import FormInput from '@/components/common/FormInput.vue'
import { call } from 'frappe-ui'
import { extractErrorMessage } from '@/utils/errorHandler'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

interface Props {
    isOpen: boolean
    studentId?: string
    studentData?: {
        studentName: string
        nisn: string
        schoolUnit: string
        gradeLevel: string
        dateOfBirth?: string
    }
}

interface SelectOption {
    value: string
    label: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
    'close': []
    'student-saved': []
}>()

const alertStore = useAlertStore()

const formData = ref({
    studentName: '',
    nisn: '',
    schoolUnit: '',
    gradeLevel: '',
    dateOfBirth: ''
})

const schoolUnits = ref<SelectOption[]>([])
const grades = ref<SelectOption[]>([])
const isProcessing = ref(false)

const isEditMode = computed(() => !!props.studentId)

const canSubmit = computed(() => {
    return formData.value.studentName.trim() !== '' && formData.value.schoolUnit !== ''
})

const gradePlaceholder = computed(() => {
    if (!formData.value.schoolUnit) {
        return 'Pilih unit sekolah terlebih dahulu'
    }
    return grades.value.length > 0 ? 'Pilih kelas (opsional)' : 'Tidak ada kelas tersedia'
})

// Load school units
const loadSchoolUnits = async () => {
    try {
        // Load school units
        const unitsResponse = await call('/api/method/webshop.webshop.api.auth.get_school_units')

        schoolUnits.value = unitsResponse.school_units
    } catch (e) {
        console.error(e)
        alertStore.error("Terjadi kesalahan")
    }
}

// Load grades filtered by school unit
const loadGrades = async (schoolUnit?: string) => {
    try {
        const gradesResponse = await call('/api/method/webshop.webshop.api.auth.get_grades', { school_unit: schoolUnit })

        grades.value = gradesResponse.grades
    } catch (e) {
        alertStore.error("Terjadi kesalahan")
    }
}

// Watch for school unit changes to reload grades
watch(() => formData.value.schoolUnit, (newSchoolUnit, oldSchoolUnit) => {
    if (newSchoolUnit && newSchoolUnit !== oldSchoolUnit) {
        // Only clear grade level if this is a user change (oldSchoolUnit exists)
        // Don't clear on initial load when oldSchoolUnit is empty
        if (oldSchoolUnit) {
            formData.value.gradeLevel = ''
        }
        // Load grades for the new school unit
        loadGrades(newSchoolUnit)
    }
})

// Prevent body scroll when modal is open
watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        document.body.style.overflow = 'hidden'
    } else {
        document.body.style.overflow = ''
    }
})

// Cleanup on unmount
onUnmounted(() => {
    document.body.style.overflow = ''
})

// Watch for modal open to load data
watch(() => props.isOpen, (isOpen) => {
    if (isOpen) {
        loadSchoolUnits()
        if (props.studentData) {
            // Populate form with student data for editing
            formData.value = {
                studentName: props.studentData.studentName || '',
                nisn: props.studentData.nisn || '',
                schoolUnit: props.studentData.schoolUnit || '',
                gradeLevel: props.studentData.gradeLevel || '',
                dateOfBirth: props.studentData.dateOfBirth || ''
            }
            // Load grades for the selected school unit
            if (props.studentData.schoolUnit) {
                console.log(props.studentData.schoolUnit)
                loadGrades(props.studentData.schoolUnit)
            }
        } else {
            // Reset form for new student
            formData.value = {
                studentName: '',
                nisn: '',
                schoolUnit: '',
                gradeLevel: '',
                dateOfBirth: ''
            }
            grades.value = []
        }
    }
})

const handleClose = () => {
    if (!isProcessing.value) {
        emit('close')
    }
}

const handleSubmit = async () => {
    if (!canSubmit.value || isProcessing.value) return

    try {
        isProcessing.value = true

        const endpoint = isEditMode.value
            ? '/api/method/webshop.webshop.api.auth.update_student'
            : '/api/method/webshop.webshop.api.auth.create_student'

        const payload: any = {
            student_name: formData.value.studentName,
            nisn: formData.value.nisn,
            school_unit: formData.value.schoolUnit,
            grade_level: formData.value.gradeLevel,
            date_of_birth: formData.value.dateOfBirth
        }

        if (isEditMode.value) {
            payload.student_id = props.studentId
        }

        const response = await call(endpoint, payload)

        alertStore.success(isEditMode.value ? 'Data siswa berhasil diperbarui' : 'Siswa berhasil ditambahkan')
        emit('student-saved')
        emit('close')
    } catch (e) {
        const message = extractErrorMessage(e)
        alertStore.error(message)
    } finally {
        isProcessing.value = false
    }
}
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 50;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
}

.modal-container {
    background-color: white;
    border-radius: 1rem;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    max-width: 42rem;
    width: 100%;
    max-height: 90vh;
    overflow: auto;

    /* Custom scrollbar styles */
    scrollbar-width: thin;
    scrollbar-color: #d1d5db transparent;
}

/* Webkit scrollbar styles (Chrome, Safari, Edge) */
.modal-container::-webkit-scrollbar {
    width: 6px;
}

.modal-container::-webkit-scrollbar-track {
    background: transparent;
    margin: 1rem 0;
}

.modal-container::-webkit-scrollbar-thumb {
    background-color: #d1d5db;
    border-radius: 3px;
}

.modal-container::-webkit-scrollbar-thumb:hover {
    background-color: #9ca3af;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 10;
}

.close-button {
    color: #9ca3af;
    transition: color 0.15s ease-in-out;
}

.close-button:hover {
    color: #4b5563;
}

.modal-body {
    padding: 1.5rem;
}

.modal-footer {
    display: flex;
    gap: 0.75rem;
    padding: 1.5rem;
    border-top: 1px solid #e5e7eb;
    position: sticky;
    bottom: 0;
    background-color: white;
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
    transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
    transform: scale(0.9);
}
</style>
