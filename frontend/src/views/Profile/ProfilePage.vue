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
                    <PrimaryButton variant="outline" size="small" @click="saveProfile">
                        Edit Profil
                    </PrimaryButton>
                </div>
            </div>
        </div>

        <!-- Form Section -->
        <div class="p-8">
            <h3 class="text-lg font-bold text-gray-900 mb-6">Informasi Akun</h3>

            <div class="space-y-5 max-w-2xl">
                <!-- Nama Lengkap -->
                <div>
                    <FormLabel>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="9.9974" cy="4.99996" r="3.33333" fill="#AC208E" />
                            <ellipse cx="9.9974" cy="14.1666" rx="5.83333" ry="3.33333" fill="#AC208E" />
                        </svg>
                        Nama Lengkap
                    </FormLabel>
                    <FormInput v-model="formData.fullName" type="text" placeholder="Masukkan nama lengkap" />
                </div>

                <!-- Nomor HP -->
                <div>
                    <FormLabel>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd"
                                d="M10.0456 1.66669H9.95962C8.55943 1.66668 7.45037 1.66667 6.5824 1.7854C5.68912 1.90759 4.96611 2.16504 4.39593 2.74517C3.82575 3.3253 3.57271 4.06092 3.45261 4.96977C3.33592 5.85288 3.33593 6.98127 3.33594 8.40589V11.5941C3.33593 13.0188 3.33592 14.1472 3.45261 15.0303C3.57271 15.9391 3.82575 16.6747 4.39593 17.2549C4.96611 17.835 5.68912 18.0925 6.5824 18.2146C7.45036 18.3334 8.55941 18.3334 9.95959 18.3334H10.0456C11.4458 18.3334 12.5548 18.3334 13.4228 18.2146C14.3161 18.0925 15.0391 17.835 15.6093 17.2549C16.1795 16.6747 16.4325 15.9391 16.5526 15.0303C16.6693 14.1472 16.6693 13.0188 16.6693 11.5942V8.4059C16.6693 6.9813 16.6693 5.85288 16.5526 4.96977C16.4325 4.06092 16.1795 3.3253 15.6093 2.74517C15.0391 2.16504 14.3161 1.90759 13.4228 1.7854C12.5548 1.66667 11.4458 1.66668 10.0456 1.66669ZM7.14546 15.4264C7.14546 15.1053 7.4013 14.845 7.71689 14.845H12.2883C12.6039 14.845 12.8597 15.1053 12.8597 15.4264C12.8597 15.7475 12.6039 16.0078 12.2883 16.0078H7.71689C7.4013 16.0078 7.14546 15.7475 7.14546 15.4264Z"
                                fill="#AC208E" />
                        </svg>
                        Nomor HP (WhatsApp Aktif)
                    </FormLabel>
                    <FormInput v-model="formData.phone" type="tel" placeholder="0812 3456 7891" />
                </div>

                <!-- Email (Read-only) -->
                <div>
                    <FormLabel>
                        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path fill-rule="evenodd" clip-rule="evenodd"
                                d="M2.64037 4.30962C1.66406 5.28593 1.66406 6.85728 1.66406 9.99998C1.66406 13.1427 1.66406 14.714 2.64037 15.6903C3.61668 16.6666 5.18803 16.6666 8.33073 16.6666H11.6641C14.8068 16.6666 16.3781 16.6666 17.3544 15.6903C18.3307 14.714 18.3307 13.1427 18.3307 9.99998C18.3307 6.85728 18.3307 5.28593 17.3544 4.30962C16.3781 3.33331 14.8068 3.33331 11.6641 3.33331H8.33073C5.18803 3.33331 3.61668 3.33331 2.64037 4.30962ZM15.4775 6.26653C15.6985 6.5317 15.6627 6.92581 15.3975 7.14678L13.5671 8.67212C12.8285 9.28767 12.2298 9.78658 11.7014 10.1264C11.151 10.4804 10.615 10.704 9.9974 10.704C9.37983 10.704 8.84379 10.4804 8.29338 10.1264C7.76499 9.78658 7.16632 9.28767 6.42769 8.67213L4.59728 7.14678C4.33211 6.92581 4.29628 6.5317 4.51726 6.26653C4.73823 6.00136 5.13234 5.96553 5.39751 6.18651L7.19659 7.68574C7.97406 8.33363 8.51384 8.78199 8.96955 9.07509C9.41068 9.3588 9.70984 9.45404 9.9974 9.45404C10.285 9.45404 10.5841 9.3588 11.0252 9.07509C11.481 8.78199 12.0207 8.33363 12.7982 7.68574L14.5973 6.18651C14.8625 5.96553 15.2566 6.00136 15.4775 6.26653Z"
                                fill="#AC208E" />
                        </svg>

                        Email
                    </FormLabel>
                    <FormInput :model-value="authStore.user?.email || ''" type="email" readonly />
                </div>
            </div>

            <!-- Notice Box -->
            <div class="mt-8 max-w-2xl bg-gray-50 border border-gray-200 rounded-xl p-4">
                <p class="text-xs text-gray-600 leading-relaxed">
                    <span class="font-semibold text-gray-900">Perhatian :</span> Data ini digunakan untuk keperluan
                    transaksi, notifikasi, dan verifikasi akun.
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAlertStore } from '@/stores/alert'
import PrimaryButton from '@/components/common/PrimaryButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import FormLabel from '@/components/common/FormLabel.vue'

const authStore = useAuthStore()
const alertStore = useAlertStore()
const loading = ref(false)

const formData = reactive({
    fullName: '',
    phone: ''
})

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
    syncData()
})

const syncData = () => {
    if (authStore.user) {
        formData.fullName = authStore.user?.full_name || ''
        formData.phone = authStore.user?.phone || ''
    }
}

const saveProfile = async () => {
    if (!formData.fullName.trim()) {
        alertStore.error('Nama Lengkap wajib diisi')
        return
    }
    if (!formData.phone.trim()) {
        alertStore.error('Nomor Handphone wajib diisi')
        return
    }

    loading.value = true
    try {
        const result = await authStore.updateProfile(formData.fullName, formData.phone)
        if (result.success) {
            alertStore.success('Profile berhasil diperbarui')
        } else {
            alertStore.error(result.message || 'Gagal memperbarui profile')
        }
    } catch (e) {
        console.error(e)
        alertStore.error('Terjadi kesalahan sistem')
    } finally {
        loading.value = false
    }
}
</script>
