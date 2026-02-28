<template>
  <div class="voluntary-savings flex flex-col gap-6">
    <!-- Loading State -->
    <div v-if="savingsResource.loading" class="flex justify-center p-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
    <template v-else>
      <!-- Balance Card Container -->
      <div class="flex gap-4">
        <!-- Saldo Simpanan Sukarela Card -->
        <div class="w-full bg-background border border-border-solid rounded-2xl p-5 flex flex-col justify-between gap-6 shadow-sm">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white">
              <!-- Icon Simpanan -->
              <SavingIcon class="text-white w-8 h-8"></SavingIcon>
            </div>
            <div>
              <h3 class="text-text-default text-md !font-bold">Saldo Simpanan Sukarela</h3>
              <p class="text-sm text-text-secondary mt-1">Setoran simpanan sukarela bisa di setorkan kapan saja</p>
            </div>
          </div>
          <div class="flex items-center gap-3 justify-between">
            <span class="text-primary font-bold text-2xl font-semibold">{{ formatIDR(voluntaryBalance) }}</span>
            <div class="flex gap-2">
              <PrimaryButton variant="outline" @click="goToWithdrawal" class="flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20ZM10.75 4C10.75 3.58579 10.4142 3.25 10 3.25C9.58579 3.25 9.25 3.58579 9.25 4V4.31673C7.61957 4.60867 6.25 5.83361 6.25 7.5C6.25 9.41715 8.06278 10.75 10 10.75C11.3765 10.75 12.25 11.6557 12.25 12.5C12.25 13.3443 11.3765 14.25 10 14.25C8.62351 14.25 7.75 13.3443 7.75 12.5C7.75 12.0858 7.41421 11.75 7 11.75C6.58579 11.75 6.25 12.0858 6.25 12.5C6.25 14.1664 7.61957 15.3913 9.25 15.6833V16C9.25 16.4142 9.58579 16.75 10 16.75C10.4142 16.75 10.75 16.4142 10.75 16V15.6833C12.3804 15.3913 13.75 14.1664 13.75 12.5C13.75 10.5828 11.9372 9.25 10 9.25C8.62351 9.25 7.75 8.34427 7.75 7.5C7.75 6.65573 8.62351 5.75 10 5.75C11.3765 5.75 12.25 6.65573 12.25 7.5C12.25 7.91421 12.5858 8.25 13 8.25C13.4142 8.25 13.75 7.91421 13.75 7.5C13.75 5.83361 12.3804 4.60867 10.75 4.31673V4Z" fill="#AC208E"/>
                </svg>
                Pengajuan Pengambilan Saldo
              </PrimaryButton>
              <PrimaryButton @click="handleDepositClick" class="flex items-center gap-2">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M10 20C15.5228 20 20 15.5228 20 10C20 4.47715 15.5228 0 10 0C4.47715 0 0 4.47715 0 10C0 15.5228 4.47715 20 10 20ZM10.75 7C10.75 6.58579 10.4142 6.25 10 6.25C9.58579 6.25 9.25 6.58579 9.25 7L9.25 9.25002H7C6.58579 9.25002 6.25 9.58581 6.25 10C6.25 10.4142 6.58579 10.75 7 10.75H9.25V13C9.25 13.4142 9.58578 13.75 10 13.75C10.4142 13.75 10.75 13.4142 10.75 13L10.75 10.75H13C13.4142 10.75 13.75 10.4142 13.75 10C13.75 9.58581 13.4142 9.25002 13 9.25002H10.75V7Z" fill="white"/>
                </svg>
                Setor Simpanan Sukarela
              </PrimaryButton>
            </div>
          </div>
        </div>
      </div>

      <!-- Table Section Container -->
      <div class="flex flex-col gap-4 mt-4">
        <!-- Toolbar -->
        <div class="flex items-center justify-between">
          <h4 class="text-md font-bold text-text">Riwayat Transaksi Sukarela</h4>
          
          <!-- Action Buttons -->
          <button class="bg-background border border-border-solid text-text-secondary text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-background-soft transition-colors flex items-center gap-2 shadow-sm">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 15V3M12 15L8 11M12 15L16 11M2 17L2.25108 18.2554C2.58564 19.9282 3.86315 21 5.56708 21H18.4329C20.1368 21 21.4144 19.9282 21.7489 18.2554L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Download Tabel (PDF)
          </button>
        </div>

        <!-- Main Table -->
        <div class="border border-border-solid rounded-xl overflow-hidden shadow-sm bg-background">
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-secondary text-white text-sm font-medium">
                  <th class="py-4 px-6 w-16 text-center">
                     <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="2"/>
                     </svg>
                  </th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">No</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Tanggal</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Jenis Transaksi</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Nominal</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Status</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Metode Pembayaran</th>
                  <th class="py-4 px-6 text-center font-medium whitespace-nowrap">Aksi</th>
                </tr>
              </thead>
              <tbody class="text-sm" v-if="voluntarySavings.length > 0">
                <tr v-for="(row, index) in voluntarySavings" :key="row.name" class="border-b last:border-0 border-border-solid hover:bg-background-soft transition-colors text-text-secondary">
                  <td class="py-4 px-6 text-center">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="text-text-secondary">
                      <rect x="3" y="3" width="18" height="18" rx="4" stroke="currentColor" stroke-width="2"/>
                      <path v-if="row.status === 'Approved'" d="M8 12L11 15L16 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </td>
                  <td class="py-4 px-4">{{ index + 1 }}</td>
                  <td class="py-4 px-4">{{ formatDate(row.creation) }}</td>
                  <td class="py-4 px-4">
                    <span :class="row.transaction_type === 'Deposit' ? 'text-success' : 'text-danger'">
                      {{ row.transaction_type === 'Deposit' ? 'Setoran' : 'Penarikan' }}
                    </span>
                  </td>
                  <td class="py-4 px-4">{{ formatIDR(row.amount) }}</td>
                  <td class="py-4 px-4">
                    <div class="flex items-center gap-2">
                       <div class="w-2.5 h-2.5 rounded-full" :class="[
                          row.status === 'Approved' ? 'bg-success' : 
                          row.status === 'Pending Payment' ? 'bg-yellow-400' : 
                          (row.status === 'Pending Approval' || row.status === 'Draft') ? 'bg-orange-400' : 
                          'bg-red-500'
                        ]"></div>
                      <span class="font-medium" :class="[
                        row.status === 'Approved' ? 'text-success' : 
                        row.status === 'Pending Payment' ? 'text-yellow-600' : 
                        (row.status === 'Pending Approval' || row.status === 'Draft') ? 'text-orange-500' : 
                        'text-danger'
                      ]">{{ 
                        row.status === 'Approved' ? 'Selesai' : 
                        row.status === 'Pending Payment' ? 'Menunggu Pembayaran' : 
                        (row.status === 'Pending Approval' || row.status === 'Draft') ? 'Menunggu Persetujuan' :
                        'Ditolak' 
                      }}</span>
                    </div>
                  </td>
                  <td class="py-4 px-4">-</td>
                  <td class="py-4 px-6 text-center">
                    <button v-if="row.status === 'Approved' || row.status === 'Rejected'" class="text-primary hover:underline font-medium">Lihat Detail</button>
                    <button v-else-if="row.status === 'Pending Payment' && row.transaction_type === 'Deposit'" class="text-primary hover:underline font-medium" @click="handleResumePayment(row)">Lanjutkan Pembayaran</button>
                  </td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr>
                  <td colspan="8" class="py-8 text-center text-text-secondary">Belum ada transaksi simpanan sukarela.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { createResource } from 'frappe-ui';
import { formatIDR } from '@/utils/formatters';
import PrimaryButton from '../common/PrimaryButton.vue';
import SavingIcon from '../icons/SavingIcon.vue';

const router = useRouter();

// Fetch Savings Resource
const savingsResource = createResource({
  url: 'webshop.webshop.api.cooperative_payment.get_member_savings',
  auto: true
});

const savingsData = computed(() => savingsResource.data || {
  voluntary_saving_balance: 0,
  voluntary_savings: []
});

const voluntaryBalance = computed(() => savingsData.value.voluntary_saving_balance || 0);
const voluntarySavings = computed(() => savingsData.value.voluntary_savings || []);

// Format Date
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-';
  const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'long', year: 'numeric' };
  const d = new Date(dateStr);
  return d.toLocaleDateString('id-ID', options);
};

function goToWithdrawal() {
  router.push('/savings/withdrawal');
}

function handleDepositClick() {
  router.push('/savings/deposit');
}

const handleResumePayment = (row: any) => {
  if (row.payment_request) {
    router.push(`/savings/payment/${row.payment_request}`);
  } else {
    console.error('No payment request attached to this row', row);
  }
};
</script>
