<script setup lang="ts">
import { ref, computed } from 'vue'
import { uploadFile, validateFile, formatFileSize, type UploadProgress } from '@/utils/fileUpload'

interface Props {
  isOpen: boolean
  salesOrderId: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
  success: [fileUrl: string, notes?: string]
}>()

// State
const selectedFile = ref<File | null>(null)
const notes = ref('')
const isUploading = ref(false)
const uploadProgress = ref<UploadProgress | null>(null)
const error = ref<string | null>(null)
const isDragging = ref(false)

// Computed
const hasFile = computed(() => selectedFile.value !== null)
const canUpload = computed(() => hasFile.value && !isUploading.value)
const filePreview = computed(() => {
  if (!selectedFile.value) return null

  return {
    name: selectedFile.value.name,
    size: formatFileSize(selectedFile.value.size),
    type: selectedFile.value.type
  }
})

// File input ref
const fileInputRef = ref<HTMLInputElement | null>(null)

// Methods
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  isDragging.value = false

  const file = event.dataTransfer?.files[0]
  if (file) {
    processFile(file)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const processFile = (file: File) => {
  error.value = null

  // Validate file
  const validationError = validateFile(file, 5, [
    'image/jpeg',
    'image/png',
    'image/jpg',
    'application/pdf'
  ])

  if (validationError) {
    error.value = validationError
    selectedFile.value = null
    return
  }

  selectedFile.value = file
}

const openFilePicker = () => {
  fileInputRef.value?.click()
}

const removeFile = () => {
  selectedFile.value = null
  error.value = null
  uploadProgress.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) return

  isUploading.value = true
  error.value = null
  uploadProgress.value = null

  try {
    // Upload file to Frappe
    const result = await uploadFile(selectedFile.value, (progress) => {
      uploadProgress.value = progress
    })

    // Emit success with file URL and notes
    emit('success', result.file_url, notes.value || undefined)

    // Reset state
    selectedFile.value = null
    notes.value = ''
    uploadProgress.value = null
  } catch (err: any) {
    console.error('Upload error:', err)
    error.value = err.message || 'Failed to upload file'
  } finally {
    isUploading.value = false
  }
}

const handleClose = () => {
  if (isUploading.value) {
    if (!confirm('Upload in progress. Are you sure you want to cancel?')) {
      return
    }
  }

  // Reset state
  selectedFile.value = null
  notes.value = ''
  error.value = null
  uploadProgress.value = null
  isUploading.value = false

  emit('close')
}

const getFileIcon = (type: string) => {
  if (type.startsWith('image/')) {
    return 'image'
  } else if (type === 'application/pdf') {
    return 'pdf'
  }
  return 'file'
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
      @click="handleClose"
    >
      <div
        class="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[90vh] flex flex-col"
        @click.stop
      >
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 class="text-xl font-bold text-gray-900">Upload Bukti Transfer</h2>
            <p class="text-sm text-gray-500 mt-1">
              Upload gambar atau PDF bukti transfer Anda
            </p>
          </div>
          <button
            @click="handleClose"
            class="text-gray-400 hover:text-gray-600 transition-colors"
            :disabled="isUploading"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- File Drop Zone -->
          <div
            v-if="!hasFile"
            class="border-2 border-dashed rounded-xl p-8 text-center transition-colors"
            :class="{
              'border-[#ac208e] bg-purple-50': isDragging,
              'border-gray-300 hover:border-gray-400': !isDragging
            }"
            @drop.prevent="handleDrop"
            @dragover.prevent="handleDragOver"
            @dragleave="handleDragLeave"
          >
            <div class="flex flex-col items-center gap-4">
              <!-- Upload Icon -->
              <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>

              <div>
                <button
                  @click="openFilePicker"
                  class="text-[#ac208e] font-semibold hover:underline"
                  type="button"
                >
                  Klik untuk memilih file
                </button>
                <span class="text-gray-500"> atau drag & drop</span>
              </div>

              <p class="text-sm text-gray-500">
                JPG, PNG, atau PDF (maksimal 5MB)
              </p>
            </div>

            <!-- Hidden file input -->
            <input
              ref="fileInputRef"
              type="file"
              class="hidden"
              accept="image/jpeg,image/png,image/jpg,application/pdf"
              @change="handleFileSelect"
            />
          </div>

          <!-- File Preview -->
          <div v-else class="border border-gray-200 rounded-xl p-4">
            <div class="flex items-center gap-4">
              <!-- File Icon -->
              <div class="flex-shrink-0 w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg
                  v-if="getFileIcon(selectedFile!.type) === 'image'"
                  class="w-6 h-6 text-[#ac208e]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <svg
                  v-else
                  class="w-6 h-6 text-[#ac208e]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>

              <!-- File Info -->
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ filePreview?.name }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ filePreview?.size }}
                </p>
              </div>

              <!-- Remove Button -->
              <button
                v-if="!isUploading"
                @click="removeFile"
                class="flex-shrink-0 text-red-500 hover:text-red-700 transition-colors"
                type="button"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>

            <!-- Upload Progress -->
            <div v-if="uploadProgress" class="mt-4">
              <div class="flex items-center justify-between text-sm mb-2">
                <span class="text-gray-600">Uploading...</span>
                <span class="text-[#ac208e] font-semibold">{{ uploadProgress.percentage }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-[#ac208e] h-2 rounded-full transition-all duration-300"
                  :style="{ width: `${uploadProgress.percentage}%` }"
                ></div>
              </div>
            </div>
          </div>

          <!-- Notes Input -->
          <div class="mt-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Catatan (Opsional)
            </label>
            <textarea
              v-model="notes"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#ac208e] focus:border-transparent resize-none"
              rows="3"
              placeholder="Tambahkan catatan tentang pembayaran Anda..."
              :disabled="isUploading"
            ></textarea>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-red-800">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="border-t border-gray-200 p-6">
          <div class="flex gap-4">
            <button
              @click="handleClose"
              class="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              :disabled="isUploading"
            >
              Batal
            </button>
            <button
              @click="handleUpload"
              class="flex-1 px-6 py-3 bg-[#ac208e] text-white rounded-lg font-medium hover:bg-[#8c1a72] transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
              :disabled="!canUpload"
            >
              {{ isUploading ? 'Mengupload...' : 'Upload Bukti' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
/* Additional custom styles if needed */
</style>
