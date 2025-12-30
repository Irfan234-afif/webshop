<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import NavbarLogo from './NavbarLogo.vue'
import MenuPopup from './MenuPopup.vue'
import CartIcon from '@/components/icons/CartIcon.vue'
import WishlistIcon from '@/components/icons/WishlistIcon.vue'
import SearchIcon from '@/components/icons/SearchIcon.vue'
import HumbergerIcon from '@/components/icons/HumbergerIcon.vue'
import Container from '@/components/layout/Container.vue'
import Popup from '@/components/common/Popup.vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import type { NavLink } from '@/types/navigation'
import { useAuthStore } from '@/stores/auth'
import { useWishlistStore } from '@/stores/wishlist'

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

const handleSearch = () => {
  emit('openSearch')
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

const handleLogout = () => {
  emit('logout')
  isMenuOpen.value = false
}

const handleLoginClick = () => {
  // Navigate to login page
  router.push('/login')
}
</script>

<template>
  <header
    :class="[
      'w-full z-50 transition-all duration-300 border-b-2',
      sticky ? 'sticky top-0' : '',
      transparent ? 'bg-transparent border-transparent' : 'bg-white border-border'
    ]"
  >
    <Container>
      <div class="flex items-center justify-between h-16 sm:h-20 lg:h-24 gap-2">
        <!-- Left: Logo + Navigation Links -->
        <div class="flex items-center gap-2 sm:gap-4 min-w-0">
          <NavbarLogo :store-name="storeName" />

          <!-- Navigation Links - Hidden on mobile and tablet -->
          <nav class="hidden lg:flex items-center gap-4 ml-2">
            <router-link to="/products" class="flex items-center h-12 px-3 text-sm font-semibold text-text uppercase hover:bg-background-soft rounded-lg transition-colors">
                Produk
            </router-link>
            <router-link to="#" class="h-12 flex items-center px-3 text-sm font-semibold text-text uppercase hover:bg-background-soft rounded-lg transition-colors">
                Kontak
            </router-link>
          </nav>
        </div>

        <!-- Right: Search + Icons + Profile -->
        <div class="flex items-center gap-2 sm:gap-6 lg:gap-8 flex-1 justify-end min-w-0">
          <!-- Search Bar - Hidden on mobile, visible from sm up -->
          <div class="hidden sm:flex bg-background-soft items-center gap-3 lg:gap-6 h-10 lg:h-12 px-3 lg:px-4 rounded-full flex-shrink min-w-0 max-w-md">
            <SearchIcon class="flex-shrink-0"/>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search Produk..."
              class="bg-transparent border-none outline-none text-xs lg:text-sm font-semibold text-text/50 placeholder:text-text/50 uppercase flex-1 min-w-0 w-full"
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- Search Icon Button - Visible on mobile only -->
          <button
            class="hidden w-7 h-7 hover:opacity-70 transition-opacity flex items-center justify-center"
            aria-label="Search"
            @click="handleSearch"
          >
            <SearchIcon />
          </button>

          <!-- Wishlist Icon - Hidden on mobile -->
          <button
            class="hidden md:block w-6 h-6 lg:w-7 lg:h-7 hover:opacity-70 transition-opacity"
            aria-label="Wishlist"
            @click="router.push('/wishlist')"
          >
            <WishlistIcon />
          </button>

          <!-- Cart Icon with Badge -->
          <button
            class="hidden sm:inline-block relative w-6 h-6 lg:w-7 lg:h-7 hover:opacity-70 transition-opacity"
            aria-label="Shopping Cart"
            @click="handleOpenCart"
          >
            <CartIcon/>
            <span
              v-if="cartItemCount > 0"
              class="absolute -top-2 -right-2 bg-secondary-alt text-white text-xs font-bold rounded-full w-5 h-5 lg:w-6 lg:h-6 flex items-center justify-center"
            >
              {{ cartItemCount }}
            </span>
          </button>

          <!-- User Profile Button - Full on desktop, compact on mobile/tablet -->
          <div class="relative" v-if="!isGuest">
            <button
              ref="menuButtonRef"
              class="bg-primary text-white font-bold text-xs sm:text-sm uppercase px-3 sm:px-4 lg:px-6 py-2 sm:py-2.5 lg:py-3 rounded-xl flex items-center gap-2 sm:gap-4 lg:gap-6 hover:opacity-90 transition-opacity"
              @click.stop="handleToggleMenu"
            >
              <span class="truncate max-w-[100px] lg:max-w-none">
                {{
                  cartStore.activeStudent
                }}
              </span>
              <HumbergerIcon />
            </button>

            <!-- Menu Popup -->
            <Popup
              :is-open="isMenuOpen"
              position="top-right"
              width="min(468px, 94vw)"
              max-height="90vh"
              @close="handleCloseMenu"
            >
              <MenuPopup
                @select-student="handleSelectStudent"
                @logout="handleLogout"
              />
            </Popup>
          </div>
          <button
            v-else
            class="h-12 bg-primary text-white font-bold text-xs sm:text-sm uppercase px-3 sm:px-4 lg:px-12 py-2 sm:py-2.5 lg:py-3 rounded-xl flex items-center gap-2 sm:gap-4 lg:gap-6 hover:opacity-90 transition-opacity"
            @click="handleLoginClick"
          >
            <span class="">Login</span>
          </button>

        </div>
      </div>
    </Container>
  </header>
</template>
