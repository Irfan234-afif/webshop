<script setup lang="ts">
import ItemGroupSection from './ItemGroupSection.vue'
import type { Product, PromotionalCard } from '@/types/itemGroup'

const products: Product[] = [
  {
    id: 1,
    image: 'https://www.figma.com/api/mcp/asset/a8f0835e-1e0e-4d03-bd8e-fff2f4b22918',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Paket Seragam Siswa Baru (Hemat)',
    description: 'Paket lengkap seragam awal tahun ajaran dengan harga spesial.',
    price: 820000,
    originalPriceRange: 'Rp 900.000 - Rp 999.000',
    discount: 20,
    hasDiscount: true
  },
  {
    id: 2,
    image: 'https://www.figma.com/api/mcp/asset/1be0fa68-0289-4b4d-8ba5-17984209e906',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Paket Seragam Putih Abu-Abu',
    description: 'Paket seragam lengkap siswa baru (atasan, bawahan, dasi & atribut).',
    price: 336000,
    originalPriceRange: 'Rp 400.000 – Rp 420.000',
    discount: 20,
    hasDiscount: true
  },
  {
    id: 3,
    image: 'https://www.figma.com/api/mcp/asset/0f5f7bd1-33bf-4c47-aa6d-c1528e01ffb4',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Seragam Batik Sekolah',
    description: 'Seragam batik resmi sekolah auliya untuk hari tertentu.',
    price: 136000,
    originalPriceRange: 'Rp 160.000 – Rp 185.000',
    discount: 15,
    hasDiscount: true
  },
  {
    id: 4,
    image: 'https://www.figma.com/api/mcp/asset/6c22c40a-92da-4a1c-aacd-41a5ba034e8b',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Seragam Olahraga',
    description: 'Kaos dan celana olahraga berbahan ringan dan menyerap keringat.',
    price: 153000,
    hasDiscount: false
  },
  {
    id: 5,
    image: 'https://www.figma.com/api/mcp/asset/1be0fa68-0289-4b4d-8ba5-17984209e906',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Paket Seragam Putih Abu-Abu',
    description: 'Paket seragam lengkap siswa baru (atasan, bawahan, dasi & atribut).',
    price: 336000,
    originalPriceRange: 'Rp 400.000 – Rp 420.000',
    discount: 20,
    hasDiscount: true
  },
  {
    id: 6,
    image: 'https://www.figma.com/api/mcp/asset/0f5f7bd1-33bf-4c47-aa6d-c1528e01ffb4',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Seragam Batik Sekolah',
    description: 'Seragam batik resmi sekolah auliya untuk hari tertentu.',
    price: 136000,
    originalPriceRange: 'Rp 160.000 – Rp 185.000',
    discount: 15,
    hasDiscount: true
  },
  {
    id: 7,
    image: 'https://www.figma.com/api/mcp/asset/6c22c40a-92da-4a1c-aacd-41a5ba034e8b',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Seragam Olahraga',
    description: 'Kaos dan celana olahraga berbahan ringan dan menyerap keringat.',
    price: 153000,
    hasDiscount: false
  }
]

const promotionalCard: PromotionalCard = {
  icon: `<svg class="w-8 h-8" viewBox="0 0 32 32" fill="none">
    <path
      d="M8 12h16M8 16h16M8 20h8"
      stroke="#AC208E"
      stroke-width="2"
      stroke-linecap="round"
    />
  </svg>`,
  gradientFrom: '#AC208E',
  gradientTo: '#C263AD',
  title: 'SERAGAM',
  description: 'Seragam resmi sesuai standar sekolah untuk TK hingga SMA. Tersedia pembelian satuan, paket siswa baru.',
  ctaText: 'Lihat semua seragam sekolah'
}
</script>

<template>
  <ItemGroupSection
    title="Seragam Sekolah"
    :products="products"
    :promotional-card="promotionalCard"
  />
</template>
