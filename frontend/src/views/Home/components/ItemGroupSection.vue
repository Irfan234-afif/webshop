<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Container from '@/components/layout/Container.vue'
import ProductCard from '@/components/common/ProductCard.vue'
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
import type { Product, PromotionalCard } from '@/types/itemGroup'

interface Props {
  title: string
  products: Product[]
  promotionalCard?: PromotionalCard
}

const props = defineProps<Props>()

import { useWishlistStore } from '@/stores/wishlist'
const wishlistStore = useWishlistStore()

// State
const scrollContainer = ref<HTMLElement | null>(null)
const scrollPosition = ref(0)

// Methods
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
  const currentScroll = scrollPosition.value

  if (!scrollContainer.value) return false

  const container = scrollContainer.value
  const maxScroll = container.scrollWidth - container.clientWidth

  return currentScroll >= maxScroll - 5
})

const isAtStart = computed(() => scrollPosition.value <= 5)

const gradientStyle = computed(() => ({
  background: `linear-gradient(136.56deg, ${props.promotionalCard?.gradientFrom} 0%, ${props.promotionalCard?.gradientTo} 100.03%)`
}))

// Lifecycle
onMounted(() => {
  updateScrollPosition()
})
</script>

<template>
  <section class="bg-white w-full py-12">
    <Container class="flex flex-col gap-17">
      <!-- Section Header -->
      <div class="flex items-center justify-between gap-17 mb-16">
        <router-link :to="`/products?categories=${title}`">
          <h2 class="flex-1 !font-bold text-xl md:text-3xl leading-snug text-gray-900 capitalize">
            {{ title }}
          </h2>
        </router-link>

        <!-- Navigation Arrows -->
        <div class="flex items-center gap-4">
          <!-- Left Arrow -->
          <button
            class="w-8 h-8 md:w-12 md:h-12 rounded-full overflow-hidden flex items-center justify-center transition-colors"
            :class="isAtStart
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-secondary-alt'
              " @click="scroll('left')" :disabled="isAtStart" aria-label="Scroll left">
            <ArrowIcon class="h-5 w-5" />
          </button>

          <!-- Right Arrow -->
          <button
            class="w-8 h-8 md:w-12 md:h-12 rounded-full overflow-hidden flex items-center justify-center transition-colors"
            :class="isAtEnd
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-secondary-alt'
              " @click="scroll('right')" :disabled="isAtEnd" aria-label="Scroll right">
            <ArrowIcon class="h-5 w-5 rotate-180" />
          </button>
        </div>
      </div>

      <!-- Products Carousel -->
      <div ref="scrollContainer" class="flex items-stretch gap-4 overflow-x-auto overflow-y-visible scrollbar-hide"
        style="scroll-snap-type: x mandatory" @scroll="updateScrollPosition">
        <!-- Product Cards -->
        <div v-for="product in products" :key="product.id" class="flex-shrink-0 w-[287px] md:w-[387px] flex"
          style="scroll-snap-align: start">
          <ProductCard :image="product.image" :route="product.route" :category="product.category"
            :rating="product.rating" :title="product.title" :description="product.description" :price="product.price"
            :original-price-range="product.originalPriceRange" :discount="product.discount"
            :has-discount="product.hasDiscount" :is-in-wishlist="wishlistStore.isInWishlist(product.itemCode)"
            @view-detail="() => console.log('View detail:', product.id)"
            @toggle-wishlist="() => wishlistStore.toggleWishlist(product.itemCode)" />
        </div>

        <!-- Promotional Card -->
        <div v-if="promotionalCard"
          class="flex-shrink-0 w-[287px] md:w-[387px] flex flex-col justify-between p-12 rounded-xl"
          :style="{ ...gradientStyle, 'scroll-snap-align': 'start' }">
          <!-- Icon -->
          <div class="bg-white rounded-full w-14 h-14 flex items-center justify-center">
            <div v-html="promotionalCard.icon" />
          </div>

          <!-- Content -->
          <div class="flex flex-col gap-12">
            <div class="flex flex-col gap-6 capitalize whitespace-pre-wrap">
              <h3 class="font-bold text-xl leading-tight text-white">
                {{ promotionalCard.title }}
              </h3>
              <p class="text-sm font-medium leading-relaxed text-white/80">
                {{ promotionalCard.description }}
              </p>
            </div>

            <!-- CTA Button -->
            <button class="flex items-center gap-3 h-8 justify-start pt-4 hover:underline transition-all group">
              <span class="text-sm font-bold text-white capitalize">
                {{ promotionalCard.ctaText }}
              </span>
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none">
                <path d="M5 12h14m0 0l-6-6m6 6l-6 6" stroke="white" stroke-width="2" stroke-linecap="round"
                  stroke-linejoin="round" />
              </svg>
            </button>
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
