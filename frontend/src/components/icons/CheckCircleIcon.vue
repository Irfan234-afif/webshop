<script setup lang="ts">
interface Props {
  filled?: boolean
}

withDefaults(defineProps<Props>(), {
  filled: false
})
</script>

<template>
  <svg v-if="filled" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" fill="#AC208E"/>
    <path d="M7 12L10 15L17 8" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="9.5" stroke="rgba(30, 30, 30, 0.3)" stroke-width="1.5"/>
  </svg>
</template>
