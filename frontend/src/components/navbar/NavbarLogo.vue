<script setup lang="ts">
import { RouterLink } from 'vue-router'
import Logo from '../icons/Logo.vue'

withDefaults(
  defineProps<{
    storeName?: string
  }>(),
  {
    storeName: 'Webshop'
  }
)
</script>

<template>
  <RouterLink
    to="/"
    class="flex items-center transition-opacity hover:opacity-80 max-w-[120px] sm:max-w-full"
  >
    <Logo/>
  </RouterLink>
</template>
