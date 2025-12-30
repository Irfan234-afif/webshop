<script setup lang="ts">
import ItemGroupSection from './ItemGroupSection.vue'
import type { Product, PromotionalCard } from '@/types/itemGroup'

const products: Product[] = [
  {
    id: 1,
    image: 'https://www.figma.com/api/mcp/asset/a8f0835e-1e0e-4d03-bd8e-fff2f4b22918',
    category: 'Alat Tulis',
    rating: 4.8,
    title: 'Paket Alat Tulis Lengkap',
    description: 'Paket lengkap alat tulis untuk siswa baru dengan harga terjangkau.',
    price: 250000,
    originalPriceRange: 'Rp 300.000 - Rp 350.000',
    discount: 17,
    hasDiscount: true
  },
  {
    id: 2,
    image: 'https://www.figma.com/api/mcp/asset/1be0fa68-0289-4b4d-8ba5-17984209e906',
    category: 'Alat Tulis',
    rating: 4.9,
    title: 'Set Pensil & Penghapus',
    description: 'Set pensil 2B, penghapus, dan rautan berkualitas tinggi.',
    price: 45000,
    originalPriceRange: 'Rp 55.000 – Rp 60.000',
    discount: 18,
    hasDiscount: true
  },
  {
    id: 3,
    image: 'https://www.figma.com/api/mcp/asset/0f5f7bd1-33bf-4c47-aa6d-c1528e01ffb4',
    category: 'Alat Tulis',
    rating: 4.7,
    title: 'Buku Tulis Sinar Dunia',
    description: 'Buku tulis 38 lembar dengan kertas berkualitas.',
    price: 12000,
    hasDiscount: false
  },
  {
    id: 4,
    image: 'https://www.figma.com/api/mcp/asset/6c22c40a-92da-4a1c-aacd-41a5ba034e8b',
    category: 'Alat Tulis',
    rating: 4.9,
    title: 'Spidol Warna Set 12',
    description: 'Set spidol warna 12 pcs untuk menggambar dan mewarnai.',
    price: 85000,
    originalPriceRange: 'Rp 100.000 – Rp 110.000',
    discount: 15,
    hasDiscount: true
  },
  {
    id: 5,
    image: 'https://www.figma.com/api/mcp/asset/1be0fa68-0289-4b4d-8ba5-17984209e906',
    category: 'Alat Tulis',
    rating: 4.8,
    title: 'Penggaris Set Matematika',
    description: 'Set penggaris lengkap untuk matematika (penggaris, busur, segitiga).',
    price: 35000,
    hasDiscount: false
  },
  {
    id: 6,
    image: 'https://www.figma.com/api/mcp/asset/0f5f7bd1-33bf-4c47-aa6d-c1528e01ffb4',
    category: 'Alat Tulis',
    rating: 4.9,
    title: 'Tas Sekolah Ransel',
    description: 'Tas ransel sekolah dengan banyak kantong dan tahan lama.',
    price: 175000,
    originalPriceRange: 'Rp 200.000 – Rp 225.000',
    discount: 12,
    hasDiscount: true
  },
  {
    id: 7,
    image: 'https://www.figma.com/api/mcp/asset/6c22c40a-92da-4a1c-aacd-41a5ba034e8b',
    category: 'Alat Tulis',
    rating: 4.7,
    title: 'Kotak Pensil Premium',
    description: 'Kotak pensil dengan banyak ruang dan desain menarik.',
    price: 65000,
    hasDiscount: false
  }
]

const promotionalCard: PromotionalCard = {
  icon: `<svg class="w-8 h-8" viewBox="0 0 32 32" fill="none">
    <path
      d="M4 8h24M4 16h24M4 24h16"
      stroke="#2E7D32"
      stroke-width="2"
      stroke-linecap="round"
    />
  </svg>`,
  gradientFrom: '#2E7D32',
  gradientTo: '#66BB6A',
  title: 'ALAT TULIS',
  description: 'Perlengkapan alat tulis lengkap untuk semua tingkat pendidikan. Tersedia paket hemat dan satuan.',
  ctaText: 'Lihat semua alat tulis'
}
</script>

<template>
  <ItemGroupSection
    title="Alat Tulis & Perlengkapan"
    :products="products"
    :promotional-card="promotionalCard"
  />
</template>
