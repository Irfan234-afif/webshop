<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Container from '@/components/layout/Container.vue'
import type { WebshopOffer } from '@/types/offers'

const offers = ref<WebshopOffer[]>([])
const loading = ref(true)

const fetchOffers = async () => {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.offers.get_offers')
    const data = await response.json()
    if (data.message) {
      offers.value = data.message
    }
  } catch (error) {
    console.error('Failed to fetch webshop offers:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchOffers()
})

const getCardStyle = (color: string) => {
  if (!color) return { backgroundColor: 'rgba(0,0,0,0.05)' } // Fallback
  
  // Parse hex to rgba with 0.15 opacity
  const hex = color.replace('#', '')
  if (hex.length < 6) return { backgroundColor: 'rgba(0,0,0,0.05)' } // Invalid hex

  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)
  
  return {
    backgroundColor: `rgba(${r}, ${g}, ${b}, 0.15)`
  }
}

const getImageContainerGradient = (color: string) => {
    if (!color) return { background: '#f5f5f5' }
    return {
        background: `linear-gradient(135deg, ${color} 0%, ${color}DD 100%)`
    }
}
</script>

<template>
  <section v-if="offers.length > 0" class="py-12 bg-white">
    <Container>
      <h2 class="font-bold text-[28px] mb-12 text-[#1e1e1e]">Dapatkan Diskon Hingga 70%</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <a 
          v-for="(offer, index) in offers" 
          :key="index"
          :href="offer.cta_url || '#'"
          class="block group"
        >
          <div 
            class="relative rounded-[12px] overflow-hidden flex flex-col h-[568px] p-[48px] transition-transform hover:scale-[1.02] duration-300"
            :style="getCardStyle(offer.theme_color)"
          >
            <!-- Content -->
            <div class="flex flex-col items-start text-left z-10 w-full">
              <h3 class="font-bold text-[18px] mb-6 text-[#1e1e1e]">{{ offer.title }}</h3>
              <div 
                class="font-bold text-[48px] mb-8 leading-none"
                :style="{ color: offer.theme_color }"
              >
                {{ offer.highlight }}
              </div>
              <h4 class="font-bold text-[16px] mb-3 text-[#1e1e1e]">{{ offer.subtitle }}</h4>
              <p class="text-[14px] text-[#1e1e1e]/80 leading-relaxed">{{ offer.description }}</p>
            </div>

            <!-- Image Section -->
            <!-- Figma uses a specific container at the bottom. 
                 We'll use absolute positioning to pin it to bottom. -->
            <div 
                class="absolute bottom-0 left-0 right-0 h-[270px] overflow-hidden" 
            >
                <!-- Background Gradient for Image Area -->
                <div 
                    class="absolute inset-0 w-full h-full"
                    :style="getImageContainerGradient(offer.theme_color)"
                ></div>
                
                <!-- Image -->
                <div class="absolute inset-0 flex items-end justify-center pb-0">
                    <img 
                      v-if="offer.image"
                      :src="offer.image" 
                      alt="Offer Image"
                      class="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-105"
                    />
                </div>
            </div>
          </div>
        </a>
      </div>
    </Container>
  </section>
</template>
