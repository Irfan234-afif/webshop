<template>
  <DefaultLayout>
    <!-- Page Header -->
    <div class="bg-primary pt-8 pb-20">
      <Container>
        <div class="text-white">
          <h1 class="text-3xl font-bold mb-2">Keanggotaan Koperasi</h1>
          <p class="text-purple-100 max-w-2xl">
            Kelola keanggotaan dan simpanan koperasi Anda di sini.
          </p>
        </div>
      </Container>
    </div>

    <Container class="-mt-12 relative z-10 mb-20">
      <!-- Loading State -->
      <div v-if="cooperativeStore.isLoading" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-12 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p class="text-gray-500">Memuat status keanggotaan...</p>
      </div>

      <!-- Not Registered State -->
      <div v-else-if="!status?.is_member || status?.status === 'Not Registered'" class="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 md:p-12 text-center">
        <div class="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg class="w-10 h-10 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Belum Terdaftar sebagai Anggota</h2>
        <p class="text-gray-600 max-w-xl mx-auto mb-8 leading-relaxed">
          Nikmati berbagai keuntungan eksklusif seperti Sisa Hasil Usaha (SHU), pinjaman dengan bunga ringan, dan layanan prioritas dengan menjadi anggota Koperasi.
        </p>
        <router-link to="/member/register" class="inline-flex items-center justify-center bg-primary text-white font-bold py-4 px-8 rounded-xl hover:bg-opacity-90 transition-colors shadow-lg shadow-purple-200">
          Daftar Sekarang
        </router-link>
      </div>

      <!-- Application in Progress / Existing Member -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <!-- Left Column: Status Card -->
        <div class="lg:col-span-1 space-y-6">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="p-6 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
              <h3 class="font-bold text-gray-900">Status Keanggotaan</h3>
              <span :class="statusBadgeClass" class="px-3 py-1 text-xs font-semibold rounded-full border">
                {{ statusLabel }}
              </span>
            </div>
            
            <div class="p-6">
              <div class="text-center mb-6">
                <div class="w-20 h-20 bg-gray-100 rounded-full mx-auto mb-4 border-4 border-white shadow-md flex items-center justify-center overflow-hidden">
                  <svg class="w-10 h-10 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 20.993V24H0v-2.996A14.977 14.977 0 0112.004 15c4.904 0 9.26 2.354 11.996 5.993zM16.002 8.999a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                </div>
                <h4 class="font-bold text-lg text-gray-900">{{ status?.name || 'Member' }}</h4>
                <p class="text-sm text-gray-500 mt-1">ID: {{ status?.name || '-' }}</p>
              </div>

              <!-- Pending Payment Call to Action -->
              <div v-if="status?.status === 'Pending Payment'" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center mt-6">
                <p class="text-sm text-amber-800 font-medium mb-3">Selesaikan pembayaran pendaftaran Anda untuk melanjutkan proses.</p>
                <router-link to="/member/payment" class="block w-full bg-amber-500 text-white font-bold py-2.5 px-4 rounded-lg hover:bg-amber-600 transition-colors text-sm shadow-sm">
                  Lakukan Pembayaran
                </router-link>
              </div>

              <!-- Pending Approval Note -->
              <div v-if="status?.status === 'Pending Approval'" class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center mt-6">
                <p class="text-sm text-blue-800 font-medium mb-1">Menunggu Persetujuan</p>
                <p class="text-xs text-blue-600">Terima kasih telah membayar. Pengajuan Anda sedang direview oleh pengurus.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Savings Details (if active) -->
        <div v-if="status?.status === 'Active'" class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h3 class="font-bold text-gray-900 text-lg mb-6">Ringkasan Simpanan</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-purple-50 rounded-xl p-5 border border-purple-100 flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600 mb-1">Simpanan Pokok</p>
                  <p class="text-xl font-bold text-primary">{{ formatCurrency(status?.principal_saving_amount || 0) }}</p>
                </div>
                <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm text-primary">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
                </div>
              </div>

              <div class="bg-blue-50 rounded-xl p-5 border border-blue-100 flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600 mb-1">Simpanan Wajib</p>
                  <p class="text-xl font-bold text-blue-700">{{ formatCurrency(status?.mandatory_saving_amount || 0) }}</p>
                </div>
                <div class="w-10 h-10 bg-white rounded-full flex items-center justify-center shadow-sm text-blue-500">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
              </div>
            </div>
            
            <div class="mt-8 pt-6 border-t border-gray-100">
              <h4 class="font-bold text-gray-900 mb-4">Informasi Penting</h4>
              <ul class="text-sm text-gray-600 space-y-2 list-disc pl-5">
                <li>Simpanan Wajib dibayarkan setiap bulannya untuk mempertahankan status keanggotaan aktif.</li>
                <li>Sisa Hasil Usaha (SHU) dibagikan pada akhir tahun buku berjalan.</li>
                <li>Simpanan Pokok hanya dapat ditarik jika anggota memutuskan untuk keluar dari Koperasi.</li>
              </ul>
            </div>
          </div>
        </div>

      </div>
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useCooperativeStore } from '@/stores/cooperative'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'

const cooperativeStore = useCooperativeStore()
const status = computed(() => cooperativeStore.membershipStatus)

onMounted(async () => {
  await cooperativeStore.fetchMembershipStatus()
})

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency',
    currency: 'IDR',
    minimumFractionDigits: 0
  }).format(amount)
}

const statusBadgeClass = computed(() => {
  const s = status.value?.status
  if (s === 'Active') return 'bg-green-100 text-green-700 border-green-200'
  if (s === 'Pending Payment') return 'bg-amber-100 text-amber-700 border-amber-200'
  if (s === 'Pending Approval') return 'bg-blue-100 text-blue-700 border-blue-200'
  if (s === 'Draft') return 'bg-gray-100 text-gray-700 border-gray-200'
  if (s === 'Rejected') return 'bg-red-100 text-red-700 border-red-200'
  return 'bg-gray-100 text-gray-700 border-gray-200'
})

const statusLabel = computed(() => {
  const s = status.value?.status
  if (s === 'Active') return 'Aktif'
  if (s === 'Pending Payment') return 'Menunggu Pembayaran'
  if (s === 'Pending Approval') return 'Menunggu Persetujuan'
  if (s === 'Draft') return 'Draft'
  if (s === 'Rejected') return 'Ditolak'
  return s || 'Menunggu'
})
</script>
