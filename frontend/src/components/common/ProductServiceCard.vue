<script setup lang="ts">
import { computed } from 'vue'
import CateringIcon from '@/components/icons/CateringIcon.vue'
import BusIcon from '@/components/icons/BusIcon.vue'
import InfoCircleIcon from '@/components/icons/InfoCircleIcon.vue'

interface Props {
  icon: string
  iconColor?: string
  bgGradient: string
  category: string
  rating: number
  title: string
  description: string
  priceLabel: string
  infoNotes?: string[]
}

interface Emits {
  (e: 'viewDetail'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Map icon string to component
const iconComponent = computed(() => {
  const iconMap: Record<string, any> = {
    CateringIcon,
    BusIcon
  }
  return iconMap[props.icon] || null
})

// Generate stars for rating
const stars = computed(() => {
  const fullStars = Math.floor(props.rating)
  const hasHalfStar = props.rating % 1 >= 0.5
  return { fullStars, hasHalfStar }
})
</script>

<template>
  <article
    class="group flex h-full w-full cursor-pointer flex-col overflow-hidden rounded-xl bg-white"
  >
    <!-- Header with gradient background and icon -->
    <div
      class="relative flex h-[294px] items-center justify-center overflow-hidden rounded-t-xl p-6"
      :style="{ background: bgGradient }"
    >
      <div class="flex h-28 w-28 items-center justify-center rounded-full bg-white">
        <component :is="iconComponent" v-if="iconComponent" class="h-16 w-16" />
      </div>
    </div>

    <!-- Content -->
    <div class="flex flex-1 flex-col gap-4 p-3 md:gap-6">
      <!-- Category and Rating -->
      <div class="flex items-center justify-between">
        <p class="text-xs font-semibold uppercase text-gray-500">
          {{ category }}
        </p>
        <div class="flex items-center gap-1">
          <!-- Stars -->
          <div class="flex items-center gap-0.5">
            <svg
              v-for="i in stars.fullStars"
              :key="`full-${i}`"
              class="h-3 w-3 fill-yellow-400"
              viewBox="0 0 20 20"
            >
              <path
                d="M10 1l2.598 6.329L20 8.292l-5.5 4.635L16.18 20 10 16.329 3.82 20l1.68-7.073L0 8.292l7.402-.963L10 1z"
              />
            </svg>
            <svg v-if="stars.hasHalfStar" class="h-3 w-3 fill-yellow-400" viewBox="0 0 20 20">
              <defs>
                <linearGradient id="half">
                  <stop offset="50%" stop-color="currentColor" />
                  <stop offset="50%" stop-color="transparent" />
                </linearGradient>
              </defs>
              <path
                fill="url(#half)"
                d="M10 1l2.598 6.329L20 8.292l-5.5 4.635L16.18 20 10 16.329 3.82 20l1.68-7.073L0 8.292l7.402-.963L10 1z"
              />
            </svg>
          </div>
          <span class="text-xs font-semibold text-gray-500">({{ rating.toFixed(1) }})</span>
        </div>
      </div>

      <!-- Title and Description -->
      <div class="flex flex-col gap-5">
        <h3 class="text-lg font-bold capitalize text-gray-900">
          {{ title }}
        </h3>
        <p class="line-clamp-2 text-sm font-medium leading-snug text-gray-500">
          {{ description }}
        </p>
      </div>

      <!-- Price Label -->
      <p class="text-lg font-bold capitalize text-secondary-alt">
        {{ priceLabel }}
      </p>

      <!-- Info Notes -->
      <div v-if="infoNotes && infoNotes.length > 0" class="flex flex-col gap-2">
        <div v-for="(note, index) in infoNotes" :key="index" class="flex items-start gap-4">
          <InfoCircleIcon class="mt-0.5 h-5 w-5 shrink-0 text-gray-400" />
          <p class="text-xs font-semibold capitalize leading-tight text-gray-500">
            {{ note }}
          </p>
        </div>
      </div>

      <!-- View Detail Button -->
      <button
        @click="emit('viewDetail')"
        class="mt-auto flex h-12 w-full items-center justify-center rounded-xl border border-gray-300 px-6 py-4 font-bold capitalize text-gray-900 transition-colors hover:bg-gray-50"
      >
        Lihat Detail
      </button>
    </div>
  </article>
</template>

<style scoped>
/* Additional styles if needed */
</style>
