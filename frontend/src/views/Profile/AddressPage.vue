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
                    <PrimaryButton variant="outline" size="small" @click="editAddress">
                        Edit Alamat
                    </PrimaryButton>
                </div>
            </div>
        </div>

        <!-- Form Section -->
        <div class="p-8">
            <h3 class="text-lg font-bold text-gray-900 mb-6">Alamat Lengkap</h3>

            <div class="space-y-5 max-w-2xl">
                <!-- Provinsi -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
                            </svg>
                        </template>
                        Provinsi
                    </FormLabel>
                    <FormInput v-model="formData.province" type="text" placeholder="Masukkan provinsi" />
                </div>

                <!-- Kota / Kabupaten -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008z" />
                            </svg>
                        </template>
                        Kota / Kabupaten
                    </FormLabel>
                    <FormInput v-model="formData.city" type="text" placeholder="Masukkan kota/kabupaten" />
                </div>

                <!-- Kecamatan -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
                            </svg>
                        </template>
                        Kecamatan
                    </FormLabel>
                    <FormInput v-model="formData.district" type="text" placeholder="Masukkan kecamatan" />
                </div>

                <!-- Kelurahan / Desa -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205l3 1m1.5.5l-1.5-.5M6.75 7.364V3h-3v18m3-13.636l10.5-3.819" />
                            </svg>
                        </template>
                        Kelurahan / Desa
                    </FormLabel>
                    <FormInput v-model="formData.village" type="text" placeholder="Masukkan kelurahan/desa" />
                </div>

                <!-- Kode Pos -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M21.75 9v.906a2.25 2.25 0 01-1.183 1.981l-6.478 3.488M2.25 9v.906a2.25 2.25 0 001.183 1.981l6.478 3.488m8.839 2.51l-4.66-2.51m0 0l-1.023-.55a2.25 2.25 0 00-2.134 0l-1.022.55m0 0l-4.661 2.51m16.5 1.615a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V8.844a2.25 2.25 0 011.183-1.98l7.5-4.04a2.25 2.25 0 012.134 0l7.5 4.04a2.25 2.25 0 011.183 1.98V19.5z" />
                            </svg>
                        </template>
                        Kode Pos
                    </FormLabel>
                    <FormInput v-model="formData.postalCode" type="text" placeholder="Masukkan kode pos" />
                </div>

                <!-- Alamat Lengkap -->
                <div>
                    <FormLabel icon="custom">
                        <template #icon>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                                stroke="currentColor" class="w-4 h-4 text-primary">
                                <path stroke-linecap="round" stroke-linejoin="round"
                                    d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
                            </svg>
                        </template>
                        Alamat Lengkap
                    </FormLabel>
                    <textarea v-model="formData.fullAddress"
                        class="w-full px-4 py-3 border rounded-lg text-sm text-gray-900 transition-all bg-gray-50 border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 focus:bg-white focus:outline-none resize-none"
                        rows="4" placeholder="Jl. Jombang Raya No.48 RT 03 / RW 05"></textarea>
                </div>
            </div>

            <!-- Notice Box -->
            <div class="mt-8 max-w-2xl bg-gray-50 border border-gray-200 rounded-xl p-4">
                <p class="text-xs text-gray-600 leading-relaxed">
                    <span class="font-semibold text-gray-900">Perhatian :</span> Alamat rumah ini digunakan untuk
                    keperluan pengiriman pesanan dan layanan antar jemput siswa.
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
    province: '',
    city: '',
    district: '',
    village: '',
    postalCode: '',
    fullAddress: ''
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
    await syncData()
})

const syncData = async () => {
    loading.value = true
    try {
        const response = await fetch('/api/method/webshop.webshop.api.auth.get_address', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include'
        })

        const data = await response.json()

        if (data.message?.success && data.message?.address) {
            const address = data.message.address
            formData.province = address.province || ''
            formData.city = address.city || ''
            formData.district = address.district || ''
            formData.village = address.village || ''
            formData.postalCode = address.postal_code || ''
            formData.fullAddress = address.full_address || ''
        } else if (data.message?.success && !data.message?.address) {
            // No address found, keep fields empty
            console.log('No address found for user')
        } else {
            console.error('Failed to fetch address:', data.message?.message)
        }
    } catch (e) {
        console.error('Error fetching address:', e)
        alertStore.error('Gagal memuat data alamat')
    } finally {
        loading.value = false
    }
}

const editAddress = async () => {
    if (!formData.province.trim()) {
        alertStore.error('Provinsi wajib diisi')
        return
    }
    if (!formData.city.trim()) {
        alertStore.error('Kota/Kabupaten wajib diisi')
        return
    }
    if (!formData.district.trim()) {
        alertStore.error('Kecamatan wajib diisi')
        return
    }
    if (!formData.village.trim()) {
        alertStore.error('Kelurahan/Desa wajib diisi')
        return
    }
    if (!formData.postalCode.trim()) {
        alertStore.error('Kode Pos wajib diisi')
        return
    }
    if (!formData.fullAddress.trim()) {
        alertStore.error('Alamat Lengkap wajib diisi')
        return
    }

    loading.value = true
    try {
        const response = await fetch('/api/method/webshop.webshop.api.auth.update_address', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                province: formData.province,
                city: formData.city,
                district: formData.district,
                village: formData.village,
                postal_code: formData.postalCode,
                full_address: formData.fullAddress
            })
        })

        const data = await response.json()

        if (data.message?.success) {
            alertStore.success('Alamat berhasil diperbarui')
            await syncData() // Refresh data after update
        } else {
            alertStore.error(data.message?.message || 'Gagal memperbarui alamat')
        }
    } catch (e) {
        console.error(e)
        alertStore.error('Terjadi kesalahan sistem')
    } finally {
        loading.value = false
    }
}
</script>
