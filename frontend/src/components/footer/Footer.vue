<script setup lang="ts">
import InstagramIcon from '@/components/icons/InstagramIcon.vue'
import TwitterIcon from '@/components/icons/TwitterIcon.vue'
import FacebookIcon from '@/components/icons/FacebookIcon.vue'
import LinkedInIcon from '@/components/icons/LinkedInIcon.vue'
import WhatsAppIcon from '@/components/icons/WhatsAppIcon.vue'
import Logo from '../icons/Logo.vue'

interface FooterLink {
  label: string
  href: string
}

interface FooterSection {
  title: string
  links: FooterLink[]
}

const currentYear = new Date().getFullYear()

const productLinks: FooterLink[] = [
  { label: 'Seragam Sekolah', href: '#' },
  { label: 'Seragam Ekstrakurikuler', href: '#' },
  { label: 'Buku Pelajaran', href: '#' },
  { label: 'Alat Tulis (ATK)', href: '#' },
  { label: 'Tas & Aksesoris', href: '#' },
  { label: 'Paket Kebutuhan Siswa', href: '#' }
]

const informationLinks: FooterLink[] = [
  { label: 'Tentang Koperasi', href: '#' },
  { label: 'Cara Belanja', href: '#' },
  { label: 'Cara Pembayaran', href: '#' },
  { label: 'Pengiriman & Tracking', href: '#' },
  { label: 'Kebijakan Pengembalian', href: '#' },
  { label: 'FAQ', href: '#' }
]

const serviceLinks: FooterLink[] = [
  { label: 'Hubungi Kami', href: '#' },
  { label: 'Pusat Bantuan', href: '#' },
  { label: 'Konsultasi Ukuran Seragam', href: '#' },
  { label: 'Layanan Pengiriman ke Rumah', href: '#' },
  { label: 'Layanan Pengambilan di Koperasi', href: '#' }
]

const socialLinks = [
  { name: 'Instagram', href: '#', icon: 'instagram' },
  { name: 'Twitter', href: '#', icon: 'twitter' },
  { name: 'Facebook', href: '#', icon: 'facebook' },
  { name: 'LinkedIn', href: '#', icon: 'linkedin' },
  { name: 'WhatsApp', href: '#', icon: 'whatsapp' }
]

const legalLinks: FooterLink[] = [
  { label: 'Privacy Policy', href: '#' },
  { label: 'Legal Disclaimer', href: '#' }
]
</script>

<template>
  <footer class="bg-[#f2f2f2] w-full">
    <div class="max-w-7xl mx-auto px-4 md:px-8 lg:px-16 xl:px-24 py-16 lg:py-20">
      <!-- Main Footer Content -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 lg:gap-8 mb-16">
        <!-- Company Info Section -->
        <div class="flex flex-col gap-12 lg:col-span-1">
          <!-- Company Header -->
          <div class="flex flex-col gap-8">
            <div class="flex flex-col gap-6">
              <div>
                <Logo/>
              </div>
              <p class="text-[#1e1e1e] text-sm leading-relaxed">
                Menyediakan kebutuhan sekolah lengkap dari TK hingga SMA, mulai dari seragam, buku
                pelajaran, hingga perlengkapan belajar. Kami berkomitmen memberikan layanan cepat,
                harga terjangkau, dan kemudahan akses untuk seluruh siswa dan wali murid.
              </p>
            </div>

            <!-- Contact Information -->
            <div class="flex flex-col gap-7">
              <!-- Operating Hours -->
              <div class="flex flex-col gap-4">
                <h3 class="text-primary text-base font-bold uppercase">Jam Operasional</h3>
                <div class="text-[#1e1e1e] text-sm">
                  <p class="mb-0">Senin – Sabtu 07:00 – 15:00 WIB</p>
                  <p class="mb-0">Belanja online tetap 24 jam</p>
                </div>
              </div>

              <!-- Office Address -->
              <div class="flex flex-col gap-4">
                <h3 class="text-primary text-base font-bold uppercase">Office</h3>
                <div class="text-[#1e1e1e] text-sm">
                  <p class="mb-0">
                    Jl. Jend. Sudirman Kav. 52-53, Kawasan District 8, SCBD Lot. 13
                  </p>
                  <p class="mb-0">SCBD, Jakarta Selatan</p>
                </div>
              </div>

              <!-- Phone -->
              <div class="flex flex-col gap-4">
                <h3 class="text-primary text-base font-bold uppercase">Phone</h3>
                <p class="text-[#1e1e1e] text-sm">+62 812 3456 7890</p>
              </div>

              <!-- Email -->
              <div class="flex flex-col gap-4">
                <h3 class="text-primary text-base font-bold uppercase">Email</h3>
                <p class="text-[#1e1e1e] text-sm">info@koperasiauliya.co.id</p>
              </div>
            </div>
          </div>

        </div>

        <!-- Products Section -->
        <div class="flex flex-col gap-12">
          <h3 class="text-primary text-base font-bold uppercase">Produk</h3>
          <nav class="flex flex-col gap-6">
            <a
              v-for="link in productLinks"
              :key="link.label"
              :href="link.href"
              class="text-[#1e1e1e] text-sm capitalize hover:text-primary transition-colors"
            >
              {{ link.label }}
            </a>
          </nav>
        </div>

        <!-- Information Section -->
        <div class="flex flex-col gap-12">
          <h3 class="text-primary text-base font-bold uppercase">Informasi</h3>
          <nav class="flex flex-col gap-6">
            <a
              v-for="link in informationLinks"
              :key="link.label"
              :href="link.href"
              class="text-[#1e1e1e] text-sm capitalize hover:text-primary transition-colors"
            >
              {{ link.label }}
            </a>
          </nav>
        </div>

        <!-- Help & Services Section -->
        <div class="flex flex-col gap-12">
          <h3 class="text-primary text-base font-bold uppercase">Bantuan & Layanan</h3>
          <nav class="flex flex-col gap-6">
            <a
              v-for="link in serviceLinks"
              :key="link.label"
              :href="link.href"
              class="text-[#1e1e1e] text-sm capitalize hover:text-primary transition-colors"
            >
              {{ link.label }}
            </a>
          </nav>
        </div>
      </div>

      <!-- Bottom Section -->
      <div class="flex flex-col md:flex-row items-center justify-between gap-6 pt-8 border-t border-gray-300">
        <!-- Copyright -->
        <p class="text-[#1e1e1e] text-sm capitalize order-2 md:order-1">
          © {{ currentYear }} Copyright All Rights Reserved.
        </p>

        <!-- Legal Links -->
        <div class="flex items-center gap-6 order-3 md:order-2">
          <a
            v-for="link in legalLinks"
            :key="link.label"
            :href="link.href"
            class="text-[#1e1e1e] text-sm capitalize hover:text-primary transition-colors"
          >
            {{ link.label }}
          </a>
        </div>

        <!-- Social Media Icons -->
        <div class="flex flex-wrap items-center gap-4 order-1 md:order-3">
          <a
            v-for="social in socialLinks"
            :key="social.name"
            :href="social.href"
            :aria-label="social.name"
            :class="[
              'w-[52px] h-[52px] rounded-xl flex items-center justify-center transition-all hover:opacity-80',
              social.icon === 'whatsapp' ? 'bg-[#8dc73c]' : 'bg-white'
            ]"
          >
            <InstagramIcon
              v-if="social.icon === 'instagram'"
              :class="social.icon === 'whatsapp' ? 'text-white' : 'text-primary'"
            />
            <TwitterIcon
              v-else-if="social.icon === 'twitter'"
              :class="social.icon === 'whatsapp' ? 'text-white' : 'text-primary'"
            />
            <FacebookIcon
              v-else-if="social.icon === 'facebook'"
              :class="social.icon === 'whatsapp' ? 'text-white' : 'text-primary'"
            />
            <LinkedInIcon
              v-else-if="social.icon === 'linkedin'"
              :class="social.icon === 'whatsapp' ? 'text-white' : 'text-primary'"
            />
            <WhatsAppIcon v-else-if="social.icon === 'whatsapp'" class="text-white" />
          </a>
        </div>
      </div>
    </div>
  </footer>
</template>
