<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import { storeToRefs } from 'pinia'
import UserRoundedIcon from '@/components/icons/UserRoundedIcon.vue'
import CheckCircleIcon from '@/components/icons/CheckCircleIcon.vue'
import BillIcon from '@/components/icons/BillIcon.vue'
import CartLargeIcon from '@/components/icons/CartLargeIcon.vue'
import BillListIcon from '@/components/icons/BillListIcon.vue'
import InfoCircleIcon from '@/components/icons/InfoCircleIcon.vue'
import UserCircleIcon from '@/components/icons/UserCircleIcon.vue'
import LogoutIcon from '@/components/icons/LogoutIcon.vue'
import ArrowRightIcon from '@/components/icons/ArrowRightIcon.vue'
import UniformIcon from '@/components/icons/UniformIcon.vue'
import WishlistIcon from '@/components/icons/WishlistIcon.vue'
import CartIcon from '../icons/CartIcon.vue'

interface MenuItem {
  id: string
  label: string
  icon: string
  badge?: number
  link?: string
  onClick?: () => void
}

const authStore = useAuthStore()
const cartStore = useCartStore()
const { students, activeStudent } = storeToRefs(cartStore)

const menuItems = computed<MenuItem[]>(() => {
  const allItems: (MenuItem & { requiresAuth?: boolean })[] = [
    { id: 'orders', label: 'Pesanan', icon: 'bill', badge: 3, link: '/orders', requiresAuth: true },
    { id: 'products', label: 'Produk', icon: 'uniform', link: '/products' },
    { id: 'wishlist', label: 'Wishlist', icon: 'wishlist', link: '/wishlist', requiresAuth: true },
    { id: 'contact', label: 'Kontak', icon: 'info', link: '#' },
    { id: 'cart', label: 'Keranjang', icon: 'cart', badge: 10, link: '/cart', requiresAuth: true },
    { id: 'bills', label: 'Tagihan', icon: 'bill-list', badge: 2, link: '/bills', requiresAuth: true },
    { id: 'help', label: 'Bantuan', icon: 'info', link: '/' },
    { id: 'account', label: 'Pengaturan Akun & Data Siswa', icon: 'user-circle', link: '/profile', requiresAuth: true },
    { id: 'logout', label: 'Log Out', icon: 'logout', onClick: () => handleLogout(), requiresAuth: true },
    { id: 'login', label: 'Log In', icon: 'user-circle', link: '/login', requiresAuth: false }
  ]

  if (authStore.isAuthenticated) {
    return allItems.filter(item => item.requiresAuth !== false)
  } else {
    return allItems.filter(item => !item.requiresAuth)
  }
})

const emit = defineEmits<{
  selectStudent: [studentId: string]
  logout: []
}>()

const selectStudent = (studentId: string) => {
  emit('selectStudent', studentId)
}

const handleLogout = () => {
  emit('logout')
}
</script>

<template>
  <div class="flex flex-col w-full">
    <!-- Header Section -->
    <div class="bg-white flex flex-col gap-4 p-8 border-b-[1.5px] border-[rgba(30,30,30,0.1)]">
      <p class="font-bold text-sm text-[#1e1e1e] capitalize">Menu & Siswa</p>
      <p class="text-[13px] text-[rgba(30,30,30,0.5)] font-semibold leading-[22px]">
        Semua data pesanan, keranjang, dan tagihan akan menyesuaikan dengan anak yang dipilih.
      </p>
    </div>

    <!-- Students Section -->
    <div class="bg-white flex flex-col p-8 border-b-[1.5px] border-[rgba(30,30,30,0.1)]">
      <div class="flex flex-col">
        <!-- Active Student -->
        <button v-for="(student, index) in students" :key="student.name" :class="[
          'flex gap-6 items-center p-6 border-[1.5px] border-[rgba(30,30,30,0.1)] transition-colors',
          student.name === activeStudent ? 'bg-muted' : 'bg-muted hover:bg-[rgba(242,242,242,1)]',
          index === 0 ? 'rounded-t-xl' : '',
          index === students.length - 1 ? 'rounded-b-xl border-t-0' : 'border-t-0'
        ]" @click="selectStudent(student.name)">
          <div :class="[
            'w-[38px] h-[38px] rounded-full flex items-center justify-center overflow-hidden',
            student.name === activeStudent ? 'bg-primary' : 'bg-[#757575]'
          ]">
            <UserRoundedIcon :class="[
              'w-5 h-5',
              student.name === activeStudent ? 'text-white' : 'text-white'
            ]" />
          </div>
          <div class="flex flex-col flex-1 items-start">
            <p class="font-bold text-sm text-[#1e1e1e] capitalize">{{ student.student_name }}</p>
            <p v-if="student.school_unit" class="text-[13px] text-[rgba(30,30,30,0.5)] font-semibold">
              {{ student.school_unit }}
            </p>
          </div>
          <CheckCircleIcon :filled="student.name === activeStudent" class="w-6 h-6" />
        </button>
      </div>
    </div>

    <!-- Menu Items Section -->
    <div class="bg-white flex flex-col p-8 pb-8">
      <div class="flex flex-col">
        <template v-for="(item, index) in menuItems">
          <button v-if="!item.link" :class="[
            'flex items-center justify-between p-6 h-[68px] border-[1.5px] border-[rgba(30,30,30,0.1)] bg-white hover:bg-[rgba(242,242,242,0.3)] transition-colors cursor-pointer',
            index === 0 ? 'rounded-t-xl' : '',
            index === menuItems.length - 1 ? 'rounded-b-xl border-t-0' : 'border-t-0'
          ]" @click="item.onClick?.()">
            <div class="flex gap-4 items-center">
              <BillIcon v-if="item.icon === 'bill'" class="w-6 h-6" />
              <CartIcon v-else-if="item.icon === 'cart'" class="w-6 h-6 text-primary" />
              <BillListIcon v-else-if="item.icon === 'bill-list'" class="w-6 h-6" />
              <InfoCircleIcon v-else-if="item.icon === 'info'" class="w-6 h-6" />
              <UserCircleIcon v-else-if="item.icon === 'user-circle'" class="w-6 h-6" />
              <LogoutIcon v-else-if="item.icon === 'logout'" class="w-6 h-6" />
              <UniformIcon v-else-if="item.icon === 'uniform'" class="w-6 h-6" />
              <WishlistIcon v-else-if="item.icon === 'wishlist'" class="w-6 h-6 text-primary" />
              <p class="font-bold text-sm text-[#1e1e1e] capitalize">{{ item.label }}</p>
            </div>
            <div class="flex gap-6 items-center">
              <div v-if="item.badge" class="bg-[#8dc73c] rounded-full w-6 h-6 flex items-center justify-center">
                <p class="text-[13px] text-white font-semibold">{{ item.badge }}</p>
              </div>
              <ArrowRightIcon class="w-4 h-4" />
            </div>
          </button>
          <router-link v-else :to="item.link" :class="[
            'flex items-center justify-between p-6 h-[68px] border-[1.5px] border-[rgba(30,30,30,0.1)] bg-white hover:bg-[rgba(242,242,242,0.3)] transition-colors',
            index === 0 ? 'rounded-t-xl' : '',
            index === menuItems.length - 1 ? 'rounded-b-xl border-t-0' : 'border-t-0'
          ]">
            <div class="flex gap-4 items-center">
              <BillIcon v-if="item.icon === 'bill'" class="w-6 h-6" />
              <CartIcon v-else-if="item.icon === 'cart'" class="w-6 h-6 text-primary" />
              <BillListIcon v-else-if="item.icon === 'bill-list'" class="w-6 h-6" />
              <InfoCircleIcon v-else-if="item.icon === 'info'" class="w-6 h-6" />
              <UserCircleIcon v-else-if="item.icon === 'user-circle'" class="w-6 h-6" />
              <LogoutIcon v-else-if="item.icon === 'logout'" class="w-6 h-6 text-primary" />
              <UniformIcon v-else-if="item.icon === 'uniform'" class="w-6 h-6" />
              <WishlistIcon v-else-if="item.icon === 'wishlist'" class="w-6 h-6 text-primary" />
              <p class="font-bold text-sm text-[#1e1e1e] capitalize">{{ item.label }}</p>
            </div>
            <div class="flex gap-6 items-center">
              <div v-if="item.badge" class="bg-[#8dc73c] rounded-full w-6 h-6 flex items-center justify-center">
                <p class="text-[13px] text-white font-semibold">{{ item.badge }}</p>
              </div>
              <ArrowRightIcon class="w-4 h-4" />
            </div>
          </router-link>
        </template>
      </div>
    </div>
  </div>
</template>
