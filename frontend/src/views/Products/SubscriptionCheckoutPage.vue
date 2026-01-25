<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'
import Container from '@/components/layout/Container.vue'
import Breadcrumb from '@/components/common/Breadcrumb.vue'
import ServiceField from '@/components/features/product-detail/ServiceField.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const itemCode = route.params.itemCode as string
const startDateQuery = route.query.start_date as string

const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const currentStep = ref(1)

const checkoutData = reactive({
    item: null as any,
    start_date: startDateQuery || '',
    notes: '',
    termsAccepted: false
})

const breadcrumbItems = [
    { label: 'Home', to: '/' },
    { label: 'Produk', to: '/products' },
    { label: 'Subscription Checkout', to: '' }
]

onMounted(async () => {
    if (!authStore.isAuthenticated) {
        router.push(`/login?redirect=${route.path}`)
        return
    }

    if (!itemCode) {
        error.value = 'Item Code missing'
        loading.value = false
        return
    }

    try {
        const response = await fetch(`/api/method/webshop.webshop.api.subscription_checkout.get_subscription_item_details?item_code=${itemCode}`)
        const data = await response.json()

        if (data.message) {
            checkoutData.item = data.message
        } else {
            error.value = 'Failed to load item details'
        }
    } catch (err) {
        console.error(err)
        error.value = 'Network error'
    } finally {
        loading.value = false
    }
})

const nextStep = () => {
    if (currentStep.value === 1) {
        if (!checkoutData.start_date) {
            alert('Please select a start date')
            return
        }
    }
    currentStep.value++
}

const prevStep = () => {
    currentStep.value--
}

const showSuccessPopup = ref(false)

const submitRequest = async () => {
    if (!checkoutData.termsAccepted) {
        alert('Mohon setujui syarat dan ketentuan terlebih dahulu')
        return
    }

    submitting.value = true
    try {
        const payload = {
            item_code: itemCode,
            start_date: checkoutData.start_date,
            notes: checkoutData.notes
        }

        const response = await fetch('/api/method/webshop.webshop.api.subscription_checkout.create_subscription_request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': (window as any).csrf_token
            },
            body: JSON.stringify({ data: JSON.stringify(payload) })
        })

        const res = await response.json()
        if (res.message) {
            showSuccessPopup.value = true
        } else {
            throw new Error(res.error || 'Unknown error')
        }
    } catch (err) {
        console.error(err)
        alert('Failed to submit request: ' + err)
    } finally {
        submitting.value = false
    }
}

const handleFinish = () => {
    router.push('/orders?tab=subscriptions')
}

</script>

<template>
    <DefaultLayout store-name="KoperasiAuliya">
        <div class="min-h-screen bg-gray-50 pb-20 pt-8">
            <Container>
                <Breadcrumb :items="breadcrumbItems" class="mb-6" />

                <div v-if="loading" class="flex justify-center p-12">Loading...</div>
                <div v-else-if="error" class="text-red-500 p-12">{{ error }}</div>

                <div v-else class="mx-auto max-w-3xl">

                    <!-- Steps Indicator -->
                    <div class="mb-8 flex items-center justify-between px-12">
                        <div class="flex flex-col items-center gap-2">
                            <div
                                :class="['flex h-7 w-7 items-center justify-center rounded-full font-bold text-sm', currentStep >= 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500']">
                                1</div>
                            <span class="text-sm font-medium">Detail</span>
                        </div>
                        <div class="h-1 flex-1 bg-gray-200 mx-4">
                            <div class="h-full bg-primary transition-all duration-300"
                                :style="{ width: currentStep >= 2 ? '100%' : '0%' }"></div>
                        </div>
                        <div class="flex flex-col items-center gap-2">
                            <div
                                :class="['flex h-7 w-7 items-center justify-center rounded-full font-bold text-sm', currentStep >= 2 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500']">
                                2</div>
                            <span class="text-sm font-medium">Konfirmasi</span>
                        </div>
                    </div>

                    <!-- Step 1: Details -->
                    <div v-if="currentStep === 1" class="rounded-2xl bg-white p-8 shadow-sm">
                        <div class="mb-6 flex items-center gap-6">
                            <div
                                class="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-white font-bold text-sm">
                                1
                            </div>
                            <h2 class="text-xl font-bold">Detail Pendaftaran</h2>
                        </div>

                        <div class="flex mb-8 gap-6 border p-4 rounded-xl">
                            <img v-if="checkoutData.item.image" :src="checkoutData.item.image"
                                class="w-24 h-24 object-cover rounded-lg bg-gray-100" />
                            <div v-else
                                class="w-24 h-24 flex items-center justify-center rounded-lg bg-gray-100 text-gray-400">
                                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z">
                                    </path>
                                </svg>
                            </div>
                            <div>
                                <h3 class="font-bold text-lg">{{ checkoutData.item.item_name }}</h3>
                                <div class="text-gray-500 text-sm prose prose-sm max-w-none"
                                    v-html="checkoutData.item.description"></div>
                                <div class="mt-2 text-primary font-bold">
                                    {{ checkoutData.item.cost.toLocaleString() }}
                                </div>
                            </div>
                        </div>

                        <div class="space-y-6">
                            <div>
                                <label class="mb-2 block text-sm font-medium text-gray-700">Tanggal Mulai</label>
                                <ServiceField :mini="true" :initial-date="checkoutData.start_date"
                                    @select-date="(d) => checkoutData.start_date = d" />
                            </div>

                            <div>
                                <label class="mb-2 block text-sm font-medium text-gray-700">Notes</label>
                                <textarea v-model="checkoutData.notes"
                                    class="w-full rounded-xl border border-gray-300 p-3 focus:border-primary focus:ring-1 focus:ring-primary"
                                    rows="3" placeholder="Tambahkan catatan khusus (opsional)..."></textarea>
                            </div>
                        </div>

                        <div class="mt-8 flex justify-end">
                            <button @click="nextStep"
                                class="rounded-xl bg-primary px-8 py-3 font-bold text-white transition hover:bg-opacity-90">
                                Selanjutnya
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: Confirmation -->
                    <div v-if="currentStep === 2" class="flex flex-col">
                        <!-- Header Card -->
                        <div class="bg-white rounded-t-xl p-8">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-6">
                                    <div
                                        class="flex h-7 w-7 items-center justify-center rounded-full bg-primary text-white font-bold text-sm">
                                        2
                                    </div>
                                    <h2 class="text-base font-bold">Konfirmasi Pendaftaran</h2>
                                </div>
                                <button @click="prevStep" class="text-sm text-gray-500 hover:text-gray-800">
                                    Edit
                                </button>
                            </div>
                        </div>

                        <!-- Informasi Siswa Card -->
                        <div class="bg-white border-t border-gray-200 p-8">
                            <h3 class="text-sm font-bold mb-4">Informasi Siswa</h3>
                            <div class="flex flex-col gap-3">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Nama Lengkap</span>
                                    <span class="text-sm font-medium">{{ authStore.user?.full_name || 'N/A' }}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Email</span>
                                    <span class="text-sm font-medium">{{ authStore.user?.email || 'N/A' }}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Nomor Telepon</span>
                                    <span class="text-sm font-medium">{{ (authStore.user as any)?.phone || '-' }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Informasi Layanan Card -->
                        <div class="bg-white border-t border-gray-200 p-8">
                            <h3 class="text-sm font-bold mb-4">Informasi Layanan</h3>
                            <div class="flex flex-col gap-3">
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Nama Layanan</span>
                                    <span class="text-sm font-medium">{{ checkoutData.item.item_name }}</span>
                                </div>
                                <div class="flex justify-between items-center">
                                    <span class="text-sm text-gray-600">Tanggal Mulai</span>
                                    <span class="text-sm font-medium">{{ checkoutData.start_date }}</span>
                                </div>
                                <div v-if="checkoutData.notes" class="flex justify-between items-start">
                                    <span class="text-sm text-gray-600">Catatan</span>
                                    <span class="text-sm font-medium text-right max-w-[60%]">{{ checkoutData.notes
                                        }}</span>
                                </div>
                            </div>
                        </div>

                        <!-- Estimasi Harga Card -->
                        <div class="bg-white border-t border-gray-200 p-8">
                            <div class="bg-gray-100/80 border border-black/10 rounded-xl p-6 flex flex-col gap-8">
                                <!-- Price Section -->
                                <div class="flex flex-col gap-6 items-start justify-center py-1.5">
                                    <p class="text-sm font-bold text-black text-left w-full">
                                        Total Estimasi Harga Layanan
                                    </p>
                                    <div class="flex flex-col gap-4 w-full">
                                        <p class="text-xl font-bold text-primary text-left">
                                            Rp {{ checkoutData.item.cost.toLocaleString('id-ID') }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Checkbox Card -->
                        <div class="bg-white border-t border-gray-200 p-8">
                            <label class="flex items-start gap-3 cursor-pointer">
                                <input type="checkbox" v-model="checkoutData.termsAccepted"
                                    class="mt-0.5 h-6 w-6 rounded border-2 border-gray-300 text-primary focus:ring-2 focus:ring-primary focus:ring-offset-0 cursor-pointer" />
                                <div class="flex-1">
                                    <p class="text-sm text-gray-700 leading-relaxed">
                                        Dengan ini saya menyatakan bahwa data yang saya masukkan adalah benar dan saya
                                        bersedia untuk mengikuti proses selanjutnya
                                    </p>
                                </div>
                            </label>
                        </div>

                        <!-- Button Card -->
                        <div class="bg-white rounded-b-xl border-t border-gray-200 p-8">
                            <div class="flex gap-3">
                                <button @click="prevStep"
                                    class="flex-1 rounded-lg bg-gray-400 px-8 py-3 font-bold text-sm text-white transition hover:bg-gray-500">
                                    Kembali (isi data alergi)
                                </button>
                                <button @click="submitRequest" :disabled="submitting || !checkoutData.termsAccepted"
                                    :class="[
                                        'flex-1 rounded-lg px-8 py-3 font-bold text-sm text-white transition flex items-center justify-center gap-2',
                                        checkoutData.termsAccepted ? 'bg-primary hover:bg-opacity-90' : 'bg-gray-400 cursor-not-allowed'
                                    ]">
                                    <span v-if="submitting"
                                        class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                                    {{ submitting ? 'Submitting...' : 'Konfirmasi Pendaftaran' }}
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </Container>

            <!-- Success Modal -->
            <div v-if="showSuccessPopup"
                class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
                <div class="w-full max-w-md rounded-2xl bg-white p-8 text-center shadow-xl">
                    <div
                        class="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-full bg-green-100 text-green-500">
                        <svg class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h3 class="mb-2 text-2xl font-bold text-gray-900">Request Submitted!</h3>
                    <p class="mb-8 text-gray-600">
                        Your subscription request has been sent for approval. We will notify you once it is active.
                    </p>
                    <button @click="handleFinish"
                        class="w-full rounded-xl bg-primary py-3 font-bold text-white transition hover:bg-opacity-90">
                        View Orders / Dashboard
                    </button>
                </div>
            </div>

        </div>
    </DefaultLayout>
</template>
