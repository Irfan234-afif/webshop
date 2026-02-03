import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/Home/Home.vue'
import AboutView from '../views/AboutView.vue'
import ProductsPage from '../views/Products/ProductsPage.vue'
import ProductDetailPage from '@/views/Products/ProductDetailPage.vue'
import CartPage from '../views/Cart/CartPage.vue'
import OrdersPage from '../views/Orders/OrdersPage.vue'
import CheckoutPaymentPage from '../views/Checkout/CheckoutPaymentPage.vue'
import LoginPage from '../views/Authentication/LoginPage.vue'
import RegistrationPage from '../views/Authentication/RegistrationPage.vue'
import CheckoutPage from '../views/Checkout/CheckoutPage.vue'
import WishlistPage from '../views/Wishlist/WishlistPage.vue'
import { useAuthStore } from '@/stores/auth'
import BillsPage from '@/views/Bills/BillsPage.vue'
import { KeepAlive } from 'vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: {
        keepAlive: true
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
        keepAlive: true
      }
    },
    {
      path: '/products/:id',
      name: 'product-detail',
      component: ProductDetailPage,
      meta: {
        title: 'Detail Produk',
        keepAlive: true
      }
    },
    {
      path: '/survey-request/:webItemCode',
      name: 'survey-request',
      component: () => import('../views/Products/SurveyRequestPage.vue'),
      meta: {
        title: 'Ajukan Survey',
        requiresAuth: true
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
      component: () => import('../views/Checkout/CheckoutPage.vue'),
      meta: {
        title: 'Checkout',
        requiresAuth: true
      }
    },
    {
      path: '/cart',
      name: 'cart',
      component: () => import('../views/Cart/CartPage.vue'),
      meta: {
        title: 'Keranjang Belanja',
        requiresAuth: true,
        keepAlive: true
      }
    },
    {
      path: '/wishlist',
      name: 'wishlist',
      component: () => import('../views/Wishlist/WishlistPage.vue'),
      meta: {
        title: 'Wishlist Saya',
        requiresAuth: true
      }
    },
    {
      path: '/orders',
      name: 'orders',
      component: () => import('../views/Orders/OrdersPage.vue'),
      meta: {
        title: 'Riwayat Pesanan',
        requiresAuth: true
      }
    },
    {
      path: '/orders/:id/review',
      name: 'order-review',
      component: () => import('../views/Orders/ReviewOrderPage.vue'),
      meta: {
        title: 'Beri Penilaian',
        requiresAuth: true
      }
    },
    {
      path: '/bills',
      name: 'bills',
      component: () => import('../views/Bills/BillsPage.vue'),
      meta: {
        title: 'Tagihan Berjalan',
        requiresAuth: true
      }
    },
    {
      path: '/order/:id/checkout',
      name: 'checkout-payment',
      component: () => import('../views/Checkout/CheckoutPaymentPage.vue'),
      meta: {
        title: 'Konfirmasi Pembayaran',
        requiresAuth: true
      }
    },
    {
      path: '/forgot-password',
      name: 'forgot-password',
      component: () => import('../views/Authentication/ForgotPasswordPage.vue'),
      meta: {
        title: 'Lupa Kata Sandi'
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
      component: () => import('../views/Authentication/RegistrationPage.vue'),
      meta: {
        title: 'Daftar Akun'
      }
    },
    {
      path: '/update-password',
      name: 'update-password',
      component: () => import('../views/Authentication/UpdatePasswordPage.vue'),
      meta: {
        title: 'Perbarui Kata Sandi'
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
    {
      path: '/order/:orderId/return',
      name: 'return-request',
      component: () => import('../views/Returns/ReturnRequestWizard.vue'),
      meta: {
        title: 'Ajukan Pengembalian',
        requiresAuth: true
      }
    },
    {
      path: '/returns',
      name: 'returns',
      component: () => import('../views/Returns/ReturnRequestsPage.vue'),
      meta: {
        title: 'Pengembalian Saya',
        requiresAuth: true
      }
    },
    {
      path: '/profile',
      component: () => import('../views/Profile/ProfileLayout.vue'),
      meta: {
        requiresAuth: true
      },
      children: [
        {
          path: '',
          name: 'profile-me',
          component: () => import('../views/Profile/ProfilePage.vue'),
          meta: {
            title: 'Profile Saya'
          }
        },
        {
          path: 'address',
          name: 'profile-address',
          component: () => import('../views/Profile/AddressPage.vue'),
          meta: { title: 'Alamat Rumah' }
        },
        {
            path: 'students',
            name: 'profile-students',
            component: () => import('../views/Profile/StudentPage.vue'),
            meta: { title: 'Data Siswa' }
        },
        {
            path: 'security',
            name: 'profile-security',
            component: () => import('../views/Profile/SecurityPage.vue'),
            meta: { title: 'Keamanan Akun' }
        }
      ]
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
