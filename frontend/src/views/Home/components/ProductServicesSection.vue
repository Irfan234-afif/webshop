<script setup lang="ts">
import ServiceCard from '@/components/common/ServiceCard.vue'
import UniformIcon from '@/components/icons/UniformIcon.vue'
import BookIcon from '@/components/icons/BookIcon.vue'
import CateringIcon from '@/components/icons/CateringIcon.vue'
import BusIcon from '@/components/icons/BusIcon.vue'

const services = [
  {
    id: 1,
    title: 'Seragam Sekolah',
    description: 'Seragam resmi sesuai standar sekolah untuk TK hingga SMA. Tersedia pembelian satuan, paket siswa baru.',
    iconComponent: UniformIcon,
    bgGradient: 'linear-gradient(141.87deg, #AC208E 0%, #C263AD 100.03%)',
    route: '/products',
    iconColor: '#AC208E'
  },
  {
    id: 2,
    title: 'Buku Pelajaran',
    description: 'Paket buku lengkap sesuai unit, kelas, dan kurikulum sekolah. Praktis, terkurasi, pada periode pengambilan tertentu',
    iconComponent: BookIcon,
    bgGradient: 'linear-gradient(141.87deg, #5F8D79 0%, #7DA393 100.03%)',
    route: '/products',
    iconColor: '#5F8D79'
  },
  {
    id: 3,
    title: 'Catering',
    description: 'Layanan makan siswa dengan menu sehat dan bergizi. Disesuaikan hari efektif sekolah dengan pembayaran bulanan.',
    iconComponent: CateringIcon,
    bgGradient: 'linear-gradient(141.87deg, #D4A574 0%, #E0B88A 100.03%)',
    route: '/products',
    iconColor: '#D4A574'
  },
  {
    id: 4,
    title: 'Antar Jemput',
    description: 'Layanan antar jemput siswa berdasarkan area tempat tinggal. Tentukan layanan antar, jemput, atau keduanya.',
    iconComponent: BusIcon,
    bgGradient: 'linear-gradient(141.87deg, #327ABA 0%, #5E9DD5 100.03%)',
    route: '/products',
    iconColor: '#327ABA'
  }
]
</script>

<template>
  <section class="bg-white w-full py-12">
    <Container>
      <!-- Section Title -->
      <h2 class="!font-bold text-xl md:text-3xl leading-snug text-text capitalize mb-16">
        Produk & Layanan Koperasi
      </h2>

      <!-- Service Cards Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <ServiceCard v-for="service in services" :key="service.id" :title="service.title"
          :description="service.description" :bg-gradient="service.bgGradient" :route="service.route">
          <template #icon>
            <component :is="service.iconComponent" :color="service.iconColor" class="w-8 h-8" />
          </template>
        </ServiceCard>
      </div>
    </Container>
  </section>
</template>
