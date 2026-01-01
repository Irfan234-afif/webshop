<script setup lang="ts">
import Container from '@/components/layout/Container.vue'

interface ServiceFeature {
  text: string
}

interface ServiceCard {
  title: string
  description: string
  features: ServiceFeature[]
  ctaText: string
  ctaLink: string
  iconType: 'catering' | 'shuttle'
  backgroundGradient: string
  imageUrl: string
}

const services: ServiceCard[] = [
  {
    title: 'CATERING',
    description: 'Layanan Catering Sekolah Auliya hadir untuk membantu memenuhi kebutuhan konsumsi harian siswa dengan menu yang sehat, bergizi, dan variatif. Layanan ini dirancang khusus mengikuti hari efektif sekolah yang ditentukan setiap bulannya.',
    features: [
      { text: 'Menu disesuaikan dengan hari efektif sekolah' },
      { text: 'Input alergi makanan untuk keamanan siswa' },
      { text: 'Sistem absensi fleksibel (izin via website / WA)' },
      { text: 'Pembayaran transparan di akhir bulan' }
    ],
    ctaText: 'Berlangganan',
    ctaLink: '#',
    iconType: 'catering',
    backgroundGradient: 'linear-gradient(158.23deg, #FBB554 0%, #FFCB82 100.03%)',
    imageUrl: 'catering.png'
  },
  {
    title: 'CATERING',
    description: 'Layanan Antar Jemput Sekolah Auliya disediakan untuk membantu wali murid memastikan perjalanan anak ke dan dari sekolah berlangsung dengan aman dan terjadwal. Layanan ini dibagi berdasarkan wilayah area dengan harga yang telah ditentukan untuk setiap area.',
    features: [
      { text: 'Harga transparan berdasarkan area' },
      { text: 'Informasi driver lengkap & jelas' },
      { text: 'Sistem kuota untuk menjaga kenyamanan & keamanan' },
      { text: 'Pilihan layanan fleksibel' }
    ],
    ctaText: 'Lihat Cakupan Area',
    ctaLink: '#',
    iconType: 'shuttle',
    backgroundGradient: 'linear-gradient(158.23deg, #327ABA 0%, #5E9DD5 100.03%)',
    imageUrl: 'antar-jemput.png'
  }
]
</script>

<template>
  <section class="bg-white w-full py-12 sm:py-16">
    <Container>
      <!-- Section Title -->
      <h2 class="text-text text-2xl sm:text-3xl !font-bold capitalize mb-12 sm:mb-16">
        Layanan Catering & Antar Jemput
      </h2>

      <!-- Services Cards Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Service Card -->
        <div v-for="(service, index) in services" :key="index"
          class="relative flex flex-col justify-between rounded-xl overflow-hidden p-8 sm:p-12 min-h-[512px]"
          :style="{ background: service.backgroundGradient }">
          <!-- Background Image -->
          <div class="absolute bottom-0 right-0 pointer-events-none opacity-90">
            <img :src="service.imageUrl" :alt="service.title" class="w-[280px] sm:w-[400px] h-auto object-contain" />
          </div>

          <!-- Content -->
          <div class="relative z-10 flex flex-col gap-8 sm:gap-11">
            <!-- Icon & Title -->
            <div class="flex gap-6 sm:gap-8 items-center">
              <!-- Icon Circle -->
              <div
                class="bg-white rounded-full w-14 h-14 sm:w-[58px] sm:h-[58px] flex items-center justify-center flex-shrink-0">
                <!-- Catering Icon -->
                <svg v-if="service.iconType === 'catering'" width="32" height="32" viewBox="0 0 32 32" fill="none"
                  xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M28 9.33301H4C2.89543 9.33301 2 10.2284 2 11.333V25.333C2 26.4376 2.89543 27.333 4 27.333H28C29.1046 27.333 30 26.4376 30 25.333V11.333C30 10.2284 29.1046 9.33301 28 9.33301Z"
                    fill="#FBB554" />
                  <path
                    d="M6 9.33301V6.66634C6 5.56177 6.89543 4.66634 8 4.66634H24C25.1046 4.66634 26 5.56177 26 6.66634V9.33301"
                    stroke="#FBB554" stroke-width="2" stroke-linecap="round" />
                </svg>

                <!-- Shuttle/Bus Icon -->
                <svg v-else width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M26.6667 21.333H24V10.6663C24 9.55977 23.1046 8.66634 22 8.66634H10C8.89543 8.66634 8 9.55977 8 10.6663V21.333H5.33333C4.59695 21.333 4 21.9299 4 22.6663V24.6663C4 25.4027 4.59695 25.9997 5.33333 25.9997H26.6667C27.403 25.9997 28 25.4027 28 24.6663V22.6663C28 21.9299 27.403 21.333 26.6667 21.333Z"
                    fill="#327ABA" />
                  <circle cx="11" cy="21.333" r="1.5" fill="white" />
                  <circle cx="21" cy="21.333" r="1.5" fill="white" />
                </svg>
              </div>

              <!-- Title -->
              <h3 class="text-white text-xl sm:text-2xl !font-bold capitalize">
                {{ service.title }}
              </h3>
            </div>

            <!-- Description -->
            <p class="text-white text-sm font-medium leading-relaxed capitalize max-w-full">
              {{ service.description }}
            </p>

            <!-- Features List -->
            <div class="flex flex-col gap-3">
              <div v-for="(feature, featureIndex) in service.features" :key="featureIndex"
                class="flex gap-4 items-center">
                <!-- Check Icon -->
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"
                  class="flex-shrink-0">
                  <path
                    d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z"
                    fill="white" />
                </svg>

                <!-- Feature Text -->
                <p class="text-white text-sm font-semibold capitalize">
                  {{ feature.text }}
                </p>
              </div>
            </div>
          </div>

          <!-- CTA Button -->
          <div class="relative z-10 mt-8">
            <a :href="service.ctaLink" class="inline-flex items-center gap-3 cursor-pointer group">
              <span class="text-white text-sm font-bold capitalize">
                {{ service.ctaText }}
              </span>
              <!-- Arrow Icon -->
              <svg width="19" height="18" viewBox="0 0 19 18" fill="none" xmlns="http://www.w3.org/2000/svg"
                class="transition-transform group-hover:translate-x-1">
                <path d="M11.5 4.5L16 9M16 9L11.5 13.5M16 9H3" stroke="white" stroke-width="2" stroke-linecap="round"
                  stroke-linejoin="round" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </Container>
  </section>
</template>

<style scoped>
/* Additional styles if needed */
</style>
