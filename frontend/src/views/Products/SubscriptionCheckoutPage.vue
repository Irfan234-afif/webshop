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
    notes: ''
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
    router.push('/orders') // or wherever
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
                                :class="['flex h-10 w-10 items-center justify-center rounded-full font-bold', currentStep >= 1 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500']">
                                1</div>
                            <span class="text-sm font-medium">Details</span>
                        </div>
                        <div class="h-1 flex-1 bg-gray-200 mx-4">
                            <div class="h-full bg-primary transition-all duration-300"
                                :style="{ width: currentStep >= 2 ? '100%' : '0%' }"></div>
                        </div>
                        <div class="flex flex-col items-center gap-2">
                            <div
                                :class="['flex h-10 w-10 items-center justify-center rounded-full font-bold', currentStep >= 2 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-500']">
                                2</div>
                            <span class="text-sm font-medium">Confirmation</span>
                        </div>
                    </div>

                    <!-- Step 1: Details -->
                    <div v-if="currentStep === 1" class="rounded-2xl bg-white p-8 shadow-sm">
                        <h2 class="mb-6 text-xl font-bold">Subscription Details</h2>

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
                                    {{ checkoutData.item.cost.toLocaleString() }} / {{
                                        checkoutData.item.billing_interval }}
                                </div>
                            </div>
                        </div>

                        <div class="space-y-6">
                            <div>
                                <label class="mb-2 block text-sm font-medium text-gray-700">Start Date</label>
                                <ServiceField :mini="true" @select-date="(d) => checkoutData.start_date = d" />
                                <p class="mt-1 text-sm text-primary font-medium">Selected: {{ checkoutData.start_date ||
                                    'None' }}</p>
                            </div>

                            <div>
                                <label class="mb-2 block text-sm font-medium text-gray-700">Notes (Optional)</label>
                                <textarea v-model="checkoutData.notes"
                                    class="w-full rounded-xl border border-gray-300 p-3 focus:border-primary focus:ring-1 focus:ring-primary"
                                    rows="3" placeholder="Add any special instructions..."></textarea>
                            </div>
                        </div>

                        <div class="mt-8 flex justify-end">
                            <button @click="nextStep"
                                class="rounded-xl bg-primary px-8 py-3 font-bold text-white transition hover:bg-opacity-90">
                                Next Step
                            </button>
                        </div>
                    </div>

                    <!-- Step 2: Confirmation -->
                    <div v-if="currentStep === 2" class="rounded-2xl bg-white p-8 shadow-sm">
                        <h2 class="mb-6 text-xl font-bold">Confirm Request</h2>

                        <div class="space-y-4 rounded-xl bg-gray-50 p-6 mb-6">
                            <div class="flex justify-between">
                                <span class="text-gray-600">Plan</span>
                                <span class="font-medium">{{ checkoutData.item.plan_name }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Billing Interval</span>
                                <span class="font-medium capitalize">{{ checkoutData.item.billing_interval }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Start Date</span>
                                <span class="font-medium">{{ checkoutData.start_date }}</span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-gray-600">Payment Type</span>
                                <span class="font-medium capitalize">{{ checkoutData.item.billing_timing }}</span>
                            </div>
                            <div class="border-t pt-4 flex justify-between items-center">
                                <span class="font-bold text-lg">Total Recurring</span>
                                <span class="font-bold text-xl text-primary">{{ checkoutData.item.cost.toLocaleString()
                                }}</span>
                            </div>
                        </div>

                        <div v-if="checkoutData.notes" class="mb-6">
                            <h3 class="text-sm font-medium text-gray-700 mb-2">Notes</h3>
                            <p class="text-gray-600 bg-gray-50 p-4 rounded-xl">{{ checkoutData.notes }}</p>
                        </div>

                        <div class="flex justify-between mt-8">
                            <button @click="prevStep" class="text-gray-500 font-medium hover:text-gray-800">
                                Back
                            </button>
                            <button @click="submitRequest" :disabled="submitting"
                                class="rounded-xl bg-primary px-8 py-3 font-bold text-white transition hover:bg-opacity-90 disabled:opacity-50 flex items-center gap-2">
                                <span v-if="submitting"
                                    class="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></span>
                                {{ submitting ? 'Submitting...' : 'Confirm Request' }}
                            </button>
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
