<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { NavLink } from '@/types/navigation'

withDefaults(
  defineProps<{
    links?: NavLink[]
  }>(),
  {
    links: () => [
      { label: 'Home', to: '/', exact: true },
      { label: 'Shop', to: '/shop' },
      { label: 'Categories', to: '/categories' },
      { label: 'About', to: '/about' }
    ]
  }
)
</script>

<template>
  <nav class="hidden md:flex items-center space-x-8">
    <RouterLink
      v-for="link in links"
      :key="link.to"
      :to="link.to"
      :exact="link.exact"
      class="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white font-medium transition-colors relative group"
    >
      {{ link.label }}
      <span class="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-600 group-hover:w-full transition-all duration-300"></span>
    </RouterLink>
  </nav>
</template>
