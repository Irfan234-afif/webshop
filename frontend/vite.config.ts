import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import frappeui from "frappe-ui/vite";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
	define: {
		__VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false,
	},
	plugins: [
		frappeui({
			frappeProxy: {
				port: 8000,
				source: "^/(app|desk|api|files|private|pages|builder_assets|midtrans_checkout)",
			},
			lucideIcons: true,
		}),
		vue(),
		vueDevTools(),
	],
	resolve: {
		alias: {
			'@': fileURLToPath(new URL('./src', import.meta.url))
		},
	},
	server: {
		allowedHosts: true,
		watch: {
			usePolling: true,
			// Optional: adjust the polling interval if needed (default is fine)
			interval: 100
		}
	},
	optimizeDeps: {
		include: ["frappe-ui > feather-icons", "engine.io-client", "interactjs", "debug"],
	}
})
