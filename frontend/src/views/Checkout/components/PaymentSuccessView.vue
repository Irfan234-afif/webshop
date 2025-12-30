<template>
    <div class="payment-success-view">
        <div class="text-center py-12">
            <div class="mb-6 flex justify-center">
                <div class="h-24 w-24 bg-green-100 rounded-full flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-green-600" fill="none"
                        viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                </div>
            </div>

            <h2 class="text-2xl font-bold text-gray-900 mb-2">Pembayaran Berhasil!</h2>
            <p class="text-gray-600 mb-8">Terima kasih, pembayaran Anda telah kami terima.</p>

            <div class="bg-gray-50 rounded-lg p-6 max-w-md mx-auto mb-8 text-left">
                <div class="flex justify-between mb-2">
                    <span class="text-gray-600">No. Order</span>
                    <span class="font-medium text-gray-900">{{ paymentDetails.sales_order.name }}</span>
                </div>
                <div class="flex justify-between mb-2">
                    <span class="text-gray-600">Total Pembayaran</span>
                    <span class="font-medium text-gray-900">{{ formatIDR(paymentDetails.sales_order.grand_total)
                        }}</span>
                </div>
                <div class="flex justify-between">
                    <span class="text-gray-600">Metode Pembayaran</span>
                    <span class="font-medium text-gray-900">{{ paymentDetails.payment_method.title }}</span>
                </div>
            </div>

            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <button @click="$emit('view-order')"
                    class="px-6 py-2 bg-[#ac208e] text-white rounded-lg hover:bg-[#8c1a72] transition-colors">
                    Lihat Pesanan
                </button>
                <button @click="$emit('continue-shopping')"
                    class="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                    Lanjut Belanja
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import type { CheckoutPaymentDetails } from '@/types/checkout'

const props = defineProps<{
    paymentDetails: CheckoutPaymentDetails
}>()

defineEmits<{
    (e: 'view-order'): void
    (e: 'continue-shopping'): void
}>()

function formatIDR(amount: number): string {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount)
}
</script>
