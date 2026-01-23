<template>
    <div>
        <!-- Header -->
        <div class="mb-8">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
                    <span class="text-xl font-bold text-white">2</span>
                </div>
                <h2 class="text-2xl font-bold text-gray-900">Alamat Lengkap</h2>
            </div>
            <p class="text-gray-600">
                Lengkapi detail alamat Anda untuk keperluan pengiriman dan data administrasi.
            </p>
        </div>

        <!-- Progress Bar for Step 2 -->
        <div class="mb-8">
            <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-primary transition-all duration-300" style="width: 50%"></div>
            </div>
        </div>

        <!-- Address Form -->
        <div class="mb-6">

            <!-- Alamat Lengkap -->
            <div class="mb-4">
                <label for="address_line1" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    <svg class="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    Alamat Lengkap
                </label>
                <FormInput v-model="formData.address.address_line1" type="text" placeholder="Jalan, No. Rumah, RT/RW" />
            </div>

            <!-- Detail Alamat (Optional) -->
            <div class="mb-4">
                <label for="address_line2" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                    Detail Alamat (Opsional)
                </label>
                <FormInput v-model="formData.address.address_line2" type="text"
                    placeholder="Apartemen, Komplek, Patokan" />
            </div>

            <!-- City and State -->
            <div class="grid grid-cols-2 gap-4 mb-4">
                <!-- Kota -->
                <div>
                    <label for="city" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        Kota
                    </label>
                    <FormInput v-model="formData.address.city" type="text" placeholder="Kota" />
                </div>

                <!-- Provinsi -->
                <div>
                    <label for="state" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        Provinsi (Opsional)
                    </label>
                    <FormInput v-model="formData.address.state" type="text" placeholder="Provinsi" />
                </div>
            </div>

            <!-- Postal Code and Country -->
            <div class="grid grid-cols-2 gap-4 mb-4">
                <!-- Kode Pos -->
                <div>
                    <label for="postal_code" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        Kode Pos (Opsional)
                    </label>
                    <FormInput v-model="formData.address.postal_code" type="text" placeholder="12345" />
                </div>

                <!-- Negara -->
                <div>
                    <label for="country" class="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                        Negara
                    </label>
                    <FormInput v-model="formData.address.country" type="text" placeholder="Indonesia" />
                </div>
            </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex gap-4">
            <button @click="registrationStore.prevStep()"
                class="flex-1 border-2 border-primary text-primary font-bold py-4 px-6 rounded-xl hover:bg-pink-50 transition-colors">
                Kembali
            </button>
            <button @click="handleNext" :disabled="!isStep2Valid"
                class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
                Lanjut
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRegistrationStore } from '@/stores/registration'
import FormInput from '@/components/common/FormInput.vue'

const registrationStore = useRegistrationStore()

const formData = computed(() => registrationStore.formData)
const isStep2Valid = computed(() => registrationStore.isStep2Valid)

const handleNext = () => {
    if (isStep2Valid.value) {
        registrationStore.nextStep()
    }
}
</script>
