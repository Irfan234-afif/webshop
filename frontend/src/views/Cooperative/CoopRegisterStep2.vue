<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <button @click="handleBack" class="w-10 h-10 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors">
          <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h2 class="text-2xl font-bold text-gray-900">Alamat Sesuai KTP (2/5)</h2>
      </div>
      <p class="text-gray-600">
        Isikan alamat lengkap Anda sesuai dengan yang tertera di KTP.
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 40%"></div>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleNext">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Province -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Provinsi</label>
          <FormInput v-model="formData.province" type="text" placeholder="Contoh: Jawa Timur" required />
        </div>

        <!-- City -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Kabupaten/Kota</label>
          <FormInput v-model="formData.city" type="text" placeholder="Contoh: Malang" required />
        </div>

        <!-- District -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Kecamatan</label>
          <FormInput v-model="formData.district" type="text" placeholder="Contoh: Lowokwaru" required />
        </div>

        <!-- Sub District -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Kelurahan/Desa</label>
          <FormInput v-model="formData.sub_district" type="text" placeholder="Contoh: Tlogomas" required />
        </div>

        <!-- Postal Code -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Kode Pos</label>
          <FormInput v-model="formData.postal_code" type="text" placeholder="Contoh: 65144" required />
        </div>
      </div>

      <!-- Full Address -->
      <div class="mb-8">
        <label class="block text-sm font-medium text-gray-700 mb-2">Alamat Lengkap (Jalan, RT/RW, Blok/No)</label>
        <textarea
          v-model="formData.full_address"
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition resize-none"
          rows="3"
          placeholder="Detail alamat sesuai KTP"
          required
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="flex gap-4">
        <button type="button" @click="handleBack"
          class="flex-1 bg-white border-2 border-gray-200 text-gray-700 font-bold py-4 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors">
          Kembali
        </button>
        <button type="submit" :disabled="!isStep2Valid"
          class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          Lanjut
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useCooperativeStore } from '@/stores/cooperative'
import FormInput from '@/components/common/FormInput.vue'

const cooperativeStore = useCooperativeStore()

const formData = computed(() => cooperativeStore.formData)
const isStep2Valid = computed(() => cooperativeStore.isStep2Valid)

const handleNext = () => {
  if (isStep2Valid.value) {
    cooperativeStore.nextStep()
  }
}

const handleBack = () => {
  cooperativeStore.prevStep()
}
</script>
