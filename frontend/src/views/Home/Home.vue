<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import HeroSection from './components/HeroSection.vue'
import ProductServicesSection from './components/ProductServicesSection.vue'
import CateringServicesSection from './components/CateringServicesSection.vue'
import { items } from '@/data/home'
import ItemGroupSection from './components/ItemGroupSection.vue'
import WebshopOffers from './components/WebshopOffers.vue'
import { transformApiProducts } from '@/utils/productTransformers'
import type { ApiProduct } from '@/types/itemGroup'

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

onMounted(async () => {
  // Only fetch banner if not already loaded
  if (!heroBannerContent.value) {
    fetchHomeHeroBanner()
  }
  // Only fetch if data hasn't been loaded yet, preventing unnecessary reloads on back/forward navigation
  if (!items.data?.items || Object.keys(items.data.items).length === 0) {
    items.fetch()
  }
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

    <template v-for="group in itemGroups" :key="group.itemGroup">
      <ItemGroupSection :title="group.itemGroup" :products="group.products" />
    </template>

    <!-- Catering & Shuttle Services Section -->
    <CateringServicesSection />

    <!-- Placeholder for additional sections -->
    <!-- You can add more sections here as per the Figma design -->
  </DefaultLayout>
</template>
