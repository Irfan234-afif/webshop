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
        <h2 class="text-2xl font-bold text-gray-900">Kontak Darurat (3/5)</h2>
      </div>
      <p class="text-gray-600">
        Mohon isikan orang terdekat yang dapat dihubungi dalam keadaan darurat.
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 60%"></div>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleNext">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- Emergency Contact Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Nama Lengkap Kontak</label>
          <FormInput v-model="formData.emergency_contact_name" type="text" placeholder="Nama Lengkap" required />
        </div>

        <!-- Relationship -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Hubungan</label>
          <FormSelect
            v-model="formData.emergency_contact_relationship"
            :options="relationshipOptions"
            placeholder="Pilih Hubungan"
            required
          />
        </div>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">No. HP Kontak Darurat</label>
        <vue-tel-input v-model="formData.emergency_contact_phone" mode="international" :default-country="'ID'"
          :preferred-countries="['ID']" :input-options="{
            placeholder: 'Masukkan nomor HP kontak darurat',
            required: true,
            styleClasses: 'phone-input'
          }" :dropdown-options="{
            showDialCodeInList: true,
            showDialCodeInSelection: true,
            showFlags: true,
            showSearchBox: true
          }" @validate="onPhoneValidate" />
        <div v-if="phoneError" class="mt-2 text-red-500 text-sm">{{ phoneError }}</div>
      </div>

      <!-- Emergency Contact Address -->
      <div class="mb-8">
        <label class="block text-sm font-medium text-gray-700 mb-2">Alamat Kontak Darurat</label>
        <textarea
          v-model="formData.emergency_contact_address"
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition resize-none"
          rows="3"
          placeholder="Alamat lengkap kontak darurat"
          required
        ></textarea>
      </div>

      <!-- Actions -->
      <div class="flex gap-4">
        <button type="button" @click="handleBack"
          class="flex-1 bg-white border-2 border-gray-200 text-gray-700 font-bold py-4 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors">
          Kembali
        </button>
        <button type="submit" :disabled="!isStep3Valid || !isPhoneValid"
          class="flex-1 bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
          Lanjut
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCooperativeStore } from '@/stores/cooperative'
import FormInput from '@/components/common/FormInput.vue'
import FormSelect from '@/components/common/FormSelect.vue'
import { VueTelInput } from 'vue-tel-input'
import 'vue-tel-input/vue-tel-input.css'

const cooperativeStore = useCooperativeStore()

const formData = computed(() => cooperativeStore.formData)
const isStep3Valid = computed(() => cooperativeStore.isStep3Valid)

const phoneError = ref('')
const isPhoneValid = ref(false)

const relationshipOptions = [
  { label: 'Suami', value: 'Suami' },
  { label: 'Istri', value: 'Istri' },
  { label: 'Orang Tua', value: 'Orang Tua' },
  { label: 'Anak', value: 'Anak' },
  { label: 'Saudara', value: 'Saudara' },
  { label: 'Lainnya', value: 'Lainnya' }
]

const onPhoneValidate = (payload: any) => {
  isPhoneValid.value = payload.valid
  if (!payload.valid && formData.value.emergency_contact_phone) {
    phoneError.value = 'Format nomor HP tidak valid'
  } else {
    phoneError.value = ''
  }
}

const handleNext = () => {
  if (isStep3Valid.value && isPhoneValid.value) {
    cooperativeStore.nextStep()
  } else if (!isPhoneValid.value) {
    phoneError.value = 'Nomor HP wajib diisi dengan valid'
  }
}

const handleBack = () => {
  cooperativeStore.prevStep()
}
</script>
