<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm px-4"
    @click.self="handleClose">
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-6 border-b border-gray-200">
        <h2 class="text-lg font-bold text-gray-900">Syarat dan Ketentuan Pengembalian</h2>
        <button @click="handleClose" class="text-gray-400 hover:text-gray-600 transition-colors" aria-label="Tutup">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6">
        <div v-if="isLoading" class="flex justify-center items-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>

        <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-red-700">{{ error }}</p>
        </div>

        <div v-else
          class="prose max-w-none prose-headings:text-gray-900 prose-p:text-text-secondary prose-p:font-semibold prose-li:font-semibold prose-li:text-sm prose-p:text-sm/6 prose-li:text-text-secondary prose-strong:text-gray-900 prose-a:text-primary hover:prose-a:underline">
          <div v-if="policyContent" v-html="policyContent"></div>
          <div v-else class="text-gray-600">
            <h3 class="text-lg font-semibold mb-4">Kebijakan Pengembalian Barang</h3>
            <p class="mb-4">
              Kami menerima pengembalian barang dalam kondisi tertentu untuk memastikan kepuasan pelanggan.
              Harap membaca dengan seksama syarat dan ketentuan berikut sebelum mengajukan pengembalian.
            </p>

            <h4 class="font-semibold mt-6 mb-3">1. Periode Pengembalian</h4>
            <p class="mb-4">
              Pengembalian dapat dilakukan dalam waktu {{ eligibilityDays }} hari sejak tanggal pengiriman barang
              diterima.
            </p>

            <h4 class="font-semibold mt-6 mb-3">2. Kondisi Barang</h4>
            <ul class="list-disc pl-6 mb-4">
              <li>Barang masih dalam kondisi asli dan belum digunakan</li>
              <li>Label dan kemasan asli masih utuh</li>
              <li>Terdapat bukti pembelian (invoice/struk)</li>
              <li>Tidak ada kerusakan yang disebabkan oleh kesalahan pengguna</li>
            </ul>

            <h4 class="font-semibold mt-6 mb-3">3. Alasan Pengembalian yang Diterima</h4>
            <ul class="list-disc pl-6 mb-4">
              <li>Produk cacat atau rusak saat diterima</li>
              <li>Produk tidak sesuai dengan pesanan</li>
              <li>Ukuran atau warna tidak sesuai</li>
              <li>Kerusakan selama pengiriman</li>
            </ul>

            <h4 class="font-semibold mt-6 mb-3">4. Proses Pengembalian</h4>
            <ul class="list-disc pl-6 mb-4">
              <li>Ajukan pengembalian melalui halaman pesanan Anda</li>
              <li>Pilih alasan pengembalian dan unggah bukti pendukung (foto/video)</li>
              <li>Tim kami akan meninjau pengajuan dalam 1-2 hari kerja</li>
              <li>Setelah disetujui, Anda akan menerima instruksi untuk mengembalikan barang</li>
            </ul>

            <h4 class="font-semibold mt-6 mb-3">5. Metode Pengembalian Dana</h4>
            <p class="mb-4">
              Dana akan dikembalikan melalui metode yang Anda pilih (transfer bank atau tunai di koperasi).
              Proses pengembalian dana memakan waktu 5-7 hari kerja setelah barang diterima dan diverifikasi.
            </p>

            <h4 class="font-semibold mt-6 mb-3">6. Barang yang Tidak Dapat Dikembalikan</h4>
            <ul class="list-disc pl-6 mb-4">
              <li>Barang yang telah digunakan atau dicuci</li>
              <li>Barang tanpa label atau kemasan asli</li>
              <li>Barang yang rusak karena kesalahan pengguna</li>
              <li>Produk yang dijual dalam kondisi clearance/sale</li>
            </ul>

            <p class="mt-6 text-sm text-gray-500">
              Dengan melanjutkan proses pengembalian, Anda menyetujui syarat dan ketentuan di atas.
              Jika Anda memiliki pertanyaan, silakan hubungi layanan pelanggan kami.
            </p>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
        <button @click="handleClose"
          class="px-6 py-3 text-gray-700 font-semibold hover:bg-gray-100 rounded-lg transition-colors">
          Batal
        </button>
        <button @click="handleAccept"
          class="px-6 py-3 bg-primary text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
          :disabled="isLoading">
          Setuju & Lanjutkan
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useReturnsStore } from '@/stores/returns'

interface Props {
  isOpen: boolean
}

interface Emits {
  (e: 'accept'): void
  (e: 'close'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const returnsStore = useReturnsStore()

const isLoading = ref(false)
const error = ref<string | null>(null)
const policyContent = ref<string>('')
const eligibilityDays = ref(14) // Default value

onMounted(async () => {
  await loadPolicyContent()
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadPolicyContent()
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden'
  } else {
    // Restore body scroll when modal is closed
    document.body.style.overflow = ''
  }
})

async function loadPolicyContent() {
  try {
    isLoading.value = true
    error.value = null

    await returnsStore.fetchWebshopSettings()

    const settings = returnsStore.webshopSettings
    if (settings) {
      policyContent.value = settings.return_policy_description || ''
      eligibilityDays.value = settings.return_eligibility_days || 14
    }
  } catch (err) {
    console.error('Error loading policy:', err)
    error.value = 'Gagal memuat kebijakan pengembalian'
  } finally {
    isLoading.value = false
  }
}

function handleClose() {
  emit('close')
}

function handleAccept() {
  emit('accept')
}
</script>
