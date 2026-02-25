<template>
  <div>
    <!-- Header -->
    <div class="mb-8">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900">Data Pribadi (1/5)</h2>
      </div>
      <p class="text-gray-600">
        Lengkapi data pribadi Anda untuk mendaftar sebagai anggota koperasi.
      </p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-primary transition-all duration-300" style="width: 20%"></div>
      </div>
    </div>

    <!-- Form -->
    <form @submit.prevent="handleNext">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <!-- NIK -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">NIK KTP</label>
          <FormInput v-model="formData.nik" type="text" placeholder="16 Digit NIK KTP" required maxlength="16" />
        </div>

        <!-- Full Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Nama Lengkap (Sesuai KTP)</label>
          <FormInput v-model="formData.full_name" type="text" placeholder="Nama Lengkap" required />
        </div>
        
        <!-- Place of Birth -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tempat Lahir</label>
          <FormInput v-model="formData.place_of_birth" type="text" placeholder="Tempat Lahir" required />
        </div>
        
        <!-- Date of Birth -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Tanggal Lahir</label>
          <DatePicker
            class="custom-datepicker"
            v-model="formData.date_of_birth"
            placeholder="Pilih tanggal lahir"
          />
        </div>

        <!-- Gender -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Jenis Kelamin</label>
          <FormSelect
            v-model="formData.gender"
            :options="genderOptions"
            placeholder="Pilih Jenis Kelamin"
            required
          />
        </div>

        <!-- Occupation -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Pekerjaan</label>
          <FormInput v-model="formData.occupation" type="text" placeholder="Pekerjaan" required />
        </div>

        <!-- Marital Status -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Status Pernikahan</label>
          <FormSelect
            v-model="formData.marital_status"
            :options="maritalStatusOptions"
            placeholder="Pilih Status Pernikahan"
            required
          />
        </div>

        <!-- Relationship -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Hubungan dengan Yayasan/Koperasi</label>
          <FormSelect
            v-model="formData.relationship_with_cooperative"
            :options="relationshipOptions"
            placeholder="Pilih Hubungan"
            required
          />
        </div>
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
        <FormInput v-model="formData.email" type="email" placeholder="Email" required />
      </div>

      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">No. HP (WhatsApp)</label>
        <vue-tel-input v-model="formData.phone_number" mode="international" :default-country="'ID'"
          :preferred-countries="['ID']" :input-options="{
            placeholder: 'Masukkan nomor WhatsApp aktif',
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

      <!-- KTP Photo Upload -->
      <div class="mb-8">
        <label class="block text-sm font-medium text-gray-700 mb-2">Upload Foto KTP</label>
        
        <div v-if="formData.ktp_photo" class="mb-4 relative rounded-xl border border-gray-200 p-2 overflow-hidden w-full max-w-sm">
          <!-- We show the uploaded file as img if image, else link -->
          <img v-if="isImageFile(formData.ktp_photo)" :src="formData.ktp_photo" class="w-full h-auto object-cover rounded-lg max-h-[200px]" />
          <div v-else class="p-4 bg-gray-50 flex items-center justify-center text-gray-600 rounded-lg">File terunggah</div>
          <button type="button" @click.prevent="removeKtpPhoto" class="absolute top-4 right-4 bg-red-500 text-white rounded-full p-1 hover:bg-red-600">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>

        <div v-else>
          <div class="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:bg-gray-50 transition cursor-pointer" @click="openFilePicker">
            <svg class="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
            </svg>
            <p class="text-sm text-gray-600">
              <span class="text-primary font-semibold">Klik untuk memilih file</span> KTP
            </p>
            <p class="text-xs text-gray-500 mt-1">JPG, PNG maksimal 5MB</p>
          </div>
          <input ref="fileInputRef" type="file" class="hidden" accept="image/jpeg,image/png,image/jpg" @change="handleFileSelect" />
          
          <div v-if="uploadProgress" class="mt-2">
            <progress :value="uploadProgress.percentage" max="100" class="w-full h-2"></progress>
            <p class="text-xs text-center text-primary mt-1">Mengupload... {{ uploadProgress.percentage }}%</p>
          </div>
          <div v-if="uploadError" class="mt-2 text-red-500 text-xs">{{ uploadError }}</div>
        </div>
      </div>

      <!-- Submit Button -->
      <button type="submit" :disabled="!isStep1Valid || !isPhoneValid || isUploading"
        class="w-full bg-primary text-white font-bold py-4 px-6 rounded-xl hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        Lanjut
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { DatePicker } from 'frappe-ui'
import { useCooperativeStore } from '@/stores/cooperative'
import { useAuthStore } from '@/stores/auth'
import FormInput from '@/components/common/FormInput.vue'
import FormSelect from '@/components/common/FormSelect.vue'
import { VueTelInput } from 'vue-tel-input'
import 'vue-tel-input/vue-tel-input.css'
import { uploadFile, validateFile, type UploadProgress } from '@/utils/fileUpload'

const cooperativeStore = useCooperativeStore()
const authStore = useAuthStore()

const formData = computed(() => cooperativeStore.formData)
const isStep1Valid = computed(() => cooperativeStore.isStep1Valid)

const phoneError = ref('')
const isPhoneValid = ref(false)

const genderOptions = [
  { label: 'Laki-laki', value: 'Male' },
  { label: 'Perempuan', value: 'Female' }
]

const maritalStatusOptions = [
  { label: 'Belum Kawin', value: 'Single' },
  { label: 'Kawin', value: 'Married' },
  { label: 'Cerai Hidup', value: 'Divorced' },
  { label: 'Cerai Mati', value: 'Widowed' }
]

const relationshipOptions = [
  { label: 'Karyawan', value: 'Karyawan' },
  { label: 'Wali Murid', value: 'Wali Murid' },
  { label: 'Simpatisan', value: 'Simpatisan' },
  { label: 'Alumni', value: 'Alumni' },
  { label: 'Lainnya', value: 'Lainnya' }
]

const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadProgress = ref<UploadProgress | null>(null)
const uploadError = ref('')
const isUploading = ref(false)

onMounted(() => {
  // Pre-fill from auth profile if empty
  if (!formData.value.full_name && authStore.user) {
    formData.value.full_name = authStore.user.full_name
  }
  if (!formData.value.email && authStore.user) {
    formData.value.email = authStore.user.email
  }
  if (!formData.value.phone_number && authStore.user?.phone) {
    formData.value.phone_number = authStore.user.phone
    isPhoneValid.value = true // assume valid if from profile
  }
})

const onPhoneValidate = (payload: any) => {
  isPhoneValid.value = payload.valid
  if (!payload.valid && formData.value.phone_number) {
    phoneError.value = 'Format nomor HP tidak valid'
  } else {
    phoneError.value = ''
  }
}

const openFilePicker = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  uploadError.value = ''
  
  const validationError = validateFile(file, 5, ['image/jpeg', 'image/png', 'image/jpg'])
  if (validationError) {
    uploadError.value = validationError
    return
  }

  isUploading.value = true
  try {
    const result = await uploadFile(file, (progress) => {
      uploadProgress.value = progress
    })
    formData.value.ktp_photo = result.file_url
  } catch (err: any) {
    uploadError.value = err.message || 'Gagal mengupload file KTP'
  } finally {
    isUploading.value = false
    uploadProgress.value = null
  }
}

const removeKtpPhoto = () => {
  formData.value.ktp_photo = ''
}

const isImageFile = (fileUrl: string) => {
  if (!fileUrl) return false
  const lowerUrl = fileUrl.toLowerCase()
  return lowerUrl.endsWith('.jpg') || lowerUrl.endsWith('.jpeg') || lowerUrl.endsWith('.png')
}

const handleNext = () => {
  if (isStep1Valid.value && isPhoneValid.value) {
    cooperativeStore.nextStep()
  } else if (!isPhoneValid.value) {
    phoneError.value = 'Nomor HP wajib diisi dengan valid'
  }
}
</script>
