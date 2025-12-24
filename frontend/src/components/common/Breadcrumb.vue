<script setup lang="ts">
import { RouterLink } from 'vue-router'

interface BreadcrumbItem {
  label: string
  to?: string
}

interface Props {
  items: BreadcrumbItem[]
}

defineProps<Props>()
</script>

<template>
  <nav aria-label="Breadcrumb" class="flex items-center gap-2 text-xs md:gap-4 md:text-sm">
    <template v-for="(item, index) in items" :key="index">
      <!-- Separator (chevron) -->
      <svg
        v-if="index > 0"
        class="h-4 w-4 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>

      <!-- Breadcrumb Item -->
      <RouterLink
        v-if="item.to"
        :to="item.to"
        class="whitespace-nowrap font-semibold text-gray-500 transition-colors hover:text-secondary-alt"
      >
        {{ item.label }}
      </RouterLink>
      <span v-else class="min-w-0 truncate font-semibold text-secondary-alt">
        {{ item.label }}
      </span>
    </template>
  </nav>
</template>

<style scoped>
/* Additional styles if needed */
</style>
