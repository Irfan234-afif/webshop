import type { ProductOrService } from '@/types/product'
import { calculatePriceRange, formatServicePrice } from '@/utils/formatters'

export const productsMockData: ProductOrService[] = [
  // Services
  {
    id: 'serv-1',
    type: 'service',
    icon: 'CateringIcon',
    iconColor: '#FBB554',
    bgGradient: 'linear-gradient(154.91deg, #FBB554 0%, #FFCB82 100.03%)',
    category: 'Layanan',
    rating: 4.9,
    title: 'Catering',
    description:
      'kebutuhan konsumsi harian siswa dengan menu yang sehat, bergizi, dan variatif.',
    pricePerMonth: 350000,
    priceLabel: formatServicePrice(350000),
    infoNotes: [
      'harga diatas bukan harga tetap',
      'Tagihan bergantung pada jumlah hari efektif siswa'
    ],
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(350000)
  },
  {
    id: 'serv-2',
    type: 'service',
    icon: 'BusIcon',
    iconColor: '#4A90E2',
    bgGradient: 'linear-gradient(154.91deg, #4A90E2 0%, #7AB8F5 100.03%)',
    category: 'Layanan',
    rating: 4.9,
    title: 'Antar Jemput',
    description:
      'memastikan perjalanan anak ke dan dari sekolah berlangsung dengan aman dan terjadwal.',
    pricePerMonth: 250000,
    priceLabel: formatServicePrice(250000),
    infoNotes: [
      'harga diatas bukan harga tetap',
      'harga bervariasi tergantung dengan wilayah'
    ],
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(250000)
  },

  // Products - Seragam Sekolah
  {
    id: 'prod-1',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400',
    category: 'Seragam Sekolah',
    rating: 4.8,
    title: 'Seragam Batik SMA',
    description: 'Seragam batik lengkap untuk siswa SMA dengan kualitas premium',
    price: 125000,
    originalPriceRange: 'Rp 150.000',
    discount: 17,
    hasDiscount: true,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(125000)
  },
  {
    id: 'prod-2',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400',
    category: 'Seragam Sekolah',
    rating: 4.7,
    title: 'Seragam Olahraga SMA',
    description: 'Seragam olahraga berkualitas dengan bahan yang nyaman dan menyerap keringat',
    price: 95000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(95000)
  },
  {
    id: 'prod-3',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400',
    category: 'Seragam Sekolah',
    rating: 4.9,
    title: 'Seragam Harian SMA Putih Abu',
    description: 'Seragam harian lengkap dengan bahan katun yang nyaman untuk kegiatan belajar',
    price: 110000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(110000)
  },

  // Products - Buku Pelajaran
  {
    id: 'prod-4',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400',
    category: 'Buku Pelajaran',
    rating: 4.9,
    title: 'Paket Buku Kelas 10',
    description: 'Paket lengkap buku pelajaran untuk kelas 10 semua mata pelajaran',
    price: 450000,
    originalPriceRange: 'Rp 500.000',
    discount: 10,
    hasDiscount: true,
    classGrade: [10],
    priceRange: calculatePriceRange(450000)
  },
  {
    id: 'prod-5',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400',
    category: 'Buku Pelajaran',
    rating: 4.8,
    title: 'Paket Buku Kelas 11',
    description: 'Paket lengkap buku pelajaran untuk kelas 11 semua mata pelajaran',
    price: 475000,
    originalPriceRange: 'Rp 530.000',
    discount: 10,
    hasDiscount: true,
    classGrade: [11],
    priceRange: calculatePriceRange(475000)
  },
  {
    id: 'prod-6',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400',
    category: 'Buku Pelajaran',
    rating: 4.9,
    title: 'Paket Buku Kelas 12',
    description: 'Paket lengkap buku pelajaran untuk kelas 12 semua mata pelajaran + buku UTBK',
    price: 520000,
    originalPriceRange: 'Rp 600.000',
    discount: 13,
    hasDiscount: true,
    classGrade: [12],
    priceRange: calculatePriceRange(520000)
  },
  {
    id: 'prod-7',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400',
    category: 'Buku Pelajaran',
    rating: 4.7,
    title: 'Buku Latihan Soal UTBK',
    description: 'Kumpulan soal latihan UTBK terlengkap dengan pembahasan detail',
    price: 85000,
    hasDiscount: false,
    classGrade: [12],
    priceRange: calculatePriceRange(85000)
  },
  {
    id: 'prod-8',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=400',
    category: 'Buku Pelajaran',
    rating: 4.6,
    title: 'Kamus Bahasa Inggris Indonesia',
    description: 'Kamus lengkap untuk membantu siswa dalam belajar Bahasa Inggris',
    price: 65000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(65000)
  },
  {
    id: 'prod-9',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400',
    category: 'Buku Pelajaran',
    rating: 4.8,
    title: 'Buku LKS Matematika',
    description: 'Lembar Kerja Siswa Matematika dengan soal-soal latihan berkualitas',
    price: 45000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(45000)
  },

  // Additional products with various categories and price ranges
  {
    id: 'prod-10',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1606326608606-aa0b62935f2b?w=400',
    category: 'Buku Pelajaran',
    rating: 4.7,
    title: 'Atlas Dunia',
    description: 'Atlas dunia lengkap dengan peta-peta terkini untuk pelajaran Geografi',
    price: 120000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(120000)
  },
  {
    id: 'prod-11',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=400',
    category: 'Seragam Sekolah',
    rating: 4.6,
    title: 'Dasi dan Topi SMA',
    description: 'Dasi dan topi sekolah resmi dengan logo sekolah',
    price: 35000,
    hasDiscount: false,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(35000)
  },
  {
    id: 'prod-12',
    type: 'product',
    image: 'https://images.unsplash.com/photo-1560343090-f0409e92791a?w=400',
    category: 'Seragam Sekolah',
    rating: 4.8,
    title: 'Sepatu Sekolah Hitam',
    description: 'Sepatu sekolah hitam formal berkualitas dengan sol anti slip',
    price: 175000,
    originalPriceRange: 'Rp 200.000',
    discount: 13,
    hasDiscount: true,
    classGrade: [10, 11, 12],
    priceRange: calculatePriceRange(175000)
  }
]
