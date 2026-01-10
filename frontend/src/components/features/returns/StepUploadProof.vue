<template>
  <div class="space-y-6">
    <!-- Upload zone -->
    <div class="relative">
      <div
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        class="border-2 border-dashed rounded-xl p-12 text-center transition-all"
        :class="{
          'border-primary bg-primary/5': isDragging,
          'border-gray-300 bg-gray-50': !isDragging
        }"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf"
          @change="handleFileSelect"
          class="hidden"
        />

        <div class="flex flex-col items-center justify-center">
          <!-- Icon -->
          <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"/>
            </svg>
          </div>

          <p class="text-lg font-semibold text-primary mb-2">
            Upload Foto (Format JPG / PNG)
          </p>
          <p class="text-sm text-gray-500 mb-4">
            atau seret dan lepaskan file di sini
          </p>
          <p class="text-xs text-gray-400">
            Maksimal 5MB per file • JPG, PNG, atau PDF
          </p>

          <button
            @click="triggerFileSelect"
            type="button"
            class="mt-4 px-6 py-3 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            Pilih File
          </button>
        </div>
      </div>
    </div>

    <!-- Uploaded files preview -->
    <div v-if="uploadedFiles.length > 0" class="space-y-3">
      <h4 class="font-semibold text-gray-900">File yang Diunggah ({{ uploadedFiles.length }})</h4>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="(file, index) in uploadedFiles"
          :key="index"
          class="relative bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <!-- Image preview for images -->
          <div v-if="isImageFile(file.file_name)" class="mb-3">
            <img
              :src="file.file_url"
              :alt="file.file_name"
              class="w-full h-32 object-cover rounded-lg"
            />
          </div>

          <!-- PDF icon for PDFs -->
          <div v-else class="mb-3 flex items-center justify-center h-32 bg-gray-100 rounded-lg">
            <svg class="w-12 h-12 text-red-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clip-rule="evenodd"/>
            </svg>
          </div>

          <!-- File info -->
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ file.file_name }}
              </p>
              <p class="text-xs text-gray-500">
                {{ formatFileSize(file.file_size) }}
              </p>
            </div>

            <!-- Remove button -->
            <button
              @click="removeFile(index)"
              type="button"
              class="ml-2 text-red-500 hover:text-red-700 transition-colors flex-shrink-0"
              aria-label="Hapus file"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Currently uploading -->
    <div v-if="uploadingFiles.length > 0" class="space-y-2">
      <h4 class="font-semibold text-gray-900">Mengunggah...</h4>
      <div
        v-for="(file, index) in uploadingFiles"
        :key="`uploading-${index}`"
        class="bg-blue-50 border border-blue-200 rounded-lg p-3"
      >
        <div class="flex items-center">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
          <span class="text-sm text-blue-700">{{ file.name }}</span>
        </div>
      </div>
    </div>

    <!-- Upload errors -->
    <div v-if="uploadErrors.length > 0" class="space-y-2">
      <div
        v-for="(error, index) in uploadErrors"
        :key="`error-${index}`"
        class="bg-red-50 border border-red-200 rounded-lg p-3"
      >
        <div class="flex items-start">
          <svg class="w-5 h-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
          </svg>
          <span class="text-sm text-red-700">{{ error }}</span>
        </div>
      </div>
    </div>

    <!-- Info message -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
        </svg>
        <div class="text-sm text-blue-700">
          <p class="font-medium mb-1">Tips untuk foto yang baik:</p>
          <ul class="list-disc pl-5 space-y-1">
            <li>Foto harus jelas dan tidak blur</li>
            <li>Tunjukkan kerusakan/cacat produk dengan jelas</li>
            <li>Sertakan foto kemasan jika relevan</li>
            <li>Anda dapat mengunggah beberapa foto</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useReturnsStore } from '@/stores/returns'
import type { UploadedFile } from '@/types/returns'

interface Emits {
  (e: 'update:files', value: string[]): void
  (e: 'update:isValid', value: boolean): void
}

const emit = defineEmits<Emits>()

const returnsStore = useReturnsStore()

const fileInput = ref<HTMLInputElement | null>(null)
const uploadedFiles = ref<UploadedFile[]>([])
const uploadingFiles = ref<File[]>([])
const uploadErrors = ref<string[]>([])
const isDragging = ref(false)

const isValid = computed(() => {
  // At least one file should be uploaded for better verification,
  // but we'll make it optional to allow flexibility
  return uploadedFiles.value.length >= 0
})

watch(uploadedFiles, () => {
  const fileUrls = uploadedFiles.value.map(f => f.file_url)
  emit('update:files', fileUrls)
}, { deep: true })

watch(isValid, (newVal) => {
  emit('update:isValid', newVal)
})

function triggerFileSelect() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    uploadFiles(Array.from(target.files))
  }
  // Reset input value to allow selecting the same file again
  target.value = ''
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  
  if (event.dataTransfer?.files) {
    uploadFiles(Array.from(event.dataTransfer.files))
  }
}

async function uploadFiles(files: File[]) {
  uploadErrors.value = []
  
  for (const file of files) {
    uploadingFiles.value.push(file)
    
    try {
      const uploadedFile = await returnsStore.uploadSupportingDocument(file)
      uploadedFiles.value.push(uploadedFile)
    } catch (err: any) {
      const errorMessage = `${file.name}: ${err.message || 'Upload gagal'}`
      uploadErrors.value.push(errorMessage)
    } finally {
      // Remove from uploading list
      const index = uploadingFiles.value.indexOf(file)
      if (index > -1) {
        uploadingFiles.value.splice(index, 1)
      }
    }
  }
}

function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

function isImageFile(fileName: string): boolean {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
  const ext = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
  return imageExtensions.includes(ext)
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Expose validation method for parent component
defineExpose({
  validateForm: () => isValid.value
})
</script>
