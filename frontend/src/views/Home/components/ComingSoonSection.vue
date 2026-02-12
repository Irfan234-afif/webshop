<template>
    <section class="bg-white w-full py-12 sm:py-16">
        <Container>
            <!-- Section Title -->
            <h2 class="text-text text-2xl sm:text-3xl !font-bold capitalize mb-12 sm:mb-16">
                Coming Soon
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div v-for="card in cards" :key="card.title" class="rounded-xl flex flex-col items-start gap-6 p-6 bg-[#f2f2f2] p-8 sm:p-12">
                    <div class="flex items-center gap-4">
                        <div class="p-2 bg-primary rounded-full">
                            <component :is="card.iconComponent" class="w-8 h-8 text-white" />
                        </div>
                        <h3 class="text-xl font-bold text-primary">{{ card.title }}</h3>
                    </div>
                    <p class="text-text-secondary font-medium text-[#5F5F5F]">{{ card.description }}</p>
                    <ul class="flex flex-col gap-3">
                        <li v-for="feature in card.features" :key="feature" class="flex items-center gap-3 text-text-secondary font-semibold text-[#5F5F5F]">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M20 10C20 15.5228 15.5228 20 10 20C4.47715 20 0 15.5228 0 10C0 4.47715 4.47715 0 10 0C15.5228 0 20 4.47715 20 10ZM14.0303 6.96967C14.3232 7.26256 14.3232 7.73744 14.0303 8.03033L9.03033 13.0303C8.73744 13.3232 8.26256 13.3232 7.96967 13.0303L5.96967 11.0303C5.67678 10.7374 5.67678 10.2626 5.96967 9.96967C6.26256 9.67678 6.73744 9.67678 7.03033 9.96967L8.5 11.4393L10.7348 9.2045L12.9697 6.96967C13.2626 6.67678 13.7374 6.67678 14.0303 6.96967Z" fill="#AC208E"/>
                            </svg>
                            <span>{{ feature }}</span>
                        </li>
                    </ul>
                    <p class="text-primary font-bold text-primary text-xl mt-4">Coming Soon</p>
                </div>
            </div>
        </Container>
    </section>
</template>

<script setup lang="ts">
import MemberIcon from '@/components/icons/MemberIcon.vue'
import SavingIcon from '@/components/icons/SavingIcon.vue'
import Container from '@/components/layout/Container.vue'

interface ComingSoonCard {
  title: string
  description: string
  features: string[]
  iconComponent: any
}

const cards: ComingSoonCard[] = [
    {
        title: 'Anggota Koperasi',
        description: 'Fitur pendaftaran anggota koperasi yang memudahkan guru dan staf sekolah untuk bergabung secara resmi sebagai anggota Koperasi Auliya dan menikmati berbagai manfaat khusus.',
        features: ['Akses layanan simpan pinjam', 'Harga Khusus Anggota'],
        iconComponent: MemberIcon
    },
    {
        title: 'Simpanan Anggota',
        description: 'Layanan simpan pinjam khusus anggota koperasi untuk mendukung kebutuhan finansial dengan proses yang transparan, aman, dan dikelola langsung oleh Koperasi Auliya.',
        features: ['Pengajuan Mudah', 'Skema Cicilan Jelas', 'Dikelola seusai aturan koperasi'],
        iconComponent: SavingIcon
    }
]

</script>
