<script setup lang="ts">
import type { SizeChartData } from '@/types/productDetail'

interface Props {
  sizeChart: SizeChartData
}

defineProps<Props>()
</script>

<template>
  <div class="flex flex-col gap-6 py-6">
    <!-- Section Title -->
    <h2 class="text-base font-bold text-gray-900 md:text-lg">Panduan Ukuran</h2>

    <!-- Size Chart Table -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 border border-gray-200">
        <!-- Table Header -->
        <thead class="bg-gray-50">
          <tr>
            <th
              v-for="header in sizeChart.headers"
              :key="header"
              scope="col"
              class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700"
            >
              {{ header }}
            </th>
          </tr>
        </thead>

        <!-- Table Body -->
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr
            v-for="(row, index) in sizeChart.rows"
            :key="index"
            :class="index % 2 === 0 ? 'bg-white' : 'bg-gray-50'"
          >
            <td
              v-for="header in sizeChart.headers"
              :key="`${index}-${header}`"
              class="whitespace-nowrap px-4 py-3 text-sm text-gray-900"
            >
              {{ row[header] }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Size Guide Note -->
    <div class="rounded-lg bg-blue-50 p-4">
      <div class="flex items-start gap-3">
        <svg class="h-5 w-5 flex-shrink-0 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex flex-col gap-1">
          <p class="text-sm font-semibold text-blue-900">Cara Mengukur</p>
          <p class="text-xs text-blue-800">
            Untuk hasil terbaik, ukur langsung pada tubuh menggunakan meteran kain. Pastikan meteran tidak terlalu ketat atau terlalu longgar.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
