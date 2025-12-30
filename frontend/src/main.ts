import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import { FrappeUI } from 'frappe-ui'
import App from './App.vue'
import router from './router'
import './setupFrappeUIResources'
import { useAuthStore } from './stores/auth'

const app = createApp(App)

const pinia = createPinia()
app.use(FrappeUI)
app.use(pinia)
app.use(router)

app.mount('#app')

// Initialize auth store to check current user status
const authStore = useAuthStore()

if (authStore.isAuthenticated) {
	authStore.fetchCurrentUser()
} else {
	authStore.isLoading = false
}

declare global {
	interface Window {
		is_developer_mode?: boolean;
		builder_version: string;
	}
}

if (window.is_developer_mode && typeof window.is_developer_mode === "string") {
	window.is_developer_mode =
		window.is_developer_mode === "1" ||
		window.is_developer_mode === "True" ||
		(window.is_developer_mode as string).startsWith("{{");
}

if (window.builder_version && window.builder_version.startsWith("{{")) {
	window.builder_version = "develop";
}