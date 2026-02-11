<script setup lang="ts">
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import { ClockIcon } from '@heroicons/vue/24/outline'
import { useRouter } from 'vue-router'
import PrimaryButton from '@/components/common/PrimaryButton.vue'

const router = useRouter()
</script>

<template>
  <DefaultLayout>
    <div class="coming-soon-container">
      <div class="content-wrapper">
        <div class="icon-wrapper">
          <ClockIcon class="w-16 h-16 text-primary" />
        </div>
        <h1 class="title">Coming Soon!</h1>
        <p class="description text-text-secondary">
          Fitur ini sedang dalam pengembangan. Kami akan segera menghadirkannya untuk Anda.
        </p>
        <div class="actions">
          <PrimaryButton variant="primary" @click="router.push('/')">
            Kembali ke Beranda
          </PrimaryButton>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<style scoped>
.coming-soon-container {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  @apply bg-background-soft;
}

.content-wrapper {
  text-align: center;
  max-width: 480px;
  background: white;
  padding: 3rem 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.icon-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 4rem;
  height: 4rem;
  @apply bg-background-soft;
  border-radius: 50%;
  margin-bottom: 1.5rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  @apply text-text-heading;
  margin-bottom: 1rem;
}

.description {
  font-size: 1.125rem;
  line-height: 1.75rem;
  margin-bottom: 2rem;
}
</style>
