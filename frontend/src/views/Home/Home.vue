<script setup lang="ts">
import { onMounted, computed, ref, watch } from 'vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import HeroSection from './components/HeroSection.vue'
import ProductServicesSection from './components/ProductServicesSection.vue'
import CateringServicesSection from './components/CateringServicesSection.vue'
import { items, fetchForStudent } from '@/data/home'
import ItemGroupSection from './components/ItemGroupSection.vue'
import WebshopOffers from './components/WebshopOffers.vue'
import { transformApiProducts } from '@/utils/productTransformers'
import type { ApiProduct } from '@/types/itemGroup'
import { useCartStore } from '@/stores/cart'

// Set component name for KeepAlive caching
defineOptions({
  name: 'HomePage'
})

interface BannerContent {
  type?: string
  image?: string
  title?: string
  subtitle?: string
  cta_text?: string
  cta_url?: string
  secondary_cta_text?: string
  secondary_cta_url?: string
  right_image?: string
}

const heroBannerContent = ref<BannerContent | undefined>(undefined)

const fetchHomeHeroBanner = async () => {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.website.get_banner_content?banner_key=Home Hero')
    const data = await response.json()
    if (data.message) {
      heroBannerContent.value = data.message
    }
  } catch (error) {
    console.error('Failed to fetch Home Hero banner:', error)
  }
}

// Get cart store for active student
const cartStore = useCartStore()

// Computed property to get active student info
const activeStudentName = computed(() => {
  if (!cartStore.activeStudent) return null
  const student = cartStore.students.find(s => s.name === cartStore.activeStudent)
  return student?.student_name || null
})

onMounted(async () => {
  // Only fetch banner if not already loaded
  if (!heroBannerContent.value) {
    fetchHomeHeroBanner()
  }
  // Always fetch items on mount with current active student
  fetchForStudent(cartStore.activeStudent)
})

// Watch for active student changes and reload recommendations
watch(() => cartStore.activeStudent, (newStudent) => {
  // Reload items when active student changes
  fetchForStudent(newStudent)
})

// Transform items data for display
const itemGroups = computed(() => {
  if (!items.data?.items) return []

  return Object.entries(items.data.items).map(([itemGroup, products]) => ({
    itemGroup,
    products: transformApiProducts(products as ApiProduct[])
  }))
})

</script>

<template>
  <DefaultLayout store-name="KoperasiAuliya">
    <!-- Hero Section -->
    <HeroSection :content="heroBannerContent" />

    <!-- Webshop Offers -->
    <WebshopOffers />

    <!-- School Year Preparation Section -->
    <!-- <SchoolYearPreparationSection /> -->

    <!-- Product & Services Section -->
    <ProductServicesSection />

    <!-- Loading shimmer effect -->
    <template v-if="items.loading">
      <div v-for="i in 3" :key="`shimmer-${i}`" class="shimmer-container">
        <div class="shimmer-title"></div>
        <div class="shimmer-products">
          <div v-for="j in 4" :key="`shimmer-product-${j}`" class="shimmer-card"></div>
        </div>
      </div>
    </template>

    <!-- Actual content -->
    <template v-else>
      <template v-for="group in itemGroups" :key="group.itemGroup">
        <ItemGroupSection :title="group.itemGroup" :products="group.products" />
      </template>
    </template>

    <!-- Catering & Shuttle Services Section -->
    <CateringServicesSection />

    <!-- Placeholder for additional sections -->
    <!-- You can add more sections here as per the Figma design -->
  </DefaultLayout>
</template>

<style scoped>
/* Shimmer loading effect */
.shimmer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 1.5rem;
}

.shimmer-title {
  height: 32px;
  width: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.shimmer-products {
  display: flex;
  gap: 1.5rem;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 1rem;
  scrollbar-width: thin;
  scrollbar-color: #e0e0e0 transparent;
}

.shimmer-products::-webkit-scrollbar {
  height: 8px;
}

.shimmer-products::-webkit-scrollbar-track {
  background: transparent;
}

.shimmer-products::-webkit-scrollbar-thumb {
  background-color: #e0e0e0;
  border-radius: 4px;
}

.shimmer-card {
  min-width: 250px;
  height: 320px;
  flex-shrink: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 12px;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }

  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 768px) {
  .shimmer-card {
    min-width: 180px;
    height: 240px;
  }
}

/* Personalization Banner Styles */
.personalization-banner {
  max-width: 1200px;
  margin: 2rem auto 1rem;
  padding: 0 1.5rem;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  font-size: 0.95rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);
}

.banner-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.banner-content strong {
  font-weight: 600;
}

@media (max-width: 768px) {
  .banner-content {
    font-size: 0.875rem;
    padding: 0.875rem 1rem;
  }

  .banner-icon {
    width: 18px;
    height: 18px;
  }
}
</style>
