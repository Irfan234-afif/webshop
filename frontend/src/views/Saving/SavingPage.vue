<template>
  <DefaultLayout>
    <Container class="py-6">
      <!-- Breadcrumb -->
      <Breadcrumb :items="[
        { label: 'Home', to: '/' },
        { label: 'Simpanan Anggota Koperasi' }
      ]" class="mb-6" />
      <!-- Header section with back button and Search Box placeholder -->
      <h1 class="text-xl font-bold text-gray-900 mb-10">Simpanan Anggota Koperasi</h1>

      <!-- Main Content -->
      <main class="flex-1 px-4">
        <!-- Tabs -->
        <div class="flex border-b border-divider mt-2 mb-6 gap-6">
          <button 
            v-for="tab in tabs" :key="tab.id"
            @click="changeTab(tab.id as any)"
            class="pb-3 text-lg font-semibold transition-colors border-b-2"
            :class="[
              currentTab === tab.id 
                ? 'text-primary border-primary' 
                : 'text-text-secondary border-transparent hover:text-text'
            ]"
          >
            {{ tab.label }}
          </button>
        </div>

        <!-- Tab Content -->
        <div class="tab-content transition-all">
          <KeepAlive>
            <component :is="activeComponent" />
          </KeepAlive>
        </div>
      </main>
    </Container>
  </DefaultLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import MandatorySavingsTab from '@/components/Saving/MandatorySavingsTab.vue'
import VoluntarySavingsTab from '@/components/Saving/VoluntarySavingsTab.vue'
import HistoryTab from '@/components/Saving/HistoryTab.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
// Add store imports when integrating data
// import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()

type TabType = 'wajib' | 'sukarela' | 'riwayat'

const currentTab = ref<TabType>(
  (route.query.tab as TabType) || 'wajib'
)

const tabs: { id: TabType, label: string }[] = [
  { id: 'wajib', label: 'Simpanan Wajib' },
  { id: 'sukarela', label: 'Simpanan Sukarela' },
  { id: 'riwayat', label: 'Riwayat' }
]

const changeTab = (tab: TabType) => {
  router.push({ query: { ...route.query, tab } })
}

watch(() => route.query.tab, (newTab) => {
  const validTab = (newTab as TabType) || 'wajib'
  if (currentTab.value !== validTab) {
    currentTab.value = validTab
  }
}, { immediate: true })

const activeComponent = computed(() => {
  switch (currentTab.value) {
    case 'wajib':
      return MandatorySavingsTab
    case 'sukarela':
      return VoluntarySavingsTab
    case 'riwayat':
      return HistoryTab
    default:
      return MandatorySavingsTab
  }
})
</script>

<style scoped>
/* Scoped styles if necessary, rely mainly on Tailwind preset classes */
</style>
