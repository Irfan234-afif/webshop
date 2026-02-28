<template>
  <div class="history-tab flex flex-col gap-6">
    <!-- Loading State -->
    <div v-if="isLoading && items.length === 0" class="flex justify-center p-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <template v-else>
      <!-- Toolbar -->
      <div class="flex items-center justify-between">
        <!-- Filters -->
        <div class="flex items-center gap-6">
          <!-- Jenis Simpanan Filter -->
          <div class="relative border border-border-solid rounded-xl px-4 py-2.5 flex items-center gap-3 bg-background group shadow-sm">
            <span class="text-text-secondary text-sm font-semibold">Jenis Simpanan :</span>
            <select v-model="selectedSavingType" class="bg-transparent text-sm font-semibold text-text-secondary focus:outline-none appearance-none cursor-pointer pr-4">
              <option value="">Semua</option>
              <option value="Simpanan Pokok">Simpanan Pokok</option>
              <option value="Simpanan Wajib">Simpanan Wajib</option>
              <option value="Simpanan Sukarela">Simpanan Sukarela</option>
            </select>
            <svg width="11" height="6" viewBox="0 0 11 6" fill="none" xmlns="http://www.w3.org/2000/svg" class="text-text pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
              <path d="M1 1L5.5 5L10 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- Jenis Pembayaran Filter -->
          <div class="relative border border-border-solid rounded-xl px-4 py-2.5 flex items-center gap-3 bg-background group shadow-sm">
            <span class="text-text-secondary text-sm font-semibold">Jenis Pembayaran :</span>
            <select v-model="selectedTransactionKind" class="bg-transparent text-sm font-semibold text-text-secondary focus:outline-none appearance-none cursor-pointer pr-4">
              <option value="">Semua</option>
              <option value="Pembayaran">Pembayaran</option>
              <option value="Setoran">Setoran</option>
              <option value="Pengambilan">Pengambilan</option>
              <option value="Simpanan Pokok">Simpanan Pokok</option>
            </select>
            <svg width="11" height="6" viewBox="0 0 11 6" fill="none" xmlns="http://www.w3.org/2000/svg" class="text-text pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
              <path d="M1 1L5.5 5L10 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
        </div>

        <!-- Search & Download -->
        <div class="flex items-center gap-4">
          <!-- Search Input -->
          <div class="relative border border-border-solid rounded-xl px-4 py-2.5 flex items-center gap-4 bg-background shadow-sm w-[340px]">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="text-text-secondary shrink-0">
              <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="1.5"/>
              <path d="M20 20L17 17" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Cari jenis pesanan, atau tanggal"
              class="bg-transparent text-sm font-semibold text-text placeholder-text-secondary/50 focus:outline-none w-full"
            />
          </div>

          <!-- Download Button -->
          <button class="bg-primary text-white text-sm font-bold px-4 py-2.5 rounded-lg hover:bg-primary/90 transition-colors flex items-center gap-3 shadow-sm whitespace-nowrap">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3V15M12 15L8 11M12 15L16 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L2.25108 18.2554C2.58564 19.9282 3.86315 21 5.56708 21H18.4329C20.1368 21 21.4144 19.9282 21.7489 18.2554L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Download Riwayat (PDF)
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="border border-border-solid rounded-xl overflow-hidden shadow-sm bg-background">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-secondary text-white text-sm font-bold">
                <th class="py-4 px-6 w-16 font-bold whitespace-nowrap">No</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Periode</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Nominal</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Jatuh Tempo</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Simpanan</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Jenis</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap">Tanggal Bayar/Setor</th>
                <th class="py-4 px-4 font-bold whitespace-nowrap text-right">Metode Pembayaran</th>
              </tr>
            </thead>
            <tbody class="text-sm font-bold" v-if="filteredItems.length > 0">
              <tr
                v-for="(item, index) in filteredItems"
                :key="`${item.type}-${item.reference_name}-${item.date}`"
                class="border-b last:border-0 border-border-solid/10 hover:bg-background-soft transition-colors text-text"
              >
                <td class="py-5 px-6 w-16">{{ totalCount - ((currentPage - 1) * pageLength) - index }}</td>
                <td class="py-5 px-4">{{ item.period || '-' }}</td>
                <td class="py-5 px-4" :class="item.type === 'voluntary_withdrawal' ? 'text-danger' : ''">
                  {{ item.type === 'voluntary_withdrawal' ? '- ' : '' }}{{ formatIDR(item.amount) }}
                </td>
                <td class="py-5 px-4">{{ item.due_date ? formatDate(item.due_date) : '-' }}</td>
                <td class="py-5 px-4">{{ item.saving_type }}</td>
                <td class="py-5 px-4">{{ item.transaction_kind }}</td>
                <td class="py-5 px-4">{{ item.payment_date ? formatDate(item.payment_date) : '-' }}</td>
                <td class="py-5 px-4 text-right">{{ item.payment_method }}</td>
              </tr>
            </tbody>
            <tbody v-else>
              <tr>
                <td colspan="8" class="py-16 text-center">
                  <div class="flex flex-col items-center justify-center">
                    <div class="bg-primary/5 text-primary w-16 h-16 rounded-full flex items-center justify-center mb-4">
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 8V12L15 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                      </svg>
                    </div>
                    <h3 class="text-lg poppins-semibold text-text mb-2">Belum Ada Riwayat</h3>
                    <p class="text-sm text-text-secondary max-w-sm">Anda belum memiliki riwayat transaksi simpanan. Mulai bertransaksi untuk melihat riwayat di sini.</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="flex justify-center">
        <button
          class="bg-background border border-border-solid text-text-secondary text-sm font-medium px-6 py-2.5 rounded-lg hover:bg-background-soft transition-colors shadow-sm"
          :disabled="isLoading"
          @click="loadMore"
        >
          <span v-if="isLoading">Memuat...</span>
          <span v-else>Muat Lebih Banyak</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

import { formatIDR } from '@/utils/formatters'
import { getSavingsHistory } from '@/utils/savingPaymentApi'

import type { SavingsHistoryItem, SavingsHistorySavingType, SavingsHistoryTransactionKind } from '@/types/cooperative'

const selectedSavingType = ref<SavingsHistorySavingType | ''>('')
const selectedTransactionKind = ref<SavingsHistoryTransactionKind | ''>('')
const searchQuery = ref('')
const items = ref<SavingsHistoryItem[]>([])
const isLoading = ref(false)
const hasMore = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageLength = 20

const fetchHistory = async (page = 1, append = false) => {
  isLoading.value = true
  try {
    const result = await getSavingsHistory(
      page,
      pageLength,
      selectedSavingType.value || undefined,
      selectedTransactionKind.value || undefined
    )
    if (append) {
      items.value = [...items.value, ...result.items]
    } else {
      items.value = result.items
    }
    hasMore.value = result.has_more
    currentPage.value = result.page
    totalCount.value = result.total_count
  } catch {
    items.value = append ? items.value : []
    hasMore.value = false
  } finally {
    isLoading.value = false
  }
}

const loadMore = () => {
  fetchHistory(currentPage.value + 1, true)
}

// Re-fetch when filters change
watch([selectedSavingType, selectedTransactionKind], () => {
  fetchHistory(1, false)
}, { immediate: true })

// Client-side search filtering
const filteredItems = computed(() => {
  if (!searchQuery.value.trim()) return items.value
  const query = searchQuery.value.toLowerCase()
  return items.value.filter((item) => {
    return (
      (item.period && item.period.toLowerCase().includes(query)) ||
      item.saving_type.toLowerCase().includes(query) ||
      item.transaction_kind.toLowerCase().includes(query) ||
      item.payment_method.toLowerCase().includes(query) ||
      (item.payment_date && item.payment_date.includes(query))
    )
  })
})

// Format Date
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'long', year: 'numeric' }
  const d = new Date(dateStr)
  return d.toLocaleDateString('id-ID', options)
}
</script>
