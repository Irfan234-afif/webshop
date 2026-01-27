<script setup lang="ts">
import { computed } from 'vue'
import { createResource } from 'frappe-ui'
import ServiceCard from '@/components/common/ServiceCard.vue'

const servicesResource = createResource({
  url: 'webshop.webshop.doctype.webshop_service.webshop_service.get_active_services',
  auto: true
})

const services = computed(() => {
  if (servicesResource.data) {
    return servicesResource.data
  }
  return []
})
</script>

<template>
  <section class="bg-white w-full py-12">
    <Container>
      <!-- Section Title -->
      <h2 class="!font-bold text-xl md:text-3xl leading-snug text-text capitalize mb-16">
        Produk & Layanan Koperasi
      </h2>

      <!-- Service Cards Grid -->
      <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <ServiceCard v-for="service in services" :key="service.name" :title="service.title"
          :description="service.description" :bg-gradient="service.bg_gradient" :route="service.route">
          <template #icon>
            <div v-html="service.icon_svg" :style="{ color: service.icon_color }" class="w-8 h-8 flex items-center justify-center [&>svg]:w-full [&>svg]:h-full"></div>
          </template>
        </ServiceCard>
      </div>
    </Container>
  </section>
</template>
