<script setup lang="ts">
import PrimaryButton from '@/components/common/PrimaryButton.vue'
import Container from '@/components/layout/Container.vue'
import { computed } from 'vue'

interface Props {
  content?: {
    type?: string
    image?: string
    title?: string
    subtitle?: string
    cta_text?: string
    cta_url?: string
    secondary_cta_text?: string
    secondary_cta_url?: string
    right_image?: string
  }
}

const props = defineProps<Props>()

const isImageOnly = computed(() => props.content?.type === 'Image Only')
const backgroundStyle = computed(() => {
  if (isImageOnly.value && props.content?.image) {
    return {
      background: `url(${props.content.image}) center/cover no-repeat`
    }
  }
  // Default gradient if not image only or no image provided
  return {
    background: 'linear-gradient(223.53deg, #AC208E 14.18%, #CE65B7 83.2%)'
  }
})
</script>

<template>
  <section
    class="relative w-full h-[705px] overflow-hidden"
    :style="backgroundStyle"
  >
    <!-- Background decorative image (Only show if NOT image-only mode) -->
    <div v-if="!isImageOnly" class="absolute inset-0 opacity-20">
      <div
        class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1063px] h-[1063px] rounded-full"
        style="background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)"
      />
    </div>

    <!-- Content -->
    <Container class="h-full flex items-center relative z-10" v-if="!isImageOnly && content">
      <div class="flex items-center justify-between w-full">
        <!-- Left Side: Text Content -->
        <div class="flex flex-col gap-12 items-start max-w-3xl">
          <!-- Heading -->
          <h1
            class="font-bold text-5xl leading-tight text-white capitalize"
          >
            {{ content.title || 'Semua Kebutuhan Sekolah, Lengkap dalam Satu Tempat' }}
          </h1>

          <!-- Description -->
          <p class="font-semibold text-base leading-7 text-white/80 max-w-[630px]">
            {{ content.subtitle || 'Belanja seragam, buku pelajaran, dan perlengkapan sekolah kini lebih mudah. Tersedia pilihan sesuai jenjang dan kebutuhan murid untuk memudahkan wali murid dan koperasi dalam setiap pembelian.' }}
          </p>

          <!-- CTA Buttons -->
          <div class="flex gap-8 items-center">
            <template v-if="content.cta_text">
              <!-- Check if cta_url is external or internal -->
               <!-- For simplicity using PrimaryButton which likely renders a button or link depending on usage. 
                    If it needs to be a link, we might need a router-link or a tag. 
                    Assuming PrimaryButton might wrap a button, or handle clicks. 
                    If it doesn't support 'to' or 'href', we wrap it or use it as is if logic handled elsewhere.
                    However, usually UI components have an encoding for links. 
                    Let's assume we can wrap it in an anchor or router-link if needed, but existing code didn't use links yet. 
                    Wait, existing code didn't have hrefs. I will render text.
                -->
               <a :href="content.cta_url || '#'">
                 <PrimaryButton variant="primary" size="large" icon="arrow">
                   {{ content.cta_text }}
                 </PrimaryButton>
               </a>
            </template>
            <!-- Fallback if no data -->
            <PrimaryButton v-else variant="primary" size="large" icon="arrow">
              Belanja Sekarang
            </PrimaryButton>

            <template v-if="content.secondary_cta_text">
               <a :href="content.secondary_cta_url || '#'">
                 <PrimaryButton variant="outline" size="large" icon="arrow">
                   {{ content.secondary_cta_text }}
                 </PrimaryButton>
               </a>
            </template>
             <PrimaryButton v-else variant="outline" size="large" icon="arrow">
               Hubungi Koperasi
             </PrimaryButton>
          </div>
        </div>

        <!-- Right Side: Image (Optional) -->
        <div v-if="content.right_image" class="hidden lg:block relative z-10">
            <img :src="content.right_image" alt="Hero Image" class="max-h-[500px] w-auto object-contain" />
        </div>
      </div>
    </Container>
  </section>
</template>

<style scoped>
/* Additional gradient overlay for depth */
section::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 70% 50%, rgba(206, 101, 183, 0.3) 0%, transparent 60%);
  pointer-events: none;
  /* Hide overlay in image-only mode if desired, or keep it for text readability if text were overlaid. 
     But for 'image only', usually we want clean image. */
  display: v-bind("isImageOnly ? 'none' : 'block'");
}
</style>
