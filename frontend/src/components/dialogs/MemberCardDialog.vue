<script setup lang="ts">
import { computed, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

interface Props {
  isOpen: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

const router = useRouter()
const authStore = useAuthStore()

// Format date to Indonesian format e.g., "05 Februari 2026"
const formatDate = (dateString: string | null) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return dateString
  
  return date.toLocaleDateString('id-ID', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

const memberStatus = computed(() => authStore.memberStatus || 'Tidak Diketahui')
const isActive = computed(() => memberStatus.value === 'Active')

// Status color mapping
const statusClass = computed(() => {
  if (isActive.value) return 'text-[#AC208E]'
  if (memberStatus.value === 'Pending Payment') return 'text-orange-500'
  if (memberStatus.value === 'Pending Approval') return 'text-blue-500'
  return 'text-gray-500'
})

// Handle escape key to close modal
const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.isOpen) {
    emit('close')
  }
}

const goToPayment = () => {
  emit('close')
  router.push('/member/payment')
}

// Prevent body scroll when modal is open
watch(
  () => props.isOpen,
  (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      document.addEventListener('keydown', handleEscape)
    } else {
      document.body.style.overflow = ''
      document.removeEventListener('keydown', handleEscape)
    }
  }
)

onUnmounted(() => {
  document.body.style.overflow = ''
  document.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/50"
        @click="emit('close')"
        aria-hidden="true"
      />
    </Transition>

    <!-- Modal Content -->
    <Transition name="modal-bounce">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        @click.stop
      >
        <div class="relative bg-white rounded-2xl shadow-xl w-full max-w-[600px] overflow-hidden flex flex-col p-6 sm:p-8 items-center gap-8">

          <div class="flex items-start justify-between w-full">
            <svg width="49" height="49" viewBox="0 0 49 49" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect width="48.6782" height="48.6782" rx="24.3391" fill="#AC208E"/>
              <path d="M34.088 16.356L26.3773 11.9036C25.1182 11.1767 23.5605 11.1767 22.2884 11.9036L14.5907 16.356C13.3316 17.083 12.5527 18.433 12.5527 19.8998V28.7787C12.5527 30.2326 13.3316 31.5826 14.5907 32.3225L22.3014 36.7749C23.5605 37.5018 25.1182 37.5018 26.3903 36.7749L34.101 32.3225C35.3601 31.5956 36.1389 30.2455 36.1389 28.7787V19.8998C36.126 18.433 35.3471 17.0959 34.088 16.356ZM24.3394 18.2902C26.0139 18.2902 27.3639 19.6402 27.3639 21.3147C27.3639 22.9892 26.0139 24.3393 24.3394 24.3393C22.6648 24.3393 21.3148 22.9892 21.3148 21.3147C21.3148 19.6532 22.6648 18.2902 24.3394 18.2902ZM27.8182 30.3883H20.8605C19.809 30.3883 19.1989 29.2201 19.7831 28.3503C20.6658 27.0393 22.3792 26.1566 24.3394 26.1566C26.2995 26.1566 28.0129 27.0393 28.8956 28.3503C29.4798 29.2071 28.8567 30.3883 27.8182 30.3883Z" fill="white"/>
            </svg>
            <!-- Close Button -->
            <button
              @click="emit('close')"
              class="flex h-10 w-10 items-center justify-center rounded-full transition-colors hover:bg-gray-100 z-20 text-gray-400 hover:text-gray-600"
              aria-label="Close"
            >
              <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Title Area -->
          <div class="w-full">
            <h2 class="text-[#1E1E1E] text-[18px] sm:text-xl !font-bold font-instrument mb-1.5 text-left">
              Kartu Anggota Koperasi Auliya
            </h2>
            <p class="text-[rgba(30,30,30,0.5)] text-sm sm:text-[15px] !font-semibold font-inter leading-relaxed text-left">
              Identitas resmi anggota koperasi yang dapat digunakan sebagai bukti keanggotaan aktif.
            </p>
          </div>

          <!-- Card Graphic -->
          <div class="w-full flex flex-col rounded-[16px] bg-[#F2F2F2] border-[2px] border-[rgba(30,30,30,0.1)] overflow-hidden shadow-sm">
            
            <!-- Card Header (Purple Area) -->
            <div class="w-full bg-[#AC208E] p-6 sm:p-8 flex flex-row items-center justify-between relative overflow-hidden">
              <!-- Background Circles -->
              <div class="absolute w-[160px] h-[160px] rounded-full bg-[rgba(255,255,255,0.1)] -top-[50px] right-[40px]"></div>
              <div class="absolute w-[200px] h-[200px] rounded-full bg-[rgba(255,255,255,0.1)] top-[10px] -left-[20px]"></div>
              
              <div class="flex flex-row gap-4 relative z-10 w-full">
                <div class="flex flex-col gap-1.5 flex-1 items-start">
                  <h3 class="text-white text-[16px] sm:text-[18px] font-bold font-instrument uppercase text-left w-full">
                    {{ authStore.memberFullName || authStore.user?.full_name || 'NAMA ANGGOTA' }}
                  </h3>
                  <div class="flex gap-2 justify-start w-full">
                    <p class="text-[rgba(255,255,255,0.8)] text-[14px] font-semibold font-inter text-left">
                      {{ authStore.memberName || 'KOP-AUL-XXXXXX' }}
                    </p>
                  </div>
                </div>
                
                <!-- Status Badge -->
                <div class="mt-1.5 flex justify-center items-start">
                  <div class="bg-white px-4 py-1.5 rounded-full flex items-center justify-center">
                    <span class="text-[14px] font-bold font-instrument" :class="statusClass">
                      {{ memberStatus }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Card Details (Gray Area) -->
            <div class="w-full p-6 sm:p-8 flex flex-col gap-6">
              <div class="w-full flex flex-row gap-4">
                <div class="flex flex-col gap-2 w-1/2">
                  <span class="text-[13px] font-semibold text-[rgba(30,30,30,0.5)] font-inter">Nomor Anggota</span>
                  <span class="text-sm sm:text-base !font-bold text-[#1E1E1E] font-instrument">{{ authStore.memberName || '-' }}</span>
                </div>
                <div class="flex flex-col gap-2 w-1/2 items-end">
                  <span class="text-[13px] font-semibold text-[rgba(30,30,30,0.5)] font-inter text-right">Tanggal Bergabung</span>
                  <span class="text-sm sm:text-base !font-bold text-[#1E1E1E] font-instrument text-right">{{ formatDate(authStore.memberJoinDate) }}</span>
                </div>
              </div>
              
              <div class="w-full flex flex-row gap-4">
                <div class="flex flex-col gap-2 w-1/2">
                  <span class="text-[13px] font-semibold text-[rgba(30,30,30,0.5)] font-inter">Kategori</span>
                  <span class="text-sm sm:text-base !font-bold text-[#1E1E1E] font-instrument">{{ authStore.memberCategory || '-' }}</span>
                </div>
                <div class="flex flex-col gap-2 w-1/2 items-end">
                  <span class="text-[13px] font-semibold text-[rgba(30,30,30,0.5)] font-inter text-right">Status</span>
                  <span class="text-sm sm:text-base !font-bold text-[#1E1E1E] font-instrument text-right">{{ memberStatus }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer Note -->
          <div class="w-full text-left -mt-2 flex flex-col gap-3">
            <p class="text-[rgba(30,30,30,0.5)] text-[13px] font-semibold font-inter">
              *Berlaku selama status anggota aktif.
            </p>

            <PrimaryButton 
              v-if="['Pending Payment', 'Pending Approval'].includes(memberStatus)"
              class="w-full py-2.5 text-[14px]"
              @click="goToPayment"
            >
              Lanjutkan Pembayaran
            </PrimaryButton>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>

/* Fade transition for backdrop */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Bounce transition for modal */
.modal-bounce-enter-active {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.modal-bounce-leave-active {
  transition: all 0.3s cubic-bezier(0.6, -0.28, 0.735, 0.045);
}

.modal-bounce-enter-from,
.modal-bounce-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
