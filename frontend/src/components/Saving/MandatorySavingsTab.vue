<template>
  <div class="mandatory-savings flex flex-col gap-6">
    <!-- Loading State -->
    <div v-if="savingsResource.loading" class="flex justify-center p-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
    <template v-else>
      <!-- Balance & Billing Section Container -->
      <div class="flex flex gap-4">
        <!-- Saldo Simpanan Wajib Card -->
        <div class="flex-auto w-[90%] bg-background border border-border-solid rounded-2xl p-5 flex flex-col justify-between gap-6 shadow-sm">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-primary flex items-center justify-center text-white">
              <!-- Icon Simpanan -->
              <SavingIcon class="text-white w-8 h-8"></SavingIcon>
            </div>
            <div>
              <h3 class="text-text-default text-md !font-bold">Saldo Simpanan Wajib</h3>
              <p class="text-sm text-text-secondary mt-1">Jumlah saldo simpanan anda saat ini</p>
            </div>
          </div>
          <div class="flex items-center gap-3 justify-between">
            <span class="text-primary font-bold text-2xl font-semibold">{{ formatIDR(mandatoryBalance) }}</span>
            <!-- Info Circle -->
            <button class="text-primary hover:text-primary/80 transition-colors">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" stroke-width="1.5"/>
                <path d="M12 11V16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12.0498 8V8.1" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Tagihan Periode Card -->
        <div class="flex-auto bg-background border border-border-solid rounded-2xl p-5 flex flex-col justify-between gap-6 shadow-sm">
          <div>
            <h3 class="text-text-default text-md !font-bold">
              {{
                selectedRows.length > 0
                  ? `Tagihan Periode Terpilih (${selectedRows.length} Bulan)`
                  : `Tagihan Periode ${currentBilling ? currentBilling.month_name : '-'} ${selectedYear}`
              }}
            </h3>
            <p class="text-sm text-text-secondary mt-1">
              {{
                selectedRows.length > 0
                  ? `Pembayaran kumulatif untuk ${selectedRows.length} bulan terpilih`
                  : (currentBilling ? 'Tagihan Simpanan Wajib akan di terbitkan setiap tanggal 28 pada akhir bulan' : 'Anda tidak memiliki tagihan bulan ini')
              }}
            </p>
          </div>
          <div class="flex items-center justify-between gap-6">
            <span class="text-primary font-bold text-xl font-semibold">
              {{ selectedRows.length > 0 ? formatIDR(selectedRows.reduce((sum, row) => sum + row.amount, 0)) : (currentBilling ? formatIDR(currentBilling.amount) : 'Rp 0') }}
            </span>
            <template v-if="selectedRows.length > 0">
              <PrimaryButton v-if="selectedRows.some(r => r.status === 'Pending Payment')" @click="handleResumePayment(selectedRows.find(r => r.status === 'Pending Payment'))">
                Lanjutkan Pembayaran
              </PrimaryButton>
              <PrimaryButton v-else @click="handlePaymentClick(selectedRows)">
                Bayar Sekarang
              </PrimaryButton>
            </template>
            <template v-else-if="currentBilling">
               <PrimaryButton v-if="currentBilling.status === 'Pending Payment'" @click="handleResumePayment(currentBilling)">
                Lanjutkan Pembayaran
              </PrimaryButton>
              <PrimaryButton v-else @click="handlePaymentClick(currentBilling)">
                Bayar Sekarang
              </PrimaryButton>
            </template>
          </div>
        </div>
      </div>

      <!-- Table Section Container -->
      <div class="flex flex-col gap-4 mt-4">
        <!-- Toolbar -->
        <div class="flex items-center justify-between">
          <!-- Year filter -->
          <div class="relative border border-border-solid rounded-xl px-4 py-2.5 flex items-center gap-3 bg-background group shadow-sm">
            <span class="text-text-secondary text-sm font-medium">Tahun :</span>
            <select v-model="selectedYear" class="bg-transparent text-sm font-medium text-text focus:outline-none appearance-none cursor-pointer pr-4">
              <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
            </select>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="text-text-secondary pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
              <path d="M19 9L12 16L5 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          
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
                    <input type="checkbox"
                           class="w-4 h-4 rounded border-border-solid text-primary focus:ring-primary cursor-pointer"
                           :checked="isAllSelected"
                           @change="toggleAll" />
                  </th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">No</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Periode</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Nominal</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Jatuh Tempo</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Status Bayar</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Tanggal Bayar</th>
                  <th class="py-4 px-4 font-medium whitespace-nowrap">Metode Pembayaran</th>
                  <th class="py-4 px-6 text-center font-medium whitespace-nowrap">Aksi</th>
                </tr>
              </thead>
              <tbody class="text-sm" v-if="monthlyDetails.length > 0">
                <tr v-for="(row, index) in monthlyDetails" :key="row.name" class="border-b last:border-0 border-border-solid hover:bg-background-soft transition-colors text-text-secondary">
                  <td class="py-4 px-6 text-center">
                    <input v-if="row.status === 'Unpaid' || row.status === 'Pending Payment'"
                           type="checkbox"
                           :value="row"
                           v-model="selectedRows"
                           class="w-4 h-4 rounded border-border-solid text-primary focus:ring-primary cursor-pointer" />
                    <input v-else-if="row.status === 'Paid'"
                           type="checkbox"
                           disabled
                           checked
                           class="w-4 h-4 rounded border-border-solid text-primary focus:ring-primary opacity-50 cursor-not-allowed" />
                    <input v-else
                           type="checkbox"
                           disabled
                           class="w-4 h-4 rounded border-border-solid text-primary focus:ring-primary opacity-50 cursor-not-allowed" />
                  </td>
                  <td class="py-4 px-4">{{ index + 1 }}</td>
                  <td class="py-4 px-4">{{ row.month_name }} {{ selectedYear }}</td>
                  <td class="py-4 px-4">{{ formatIDR(row.amount) }}</td>
                  <!-- <td class="py-4 px-4">28 {{ row.month_name }} {{ selectedYear }}</td> -->
                  <td class="py-4 px-4">{{ formatDate(new Date(selectedYear, row.month, 0)) }}</td> 
                  <td class="py-4 px-4">
                    <div class="flex items-center gap-2">
                      <div class="w-2.5 h-2.5 rounded-full" :class="[row.status === 'Paid' ? 'bg-success' : 'bg-yellow-400']"></div>
                      <span class="font-medium" :class="[row.status === 'Paid' ? 'text-success' : 'text-yellow-600']">{{ row.status === 'Paid' ? 'Lunas' : (row.status === 'Pending Payment' ? 'Menunggu Verifikasi' : 'Belum Bayar') }}</span>
                    </div>
                  </td>
                  <td class="py-4 px-4">{{ row.payment_date ? formatDate(row.payment_date) : '-' }}</td>
                  <td class="py-4 px-4">-</td>
                  <td class="py-4 px-6 text-center">
                    <button v-if="row.status === 'Paid'" class="text-primary hover:underline font-medium">Lihat Detail</button>
                    <button v-else-if="row.status === 'Pending Payment'" class="text-primary hover:underline font-medium" @click="handleResumePayment(row)">Lanjutkan Pembayaran</button>
                    <button v-else class="text-primary hover:underline font-medium" @click="handlePaymentClick(row)">Bayar Sekarang</button>
                  </td>
                </tr>
              </tbody>
              <tbody v-else>
                <tr>
                  <td colspan="9" class="py-8 text-center text-text-secondary">Belum ada data simpanan wajib untuk tahun ini.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <!-- Payment Modal -->
      <SavingPaymentModal
        v-if="currentYearSaving"
        :is-open="isPaymentModalOpen"
        :saving-name="currentYearSaving.name"
        :selected-rows="selectedRowsForPayment"
        @close="closePaymentModal"
        @payment-initiated="handlePaymentInitiated"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { createResource } from 'frappe-ui';
import { formatIDR } from '@/utils/formatters';
import PrimaryButton from '../common/PrimaryButton.vue';
import SavingIcon from '../icons/SavingIcon.vue';
import SavingPaymentModal from './SavingPaymentModal.vue';

// Fetch Savings Resource
const router = useRouter();

const savingsResource = createResource({
  url: 'webshop.webshop.api.cooperative_payment.get_member_savings',
  auto: true
});

const savingsData = computed(() => savingsResource.data || {
  mandatory_saving_balance: 0,
  mandatory_savings: []
});

const mandatoryBalance = computed(() => savingsData.value.mandatory_saving_balance || 0);

// Year filter
const availableYears = computed(() => {
  return savingsData.value.mandatory_savings.map((s: any) => s.year).sort((a: any, b: any) => b - a);
});
const selectedYear = ref(new Date().getFullYear());

watch(availableYears, (newYears) => {
  if (newYears.length > 0 && !newYears.includes(selectedYear.value)) {
    selectedYear.value = newYears[0];
  }
});

const currentYearSaving = computed(() => {
  return savingsData.value.mandatory_savings.find((s: any) => s.year === selectedYear.value) || null;
});

const monthlyDetails = computed(() => {
  if (!currentYearSaving.value) return [];
  return currentYearSaving.value.monthly_details;
});

const selectedRows = ref<any[]>([]);

watch(selectedYear, () => {
  selectedRows.value = [];
});

const checkableRows = computed(() => {
  return monthlyDetails.value.filter((r: any) => r.status === 'Unpaid' || r.status === 'Pending Payment');
});

const isAllSelected = computed(() => {
  return checkableRows.value.length > 0 && selectedRows.value.length === checkableRows.value.length;
});

const toggleAll = (event: Event) => {
  const isChecked = (event.target as HTMLInputElement).checked;
  if (isChecked) {
    selectedRows.value = [...checkableRows.value];
  } else {
    selectedRows.value = [];
  }
};

// Calculate current billing (basically first unpaid/pending month)
const currentBilling = computed(() => {
  if (!currentYearSaving.value) return null;
  const unpaid = currentYearSaving.value.monthly_details.find((d: any) => d.status === 'Unpaid' || d.status === 'Pending Payment');
  return unpaid;
});

// Format Date
const formatDate = (dateStr: string | Date) => {
  if (!dateStr) return '-';
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: 'long', year: 'numeric' };
  const d = new Date(dateStr);
  return d.toLocaleDateString('id-ID', options);
};

// Payment Modal State
const isPaymentModalOpen = ref(false);
const selectedRowsForPayment = ref<any[]>([]);

// Handle Payment click
const handlePaymentClick = (rowOrRows: any) => {
  if (Array.isArray(rowOrRows)) {
    selectedRowsForPayment.value = rowOrRows;
  } else {
    selectedRowsForPayment.value = [rowOrRows];
  }
  isPaymentModalOpen.value = true;
};

const closePaymentModal = () => {
  isPaymentModalOpen.value = false;
  selectedRowsForPayment.value = [];
};

const handlePaymentInitiated = (prName: string) => {
  closePaymentModal();
  savingsResource.reload();
};

const handleResumePayment = (row: any) => {
  if (row.payment_request) {
    router.push(`/savings/payment/${row.payment_request}`);
  } else {
    console.error('No payment request attached to this row', row);
  }
};
</script>
