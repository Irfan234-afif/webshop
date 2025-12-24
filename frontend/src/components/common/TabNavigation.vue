<script setup lang="ts">
import { computed } from 'vue'

export interface Tab {
  key: string
  label: string
  disabled?: boolean
}

interface Props {
  tabs: Tab[]
  activeTab: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  change: [key: string]
}>()

const handleTabClick = (tab: Tab) => {
  if (!tab.disabled && tab.key !== props.activeTab) {
    emit('change', tab.key)
  }
}

const handleKeydown = (event: KeyboardEvent, tab: Tab, index: number) => {
  if (tab.disabled) return

  switch (event.key) {
    case 'Enter':
    case ' ':
      event.preventDefault()
      handleTabClick(tab)
      break
    case 'ArrowRight':
      event.preventDefault()
      focusNextTab(index)
      break
    case 'ArrowLeft':
      event.preventDefault()
      focusPreviousTab(index)
      break
  }
}

const focusNextTab = (currentIndex: number) => {
  const nextIndex = (currentIndex + 1) % props.tabs.length
  const nextTab = document.querySelector(`[data-tab-index="${nextIndex}"]`) as HTMLElement
  nextTab?.focus()
}

const focusPreviousTab = (currentIndex: number) => {
  const prevIndex = (currentIndex - 1 + props.tabs.length) % props.tabs.length
  const prevTab = document.querySelector(`[data-tab-index="${prevIndex}"]`) as HTMLElement
  prevTab?.focus()
}
</script>

<template>
  <div class="border-b border-gray-200">
    <nav
      class="-mb-px flex gap-6 overflow-x-auto"
      role="tablist"
      aria-label="Product tabs"
    >
      <button
        v-for="(tab, index) in tabs"
        :key="tab.key"
        type="button"
        role="tab"
        :aria-selected="tab.key === activeTab"
        :aria-disabled="tab.disabled"
        :data-tab-index="index"
        :tabindex="tab.key === activeTab ? 0 : -1"
        :class="[
          'whitespace-nowrap border-b-2 px-1 py-4 text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-secondary-alt focus:ring-offset-2',
          tab.key === activeTab
            ? 'border-secondary-alt text-secondary-alt'
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
          tab.disabled
            ? 'cursor-not-allowed opacity-50'
            : 'cursor-pointer'
        ]"
        @click="handleTabClick(tab)"
        @keydown="handleKeydown($event, tab, index)"
      >
        {{ tab.label }}
      </button>
    </nav>
  </div>
</template>
