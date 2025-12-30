<script setup lang="ts">
interface Props {
  title: string
  description: string
  bgGradient: string
  link?: string
}

defineProps<Props>()
</script>

<template>
  <div
    class="flex flex-col h-full justify-between overflow-hidden rounded-xl p-12 relative"
    :style="{ background: bgGradient }"
  >
    <!-- Content -->
    <div class="flex flex-col gap-12 items-start relative shrink-0 w-full z-10">
      <!-- Icon -->
      <div class="bg-white overflow-hidden rounded-full shrink-0 w-14 h-14 flex items-center justify-center">
        <slot name="icon" />
      </div>

      <!-- Text Content -->
      <div class="flex flex-col gap-6 items-start w-full">
        <h3 class="font-bold text-xl leading-tight text-white uppercase">
          {{ title }}
        </h3>
        <p class="font-medium text-sm leading-relaxed text-white/80">
          {{ description }}
        </p>
      </div>
    </div>

    <!-- CTA Button -->
    <div class="flex items-center gap-3 h-8 justify-start pt-4 relative z-10">
      <button
        class="font-bold text-sm leading-tight text-white uppercase hover:underline transition-all"
      >
        Lihat Detail
      </button>
      <span class="w-5 h-5">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M14.43 5.93L20.5 12L14.43 18.07"
            stroke="white"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            d="M4 12H20"
            stroke="white"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </span>
    </div>

    <!-- Background decorative images slot -->
    <slot name="background" />
  </div>
</template>
