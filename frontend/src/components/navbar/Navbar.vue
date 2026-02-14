<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import NavbarLogo from './NavbarLogo.vue'
import MenuPopup from './MenuPopup.vue'
import CartIcon from '@/components/icons/CartIcon.vue'
import WishlistIcon from '@/components/icons/WishlistIcon.vue'
import SearchIcon from '@/components/icons/SearchIcon.vue'
import HumbergerIcon from '@/components/icons/HumbergerIcon.vue'
import Container from '@/components/layout/Container.vue'
import Popup from '@/components/common/Popup.vue'
import { useRouter, useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import type { NavLink } from '@/types/navigation'
import { useAuthStore } from '@/stores/auth'
import { useWishlistStore } from '@/stores/wishlist'
import PrimaryButton from '../common/PrimaryButton.vue'

withDefaults(
  defineProps<{
    storeName?: string
    links?: NavLink[]
    transparent?: boolean
    sticky?: boolean
  }>(),
  {
    storeName: 'Webshop',
    transparent: false,
    sticky: true
  }
)

const router = useRouter()
const route = useRoute()
const cartStore = useCartStore()
const authStore = useAuthStore()
const wishlistStore = useWishlistStore()

const emit = defineEmits<{
  openSearch: []
  openCart: []
  selectStudent: [studentId: string]
  logout: []
}>()

const searchQuery = ref('')
const cartItemCount = computed(() => cartStore.itemCount)
const isMenuOpen = ref(false)
const menuButtonRef = ref<HTMLElement | null>(null)
const isGuest = computed(() => authStore.isGuest)

// Initialize cart data on component mount
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await cartStore.initialize()
    await wishlistStore.fetchWishlist()
  }
})



// Sync search query from URL
watch(
  () => route.query.search,
  (newSearch) => {
    if (typeof newSearch === 'string') {
      searchQuery.value = newSearch
    } else {
      searchQuery.value = ''
    }
  },
  { immediate: true }
)

// Debounce utility
const debounce = (fn: Function, delay: number) => {
  let timeoutId: ReturnType<typeof setTimeout>
  return (...args: any[]) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const executeSearch = () => {
  if (searchQuery.value) {
    // If not on products page, always push
    // If on products page, only push if changed (though router handles this usually)
    router.push({
      path: '/products',
      query: { ...route.query, search: searchQuery.value }
    })
  } else {
    // If empty and on products page with search param, remove it
    if (route.path === '/products' && route.query.search) {
      const newQuery = { ...route.query }
      delete newQuery.search
      router.push({ path: '/products', query: newQuery })
    } else if (!route.path.includes('/products')) {
      // If not on products page and empty, do nothing/emit default
      emit('openSearch')
    }
  }
}

const debouncedSearch = debounce(executeSearch, 500)

// Watch input for auto-search
watch(searchQuery, (newValue) => {
  // Prevent loop if value matches URL already (synced from URL)
  if (newValue === route.query.search) return

  // If we are clearing (newValue is empty) and we have a search param, trigger
  if (!newValue && route.query.search) {
    debouncedSearch()
    return
  }

  if (newValue) {
    debouncedSearch()
  }
})

const handleSearch = () => {
  executeSearch()
}

const handleOpenCart = () => {
  router.push('/cart');
}

const handleToggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleCloseMenu = () => {
  isMenuOpen.value = false
}

const handleSelectStudent = (studentId: string) => {
  cartStore.setActiveStudent(studentId)
  emit('selectStudent', studentId)
}

const handleLogout = async () => {
  await authStore.handleLogout()
  isMenuOpen.value = false
  router.push('/')
}

const handleLoginClick = () => {
  // Navigate to login page
  router.push('/login')
}
</script>

<template>
  <header :class="[
    'w-full z-50 transition-all duration-300 border-b-2',
    sticky ? 'sticky top-0' : '',
    transparent ? 'bg-transparent border-transparent' : 'bg-white border-border'
  ]">
    <Container>
      <div class="flex items-center justify-between h-16 sm:h-20 lg:h-24 gap-2">
        <!-- Left: Logo + Navigation Links -->
        <div class="flex items-center gap-2 sm:gap-4 min-w-0">
          <NavbarLogo :store-name="storeName" />

          <!-- Navigation Links - Hidden on mobile and tablet -->
          <nav class="hidden lg:flex items-center gap-4 ml-2">
            <router-link to="/products"
              class="flex items-center h-12 px-3 text-sm font-semibold text-text hover:bg-background-soft rounded-lg transition-colors">
              Produk
            </router-link>
            <router-link to="#"
              class="h-12 flex items-center px-3 text-sm font-semibold text-text hover:bg-background-soft rounded-lg transition-colors">
              Kontak
            </router-link>
          </nav>
        </div>

        <!-- Right: Search + Icons + Profile -->
        <div class="flex items-center gap-2 sm:gap-6 lg:gap-8 flex-1 justify-end min-w-0">
          <!-- Search Bar - Hidden on mobile, visible from sm up -->
          <div
            class="flex bg-background-soft items-center gap-3 lg:gap-6 h-10 lg:h-12 px-3 lg:px-4 rounded-full flex-shrink min-w-0 max-w-md">
            <SearchIcon class="flex-shrink-0" />
            <input v-model="searchQuery" type="text" placeholder="Search Produk..."
              class="bg-transparent border-none outline-none focus:ring-0 focus:outline-none text-xs lg:text-sm !font-semibold text-text-secondary placeholder:text-text-secondary placeholder:font-semibold flex-1 min-w-0 w-full"
              @keyup.enter="handleSearch" />
          </div>

          <!-- Search Icon Button - Visible on mobile only -->
          <button class="hidden w-7 h-7 hover:opacity-70 transition-opacity flex items-center justify-center"
            aria-label="Search" @click="handleSearch">
            <SearchIcon />
          </button>

          <!-- Wishlist Icon - Hidden on mobile -->
          <button class="hidden md:block w-6 h-6 lg:w-7 lg:h-7 hover:opacity-70 transition-opacity"
            aria-label="Wishlist" @click="router.push('/wishlist')">
            <WishlistIcon class="text-primary" />
          </button>

          <!-- Cart Icon with Badge -->
          <button class="hidden sm:inline-block relative w-6 h-6 lg:w-7 lg:h-7 hover:opacity-70 transition-opacity"
            aria-label="Shopping Cart" @click="handleOpenCart">
            <CartIcon class="text-primary" />
            <span v-if="cartItemCount > 0"
              class="absolute -top-3 -right-3 bg-success text-white text-xs font-bold rounded-full w-5 h-5 lg:w-6 lg:h-6 flex items-center justify-center">
              {{ cartItemCount }}
            </span>
          </button>

          <!-- User Profile Button - Full on desktop, compact on mobile/tablet -->
          <div class="relative" v-if="!isGuest">
            <PrimaryButton ref="menuButtonRef"
              class="bg-primary text-white font-bold text-xs sm:text-sm uppercase !px-6 !py-2.5 sm:py-3 rounded-xl flex items-center gap-2 sm:gap-4 lg:gap-6 hover:opacity-90 transition-opacity"
              @click.stop="handleToggleMenu">
              <span class="truncate max-w-[100px] lg:max-w-none font-semibold">
                {{
                  cartStore.activeStudentName
                }}
              </span>
              <HumbergerIcon />
            </PrimaryButton>

            <!-- Menu Popup -->
            <Popup :is-open="isMenuOpen" position="top-right" width="min(468px, 94vw)" max-height="90vh"
              @close="handleCloseMenu">
              <MenuPopup @select-student="handleSelectStudent" @logout="handleLogout" @close="handleCloseMenu" />
            </Popup>
          </div>
          <PrimaryButton v-else
            class=""
            @click="handleLoginClick">
            <span class="">Login</span>
          </PrimaryButton>

        </div>
      </div>
    </Container>
  </header>
</template>
