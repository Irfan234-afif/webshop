<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '@/components/navbar/Navbar.vue'
import Footer from '@/components/footer/Footer.vue'
import type { NavLink } from '@/types/navigation'
import { useAuthStore } from '@/stores/auth'
import SplashScreen from '@/components/common/SplashScreen.vue'

const props = withDefaults(
  defineProps<{
    storeName?: string
    navLinks?: NavLink[]
  }>(),
  {
    storeName: 'Webshop'
  }
)

const authStore = useAuthStore()

const defaultNavLinks: NavLink[] = [
  { label: 'Home', to: '/', exact: true },
  { label: 'Shop', to: '/shop' },
  { label: 'Categories', to: '/categories' },
  { label: 'About', to: '/about' }
]

const navLinks = computed(() => props.navLinks || defaultNavLinks)

const handleOpenSearch = () => {
  console.log('Open search')
  // TODO: Implement search modal
}

</script>

<template>
  <div class="min-h-screen flex flex-col bg-white dark:bg-gray-900">
    <!-- Navbar -->
    <Navbar
      :store-name="storeName"
      :links="navLinks"
      :sticky="true"
      @open-search="handleOpenSearch"
    />

    <!-- Main Content -->
    <SplashScreen v-if="authStore.isLoading" />
    <main v-else class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <Footer />
  </div>
</template>
