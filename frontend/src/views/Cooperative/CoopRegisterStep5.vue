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
        <h2 class="text-2xl font-bold text-gray-900">Konfirmasi (5/5)</h2>
      </div>
      <p class="text-gray-600">
        Periksa kembali data Anda sebelum menyelesaikan pendaftaran.
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 100%"></div>
      </div>
    </div>

    <!-- Summary Overview -->
    <div class="space-y-6 mb-8">
      <!-- Personal Data -->
      <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-gray-900">Data Pribadi</h3>
          <button @click="cooperativeStore.goToStep(1)" class="text-primary text-sm font-medium hover:underline">Ubah</button>
        </div>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4 text-sm">
          <div>
            <dt class="text-gray-500 mb-1">NIK</dt>
            <dd class="font-medium text-gray-900">{{ formData.nik }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 mb-1">Nama Lengkap</dt>
            <dd class="font-medium text-gray-900">{{ formData.full_name }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 mb-1">Tempat, Tanggal Lahir</dt>
            <dd class="font-medium text-gray-900">{{ formData.place_of_birth }}, {{ formatDate(formData.date_of_birth) }}</dd>
          </div>
          <div>
            <dt class="text-gray-500 mb-1">Kontak</dt>
            <dd class="font-medium text-gray-900">{{ formData.phone_number }}<br/>{{ formData.email }}</dd>
          </div>
        </dl>
      </div>

      <!-- KTP Address -->
      <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-gray-900">Alamat Sesuai KTP</h3>
          <button @click="cooperativeStore.goToStep(2)" class="text-primary text-sm font-medium hover:underline">Ubah</button>
        </div>
        <p class="text-sm font-medium text-gray-900">{{ formData.full_address }}</p>
        <p class="text-sm text-gray-600 mt-1">
          Kec. {{ formData.district }}, Kel. {{ formData.sub_district }}<br/>
          {{ formData.city }}, {{ formData.province }} {{ formData.postal_code }}
        </p>
      </div>

      <!-- Emergency Contact -->
      <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-gray-900">Kontak Darurat</h3>
          <button @click="cooperativeStore.goToStep(3)" class="text-primary text-sm font-medium hover:underline">Ubah</button>
        </div>
        <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-4 text-sm">
          <div>
            <dt class="text-gray-500 mb-1">Nama & Hubungan</dt>
            <dd class="font-medium text-gray-900">{{ formData.emergency_contact_name }} ({{ formData.emergency_contact_relationship }})</dd>
          </div>
          <div>
            <dt class="text-gray-500 mb-1">No. HP</dt>
            <dd class="font-medium text-gray-900">{{ formData.emergency_contact_phone }}</dd>
          </div>
        </dl>
      </div>

      <!-- Payment & Fee -->
      <div class="bg-purple-50 rounded-xl p-6 border border-purple-200">
        <div class="flex justify-between items-center mb-4">
          <h3 class="font-bold text-gray-900">Pembayaran</h3>
          <button @click="cooperativeStore.goToStep(4)" class="text-primary text-sm font-medium hover:underline">Ubah</button>
        </div>
        
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600">Metode</span>
          <span class="text-sm font-bold text-gray-900">
             {{ paymentMethodName }}
             <span v-if="cooperativeStore.paymentChannel"> - {{ cooperativeStore.paymentChannel }}</span>
          </span>
        </div>
        <div class="flex items-center justify-between mb-4 pb-4 border-b border-purple-200">
          <span class="text-sm text-gray-600">Total Biaya</span>
          <span class="font-bold text-primary">{{ formatCurrency(cooperativeStore.settings?.total_registration_amount || 0) }}</span>
        </div>

        <p class="text-xs text-gray-500">
          Dengan mendaftar, Anda menyetujui syarat dan ketentuan keanggotaan koperasi dan bersedia membayar simpanan pokok serta simpanan wajib sesuai ketentuan yang berlaku.
        </p>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="cooperativeStore.error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
      <svg class="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-red-800">{{ cooperativeStore.error }}</p>
    </div>

    <!-- Actions -->
    <div class="flex gap-4">
      <button type="button" @click="handleBack" :disabled="cooperativeStore.isSubmitting"
        class="flex-1 bg-white border-2 border-gray-200 text-gray-700 font-bold py-4 px-6 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-colors disabled:opacity-50">
        Kembali
      </button>
      <button type="button" @click="handleSubmit" :disabled="cooperativeStore.isSubmitting"
        class="flex-[2] bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
        <svg v-if="cooperativeStore.isSubmitting" class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Selesaikan Pendaftaran
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCooperativeStore } from '@/stores/cooperative'

const router = useRouter()
const cooperativeStore = useCooperativeStore()
const formData = computed(() => cooperativeStore.formData)

const paymentMethodName = computed(() => {
  const method = cooperativeStore.paymentMethods.find(m => m.name === cooperativeStore.paymentMethodType)
  return method ? method.label : cooperativeStore.paymentMethodType
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })
  } catch(e) {
    return dateStr
  }
}

const handleBack = () => {
  cooperativeStore.prevStep()
}

const handleSubmit = async () => {
  const result = await cooperativeStore.submitRegistration()
  if (result.success) {
    // Navigate to payment page directly
    router.replace('/member/payment')
  }
}
</script>
