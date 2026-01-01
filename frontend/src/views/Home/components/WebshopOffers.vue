<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import Container from '@/components/layout/Container.vue'
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
import type { WebshopOffer } from '@/types/offers'

const offers = ref<WebshopOffer[]>([])
const loading = ref(true)

// Scroll State
const scrollContainer = ref<HTMLElement | null>(null)
const scrollPosition = ref(0)

const fetchOffers = async () => {
  try {
    const response = await fetch('/api/method/webshop.webshop.api.offers.get_offers')
    const data = await response.json()
    if (data.message) {
      offers.value = data.message
      // Update scroll position after data is loaded and DOM updated
      setTimeout(updateScrollPosition, 100)
    }
  } catch (error) {
    console.error('Failed to fetch webshop offers:', error)
  } finally {
    loading.value = false
  }
}

// Scroll Methods
const scroll = (direction: 'left' | 'right') => {
  if (!scrollContainer.value) return

  const scrollAmount = 400
  const newPosition =
    direction === 'left'
      ? scrollContainer.value.scrollLeft - scrollAmount
      : scrollContainer.value.scrollLeft + scrollAmount

  scrollContainer.value.scrollTo({
    left: newPosition,
    behavior: 'smooth'
  })
}

const updateScrollPosition = () => {
  if (scrollContainer.value) {
    scrollPosition.value = scrollContainer.value.scrollLeft
  }
}

// Computed
const isAtEnd = computed(() => {
  if (!scrollContainer.value) return false
  const container = scrollContainer.value
  // simple check
  return scrollPosition.value >= (container.scrollWidth - container.clientWidth - 5)
})

const isAtStart = computed(() => scrollPosition.value <= 5)

onMounted(() => {
  fetchOffers()
  updateScrollPosition()
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
    <Container class="flex flex-col gap-8">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <h2 class="!font-bold text-xl md:text-3xl text-[#1e1e1e]">Dapatkan Diskon Hingga 70%</h2>

        <!-- Navigation Arrows -->
        <div class="flex items-center gap-4">
          <!-- Left Arrow -->
          <button class="w-12 h-12 rounded-full overflow-hidden flex items-center justify-center transition-colors"
            :class="isAtStart
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-secondary-alt'
              " @click="scroll('left')" :disabled="isAtStart" aria-label="Scroll left">
            <ArrowIcon class="h-5 w-5" />
          </button>

          <!-- Right Arrow -->
          <button class="w-12 h-12 rounded-full overflow-hidden flex items-center justify-center transition-colors"
            :class="isAtEnd
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-secondary-alt'
              " @click="scroll('right')" :disabled="isAtEnd" aria-label="Scroll right">
            <ArrowIcon class="h-5 w-5 rotate-180" />
          </button>
        </div>
      </div>

      <!-- Scrollable Container -->
      <div ref="scrollContainer"
        class="flex items-stretch gap-4 overflow-x-auto overflow-y-visible scrollbar-hide py-8 px-4"
        style="scroll-snap-type: x mandatory" @scroll="updateScrollPosition">
        <div v-for="(offer, index) in offers" :key="index"
          class="block group flex-shrink-0 w-full sm:w-[calc(100%-32px)] md:w-[calc(50%-16px)] lg:w-[calc(33.333%-16px)]"
          style="scroll-snap-align: start">
          <div
            class="relative rounded-[12px] h-full overflow-hidden flex flex-col min-h-[568px] transition-transform hover:scale-[1.02] hover:z-10 duration-300"
            :style="getCardStyle(offer.theme_color)">
            <!-- Content -->
            <div class="flex flex-col items-start text-left z-10 w-full p-[24px] md:p-[48px] flex-1">
              <h3 class="font-bold text-[18px] mb-6 text-[#1e1e1e]">{{ offer.title }}</h3>
              <div class="font-bold text-[48px] mb-8 leading-none" :style="{ color: offer.theme_color }">
                {{ offer.highlight }}
              </div>
              <h4 class="font-bold text-[16px] mb-3 text-[#1e1e1e]">{{ offer.subtitle }}</h4>
              <p class="text-md text-[#1e1e1e]/80 leading-relaxed">{{ offer.description }}</p>
            </div>

            <!-- Image Section -->
            <div class="relative w-full h-[270px] overflow-hidden mt-auto">
              <!-- Background Gradient -->
              <div class="absolute inset-0 w-full h-full" :style="getImageContainerGradient(offer.theme_color)"></div>

              <!-- Image -->
              <div class="absolute inset-0 flex items-end justify-center pb-0">
                <img v-if="offer.image" :src="offer.image" alt="Offer Image"
                  class="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-105" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Container>
  </section>
</template>

<style scoped>
/* Hide scrollbar for Chrome, Safari and Opera */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

/* Hide scrollbar for IE, Edge and Firefox */
.scrollbar-hide {
  -ms-overflow-style: none;
  /* IE and Edge */
  scrollbar-width: none;
  /* Firefox */
}
</style>
