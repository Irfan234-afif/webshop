<template>
    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <!-- User Profile Header Card -->
        <div class="bg-white border-b border-gray-100 p-8">
            <div class="flex flex-col md:flex-row items-center gap-6">
                <!-- Avatar -->
                <div class="w-20 h-20 rounded-full flex items-center justify-center text-white text-2xl font-semibold shadow-lg shrink-0"
                    style="background: linear-gradient(to bottom right, var(--color-primary), var(--color-secondary));">
                    {{ getInitials(authStore.user?.full_name || 'User') }}
                </div>

                <!-- User Info -->
                <div class="flex-1 text-center md:text-left">
                    <h2 class="text-xl font-bold text-gray-900">{{ authStore.user?.full_name || 'User' }}</h2>
                    <p class="text-sm text-gray-500">{{ authStore.user?.email }}</p>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-3">
                    <PrimaryButton variant="outline" size="small" @click="addStudent">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                            stroke="currentColor" class="w-5 h-5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                        </svg>
                        Tambah Data Siswa
                    </PrimaryButton>
                </div>
            </div>
        </div>

        <!-- Students List Section -->
        <div class="p-8">
            <h3 class="text-lg font-bold text-gray-900 mb-6">Data Siswa</h3>

            <div class="space-y-4 max-w-full">
                <!-- Loading State -->
                <div v-if="loading" class="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                    <p class="text-gray-500">Memuat data siswa...</p>
                </div>

                <!-- Student Card -->
                <div v-else-if="!loading && students.length > 0" v-for="student in students" :key="student.id"
                    class="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                    <div class="flex items-start justify-between mb-4">
                        <div class="flex items-center gap-3">
                            <div class="w-12 h-12 rounded-full flex items-center justify-center text-white text-lg font-semibold shrink-0"
                                style="background: linear-gradient(to bottom right, var(--color-primary), var(--color-secondary));">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                                    stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
                                    <path stroke-linecap="round" stroke-linejoin="round"
                                        d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                                </svg>
                            </div>
                            <div>
                                <h4 class="font-semibold text-gray-900 text-base">
                                    {{ student.name }}
                                    <span class="text-sm font-medium text-gray-600">({{ student.unit }})</span>
                                </h4>
                            </div>
                        </div>
                        <PrimaryButton variant="outline" size="small" @click="editStudent(student.id)">
                            Edit Data Siswa
                        </PrimaryButton>
                    </div>

                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p class="text-gray-500 mb-1">NIS / NISN</p>
                            <p class="text-gray-900 font-medium">{{ student.nis }}</p>
                        </div>
                        <div>
                            <p class="text-gray-500 mb-1">Nama Anak</p>
                            <p class="text-gray-900 font-medium">{{ student.name }}</p>
                        </div>
                        <div>
                            <p class="text-gray-500 mb-1">Unit</p>
                            <p class="text-gray-900 font-medium">{{ student.unit }}</p>
                        </div>
                        <div>
                            <p class="text-gray-500 mb-1">Kelas</p>
                            <p class="text-gray-900 font-medium">{{ student.class }}</p>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else-if="!loading && students.length === 0"
                    class="bg-gray-50 border border-gray-200 rounded-xl p-12 text-center">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                        stroke="currentColor" class="w-16 h-16 mx-auto text-gray-400 mb-4">
                        <path stroke-linecap="round" stroke-linejoin="round"
                            d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                    </svg>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Belum ada data siswa</h3>
                    <p class="text-gray-500 mb-4">Tambahkan data siswa untuk memulai</p>
                    <PrimaryButton variant="primary" @click="addStudent">
                        Tambah Data Siswa
                    </PrimaryButton>
                </div>
            </div>

            <!-- Notice Box -->
            <div class="mt-8 max-w-full bg-gray-50 border border-gray-200 rounded-xl p-4">
                <p class="text-xs text-gray-600 leading-relaxed">
                    <span class="font-semibold text-gray-900">Perhatian :</span> Alamat rumah ini digunakan untuk
                    keperluan pengiriman pesanan dan layanan antar jemput siswa.
                </p>
            </div>
        </div>

        <!-- Student Modal -->
        <StudentModal :is-open="isModalOpen" :student-id="editingStudentId" :student-data="editingStudentData"
            @close="closeModal" @student-saved="handleStudentSaved" />
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAlertStore } from '@/stores/alert'
import PrimaryButton from '@/components/common/PrimaryButton.vue'
import StudentModal from '@/components/features/profile/StudentModal.vue'

interface Student {
    id: string
    nis: string
    name: string
    unit: string
    class: string
}

const authStore = useAuthStore()
const alertStore = useAlertStore()
const loading = ref(false)
const students = ref<Student[]>([])

// Modal state
const isModalOpen = ref(false)
const editingStudentId = ref<string | undefined>(undefined)
const editingStudentData = ref<{
    studentName: string
    nisn: string
    schoolUnit: string
    gradeLevel: string
    dateOfBirth?: string
} | undefined>(undefined)

// Helper function to get initials from name
const getInitials = (name: string): string => {
    if (!name) return 'U'
    const parts = name.trim().split(' ')
    if (parts.length === 1) return parts[0]!.charAt(0).toUpperCase()
    return (parts[0]!.charAt(0) + parts[parts.length - 1]!.charAt(0)).toUpperCase()
}

onMounted(async () => {
    if (!authStore.user) {
        await authStore.fetchCurrentUser()
    }
    await loadStudents()
})

const loadStudents = async () => {
    loading.value = true
    try {
        const response = await fetch('/api/method/webshop.webshop.api.auth.get_students', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })

        const data = await response.json()

        if (data.message?.success && data.message?.students) {
            // Map backend data to frontend Student interface
            students.value = data.message.students.map((s: any) => ({
                id: s.student_id,
                nis: s.nisn || '-',
                name: s.student_name,
                unit: s.school_unit || '-',
                class: s.grade_level || '-'
            }))
        } else {
            console.error('Failed to fetch students:', data.message?.message)
            students.value = []
        }
    } catch (e) {
        console.error('Error fetching students:', e)
        alertStore.error('Gagal memuat data siswa')
        students.value = []
    } finally {
        loading.value = false
    }
}

const addStudent = () => {
    editingStudentId.value = undefined
    editingStudentData.value = undefined
    isModalOpen.value = true
}

const editStudent = (studentId: string) => {
    // Find the student data
    const student = students.value.find(s => s.id === studentId)
    if (student) {
        editingStudentId.value = studentId
        editingStudentData.value = {
            studentName: student.name,
            nisn: student.nis === '-' ? '' : student.nis,
            schoolUnit: student.unit === '-' ? '' : student.unit,
            gradeLevel: student.class === '-' ? '' : student.class
        }
        isModalOpen.value = true
    }
}

const closeModal = () => {
    isModalOpen.value = false
    editingStudentId.value = undefined
    editingStudentData.value = undefined
}

const handleStudentSaved = async () => {
    await loadStudents()
}

</script>
