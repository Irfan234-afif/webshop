<script setup lang="ts">
import Container from '@/components/layout/Container.vue'
</script>

<template>
  <section class="w-full bg-white py-24">
    <Container>
      <div
        class="relative w-full h-[416px] overflow-hidden rounded-xl bg-primary"
        data-name="Helping families container"
      >
        <!-- Background decorative image -->
        <div class="absolute inset-0 pointer-events-none">
          <!-- Main decorative image positioned on the right -->
          <div class="absolute right-0 top-1/2 -translate-y-1/2 w-[600px] h-full opacity-90">
            <img
              src="https://www.figma.com/api/mcp/asset/60118137-d575-4ad5-9462-4afb35f4e6a3"
              alt=""
              class="absolute right-[-100px] top-1/2 -translate-y-1/2 w-[800px] h-auto object-contain rotate-[-2deg]"
            />
          </div>

          <!-- Vertical decorative stripes -->
          <div
            v-for="i in 40"
            :key="i"
            class="absolute h-full w-[26px] opacity-50"
            :style="{
              left: `${-84 + (i - 1) * 25.25}px`,
              top: '0',
              transform: 'rotate(-2.2deg)'
            }"
          >
            <div class="w-full h-full overflow-hidden">
              <img
                src="https://www.figma.com/api/mcp/asset/60118137-d575-4ad5-9462-4afb35f4e6a3"
                alt=""
                class="w-full h-full object-cover"
                style="object-position: left center"
              />
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="relative z-10 h-full flex items-center px-[90px]">
          <div class="flex flex-col gap-12 max-w-[757px]">
            <!-- Heading -->
            <h2
              class="font-bold text-[32px] leading-[1.2] text-white capitalize"
              
            >
              Persiapan Tahun Ajaran Baru 2025/2026
            </h2>

            <!-- Description -->
            <p class="font-semibold text-base leading-7 text-white/80 max-w-[630px]">
              Lengkapi kebutuhan sekolah mulai dari seragam, buku pelajaran, hingga perlengkapan ATK dengan harga khusus untuk siswa baru
            </p>

            <!-- CTA Button -->
            <button
              class="inline-flex items-center justify-center gap-3 px-8 py-4 bg-white text-primary font-bold text-sm rounded-xl hover:opacity-90 transition-all duration-300 cursor-pointer capitalize"
              
            >
              Belanja Sekarang
              <span class="w-5 h-5">
                <img
                  src="https://www.figma.com/api/mcp/asset/67a401bb-071c-4604-b7e8-b71130afe6ff"
                  alt="arrow"
                  class="w-full h-full object-contain"
                />
              </span>
            </button>
          </div>
        </div>
      </div>
    </Container>
  </section>
</template>

<style scoped>
/* Additional styling for the section */
section {
  position: relative;
}

/* Ensure proper stacking context */
.relative {
  position: relative;
}
</style>
