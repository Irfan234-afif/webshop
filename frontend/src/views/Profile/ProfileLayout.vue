<template>
    <DefaultLayout>
        <div class="bg-gray-50 pt-10 pb-12 min-h-[calc(100vh-64px)]">
            <div class="container mx-auto px-4 max-w-6xl">
                <div class="flex flex-col md:flex-row gap-8">
                    <!-- Sidebar -->
                    <div class="w-full md:w-64 flex-shrink-0">
                        <div class="bg-mute border border-border-solid rounded-lg overflow-hidden">
                            <!-- <div class="p-6 border-b border-gray-100 bg-gradient-to-br from-gray-50 to-white">
                                <div class="flex items-center gap-3">
                                    <div
                                        class="w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold shadow-md" style="background: linear-gradient(to bottom right, var(--color-primary), var(--color-secondary));">
                                        {{ getInitials(user?.full_name || 'User') }}
                                    </div>
                                    <div>
                                        <h3 class="font-semibold text-gray-900 truncate max-w-[140px]">{{
                                            user?.full_name
                                            ||
                                            'User' }}</h3>
                                        <p class="text-xs text-gray-500 truncate max-w-[140px]">{{ user?.email }}</p>
                                    </div>
                                </div>
                            </div> -->

                            <nav class="">
                                <div v-for="item in menuItems" :key="item.path"
                                    class="p-2 border-b border-border-solid">
                                    <router-link :to="item.path"
                                        class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all mb-1"
                                        :class="isActive(item.path) ? '' : 'text-gray-600 hover:bg-gray-50'"
                                        :style="isActive(item.path) ? { color: 'var(--color-primary)' } : {}">
                                        <component :is="item.icon" class="w-5 h-5"
                                            :class="isActive(item.path) ? '' : 'text-gray-400'"
                                            :style="isActive(item.path) ? { color: 'var(--color-primary)' } : {}" />
                                        {{ item.label }}
                                        <svg class="ml-auto" width="6" height="10" viewBox="0 0 6 10" fill="none"
                                            xmlns="http://www.w3.org/2000/svg">
                                            <path
                                                d="M5.22343 4.41973L0.803113 0.133265C0.527293 -0.134204 3.90133e-07 0.027925 3.74735e-07 0.380202L0 8.95313C-1.53985e-08 9.30541 0.527292 9.46754 0.803113 9.20007L5.22343 4.9136C5.36997 4.77151 5.36997 4.56183 5.22343 4.41973Z"
                                                fill="#1E1E1E" />
                                        </svg>
                                    </router-link>
                                </div>
                            </nav>

                            <div class="p-2 mt-2 border-t border-gray-100">
                                <button @click="handleLogout"
                                    class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors">
                                    <LogoutIcon class="w-5 h-5" />
                                    Log Out
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Main Content -->
                    <div class="flex-1">
                        <router-view />
                    </div>
                </div>
            </div>
        </div>
    </DefaultLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import {
    UserIcon,
    MapPinIcon,
    AcademicCapIcon,
    ShieldCheckIcon,
    ArrowRightOnRectangleIcon
} from '@heroicons/vue/24/outline'
import ProfileIcon from '@/components/icons/ProfileIcon.vue'
import AddressIcon from '@/components/icons/AddressIcon.vue'
import StudentDataIcon from '@/components/icons/StudentDataIcon.vue'
import SecurityIcon from '@/components/icons/SecurityIcon.vue'
import LogoutIcon from '@/components/icons/LogoutIcon.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const user = computed(() => authStore.user)


const menuItems = [
    { label: 'Profil Saya', path: '/profile', icon: ProfileIcon },
    { label: 'Alamat Rumah', path: '/profile/address', icon: AddressIcon },
    { label: 'Data Siswa', path: '/profile/students', icon: StudentDataIcon },
    { label: 'Keamanan Akun', path: '/profile/security', icon: SecurityIcon },
]

const isActive = (path: string) => {
    if (path === '/profile' && route.path === '/profile') return true
    return route.path.startsWith(path) && path !== '/profile'
}

const handleLogout = async () => {
    await authStore.logout()
    router.push('/login')
}
</script>
