<script setup lang="ts">
import { computed } from 'vue'
import type { ProductDetail } from '@/types/productDetail'
import TabNavigation, { type Tab } from '@/components/common/TabNavigation.vue'
import ProductDetailsTab from './ProductDetailsTab.vue'
import SizeChartTab from './SizeChartTab.vue'
import ReviewsTab from './ReviewsTab.vue'

interface Props {
  product: ProductDetail
  activeTab: 'details' | 'size-chart' | 'reviews'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:activeTab': [tab: 'details' | 'size-chart' | 'reviews']
}>()

// Tab configuration
const tabs = computed<Tab[]>(() => {
  const tabList: Tab[] = [
    {
      key: 'details',
      label: 'Detail Produk'
    }
  ]

  // Only show size chart tab for products with size chart
  if (props.product.type === 'product' && props.product.sizeChart) {
    tabList.push({
      key: 'size-chart',
      label: 'Ukuran (Size Chart)'
    })
  }

  // Always show reviews tab
  tabList.push({
    key: 'reviews',
    label: 'Reviews'
  })

  return tabList
})

const handleTabChange = (key: string) => {
  emit('update:activeTab', key as 'details' | 'size-chart' | 'reviews')
}

// Extended description for detail tab (from design)
const extendedDescription = computed(() => {
  return `Baju Batik Resmi SMA ini dirancang khusus sebagai seragam identitas sekolah dengan kualitas premium yang nyaman digunakan sepanjang hari. Terbuat dari bahan katun halus berkualitas tinggi, seragam batik ini memastikan siswa tetap sejuk dan tidak mudah gerah ketika beraktivitas di dalam maupun luar kelas. Tekstur kain yang lembut tidak menimbulkan iritasi, menjadikannya pilihan ideal untuk penggunaan jangka panjang. Motif batik dirancang mengikuti standar sekolah dengan perpaduan warna yang elegan, tegas, dan tetap mencerminkan karakter formal seorang pelajar SMA. Setiap potongan kain dicetak dengan teknologi high-quality dye yang membuat warna lebih tahan lama, tidak cepat pudar meski sering dicuci. Jahitan dibuat rapi dan kuat, dengan standar pabrik yang memastikan ketahanan tinggi untuk pemakaian harian. Cocok digunakan untuk kegiatan sekolah reguler, upacara, pertemuan resmi, ataupun kegiatan representatif lainnya. Seragam batik ini juga memiliki potongan ergonomis, memudahkan siswa bergerak aktif tanpa merasa sempit atau tidak nyaman. Dengan kualitas terbaik dan desain yang sesuai standar sekolah, produk ini menjadi pilihan tepat bagi siswa dan wali murid yang menginginkan seragam tahan lama, nyaman, dan resmi.`
})
</script>

<template>
  <div class="w-full">
    <!-- Tab Navigation -->
    <TabNavigation
      :tabs="tabs"
      :active-tab="activeTab"
      @change="handleTabChange"
    />

    <!-- Tab Content -->
    <div class="w-full">
      <!-- Details Tab -->
      <ProductDetailsTab
        v-if="activeTab === 'details'"
        :description="product.description"
        :specifications="product.specifications"
      />

      <!-- Size Chart Tab -->
      <SizeChartTab
        v-else-if="activeTab === 'size-chart' && product.sizeChart"
        :size-chart="product.sizeChart"
      />

      <!-- Reviews Tab -->
      <ReviewsTab
        v-else-if="activeTab === 'reviews'"
        :reviews="product.reviews || []"
      />
    </div>
  </div>
</template>
