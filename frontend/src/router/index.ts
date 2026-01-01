import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Home/Home.vue'
import AboutView from '../views/AboutView.vue'
import ProductsPage from '../views/Products/ProductsPage.vue'
import ProductDetailPage from '@/views/Products/ProductDetailPage.vue'
import CartPage from '../views/Cart/CartPage.vue'
import OrdersPage from '../views/Orders/OrdersPage.vue'
import OrderDetailPage from '../views/Orders/OrderDetailPage.vue'
import CheckoutPaymentPage from '../views/Checkout/CheckoutPaymentPage.vue'
import LoginPage from '../views/Authentication/LoginPage.vue'
import RegistrationPage from '../views/Authentication/RegistrationPage.vue'
import CheckoutPage from '../views/Checkout/CheckoutPage.vue'
import WishlistPage from '../views/Wishlist/WishlistPage.vue'
import { useAuthStore } from '@/stores/auth'
import BillsPage from '@/views/Bills/BillsPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        keepAlive: true // Preserve component state during navigation
      }
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: AboutView,
    },
    {
      path: '/products',
      name: 'products',
      component: ProductsPage,
      meta: {
        title: 'Produk & Layanan',
        keepAlive: true // Preserve component state during navigation
      }
    },
    {
      path: '/products/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: {
        title: 'Detail Produk',
        keepAlive: true // Preserve component state during navigation
      }
    },
    {
      path: '/subscription-checkout/:itemCode',
      name: 'subscription-checkout',
      component: () => import('../views/Products/SubscriptionCheckoutPage.vue'),
      meta: {
        title: 'Subscription Checkout',
        requiresAuth: true
      }
    },
    {
      path: '/checkout',
      name: 'checkout',
      component: CheckoutPage,
      meta: {
        title: 'Checkout',
        requiresAuth: true
      }
    },
    {
      path: '/cart',
      name: 'cart',
      component: CartPage,
      meta: {
        title: 'Keranjang Belanja',
        requiresAuth: true
      }
    },
    {
      path: '/wishlist',
      name: 'wishlist',
      component: WishlistPage,
      meta: {
        title: 'Wishlist Saya',
        requiresAuth: true
      }
    },
    {
      path: '/orders',
      name: 'orders',
      component: OrdersPage,
      meta: {
        title: 'Riwayat Pesanan',
        requiresAuth: true
      }
    },
    {
      path: '/bills',
      name: 'bills',
      component: BillsPage,
      meta: {
        title: 'Tagihan Berjalan',
        requiresAuth: true
      }
    },
    {
      path: '/order/:id',
      name: 'order-detail',
      component: OrderDetailPage,
      meta: {
        title: 'Detail Pesanan',
        requiresAuth: true
      }
    },
    {
      path: '/order/:id/checkout',
      name: 'checkout-payment',
      component: CheckoutPaymentPage,
      meta: {
        title: 'Konfirmasi Pembayaran',
        requiresAuth: true
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage,
      meta: {
        title: 'Masuk ke Akun'
      }
    },
    {
      path: '/register',
      name: 'register',
      component: RegistrationPage,
      meta: {
        title: 'Daftar Akun'
      }
    },
    {
      path: '/bills/:id/payment',
      name: 'bill-payment',
      component: () => import('../views/Bills/BillPaymentPage.vue'),
      meta: {
        title: 'Pembayaran Tagihan',
        requiresAuth: true
      }
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    // Selalu scroll ke atas saat pindah halaman
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0, behavior: 'smooth' };
    }
  }
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Update document title
  if (to.meta.title) {
    document.title = `${to.meta.title}`
  }
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
})

export default router
