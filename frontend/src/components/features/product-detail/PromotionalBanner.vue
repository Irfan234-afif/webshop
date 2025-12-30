<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  content?: {
    type?: string
    image?: string
    title?: string
    subtitle?: string
    cta_text?: string
    cta_url?: string
    right_image?: string
  }
}

const props = defineProps<Props>()

const isImageOnly = computed(() => props.content?.type === 'Image Only')
const backgroundStyle = computed(() => {
  if (props.content?.image) {
    return {
      backgroundImage: `url(${props.content.image})`,
      backgroundPosition: 'center',
      backgroundSize: 'cover',
      backgroundRepeat: 'no-repeat'
    }
  }
  // Default gradient if no image
  return {} // Use class based gradient
})

// Fallback values
const title = computed(() => props.content?.title || 'Persiapan Tahun Ajaran Baru 2025/2026')
const subtitle = computed(() => props.content?.subtitle || 'Lengkapi kebutuhan sekolah mulai dari seragam, buku pelajaran, hingga perlengkapan ATK dengan harga khusus untuk siswa baru')
const ctaText = computed(() => props.content?.cta_text || 'Belanja Sekarang')
const ctaLink = computed(() => props.content?.cta_url || '/products')
</script>

<template>
  <div
    class="relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-600 to-purple-800 px-6 py-12 md:px-12 lg:px-16"
    :class="{ 'bg-none': props.content?.image }"
    :style="backgroundStyle"
  >
    <!-- Content Container -->
    <div 
        class="relative z-10 mx-auto grid max-w-7xl grid-cols-1 items-center gap-8 lg:grid-cols-2"
        v-if="!isImageOnly"
    >
      <!-- Left: Text Content -->
      <div class="flex flex-col gap-6">
        <h2 class="text-2xl font-bold leading-tight text-white md:text-3xl">
          {{ title }}
        </h2>
        <p class="max-w-lg text-sm leading-relaxed text-purple-100 md:text-base">
          {{ subtitle }}
        </p>
        <div>
          <a
            :href="ctaLink"
            class="inline-flex h-14 items-center justify-center gap-2 rounded-xl bg-white px-8 text-sm font-bold text-purple-700 transition-all hover:bg-purple-50 active:scale-95"
          >
            {{ ctaText }}
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </a>
        </div>
      </div>

      <!-- Right: Product Images (decorative) -->
      <div class="relative hidden h-64 lg:block">
        
        <template v-if="content?.right_image">
            <img :src="content.right_image" alt="Promo" class="h-full object-contain mx-auto" />
        </template>
        <template v-else>
            <!-- Default Decorative circles -->
            <div class="absolute right-0 top-0 h-32 w-32 rounded-full bg-purple-500 opacity-20 blur-3xl"></div>
            <div class="absolute bottom-0 right-20 h-40 w-40 rounded-full bg-purple-400 opacity-20 blur-3xl"></div>

            <!-- Product silhouettes/icons -->
            <div class="absolute inset-0 flex items-center justify-end opacity-30">
            <svg class="h-full w-full" viewBox="0 0 400 300" fill="none">
                <!-- Simplified product shapes -->
                <rect x="50" y="100" width="80" height="120" rx="8" fill="white" opacity="0.3" />
                <rect x="150" y="80" width="80" height="140" rx="8" fill="white" opacity="0.5" />
                <rect x="250" y="90" width="80" height="130" rx="8" fill="white" opacity="0.4" />
            </svg>
            </div>
        </template>
      </div>
    </div>

    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10" v-if="!props.content?.image">
      <div class="absolute inset-0" style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 20px 20px;"></div>
    </div>
  </div>
</template>
