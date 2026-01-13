<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'

interface Props {
  images: string[]
  selectedIndex: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  selectImage: [index: number]
}>()

// Computed main image
const mainImage = computed(() => props.images[props.selectedIndex] || props.images[0])

// Keyboard navigation
const handleKeydown = (event: KeyboardEvent) => {
  if (props.images.length === 0) return

  switch (event.key) {
    case 'ArrowLeft':
      event.preventDefault()
      selectPreviousImage()
      break
    case 'ArrowRight':
      event.preventDefault()
      selectNextImage()
      break
  }
}

const selectPreviousImage = () => {
  const newIndex = (props.selectedIndex - 1 + props.images.length) % props.images.length
  emit('selectImage', newIndex)
}

const selectNextImage = () => {
  const newIndex = (props.selectedIndex + 1) % props.images.length
  emit('selectImage', newIndex)
}

// Add keyboard listener
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="flex w-full flex-col gap-4">
    <!-- Main Image -->
    <div class="relative aspect-[621/504] w-full overflow-hidden rounded-xl bg-gray-100">
      <img :src="mainImage" :alt="`Product image ${selectedIndex + 1}`" class="h-full w-full object-cover"
        loading="eager" />

      <!-- Navigation Arrows (optional, for larger screens) -->
      <div v-if="images.length > 1" class="absolute inset-0 hidden items-center justify-between px-4 md:flex">
        <button type="button"
          class="flex h-10 w-10 items-center justify-center rounded-full bg-white/80 shadow-md transition-all hover:bg-white hover:shadow-lg"
          @click="selectPreviousImage" aria-label="Previous image">
          <svg class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <button type="button"
          class="flex h-10 w-10 items-center justify-center rounded-full bg-white/80 shadow-md transition-all hover:bg-white hover:shadow-lg"
          @click="selectNextImage" aria-label="Next image">
          <svg class="h-5 w-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Thumbnail Gallery -->
    <div v-if="images.length > 1" class="flex gap-2 overflow-x-auto p-2" role="tablist" aria-label="Product images">
      <button v-for="(image, index) in images" :key="index" type="button" role="tab"
        :aria-selected="index === selectedIndex" :aria-label="`View image ${index + 1}`" :class="[
          'flex-shrink-0 overflow-hidden rounded-lg transition-all',
          'h-24 w-24',
          index === selectedIndex
            ? 'ring-2 ring-secondary-alt ring-offset-2'
            : 'opacity-60 hover:opacity-100'
        ]" @click="emit('selectImage', index)">
        <img :src="image" :alt="`Thumbnail ${index + 1}`" class="h-full w-full object-cover" loading="lazy" />
      </button>
    </div>
  </div>
</template>
