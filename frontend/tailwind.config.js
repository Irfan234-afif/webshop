import frappeUIPreset from "frappe-ui/tailwind"
export default {
	presets: [frappeUIPreset],
	content: [
		"./index.html",
		"./src/**/*.{vue,js,ts,jsx,tsx}",
		"./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
		"../node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
	],
	theme: {
		extend: {
			screens: {
				standalone: {
					raw: "(display-mode: standalone)",
				},
			},
			padding: {
				"safe-top": "env(safe-area-inset-top)",
				"safe-right": "env(safe-area-inset-right)",
				"safe-bottom": "env(safe-area-inset-bottom)",
				"safe-left": "env(safe-area-inset-left)",
			},
			colors: {
				// Primary & Secondary Colors
				primary: "var(--color-primary)",
				secondary: {
					DEFAULT: "var(--color-secondary)",
					alt: "var(--color-secondary-alt)",
				},

				// Background Colors
				background: {
					DEFAULT: "var(--color-background)",
					soft: "var(--color-background-soft)",
					mute: "var(--color-background-mute)",
				},

				// Shorthand aliases
				mute: "var(--color-background-mute)",

				// Text Colors
				text: {
					DEFAULT: "var(--color-text)",
					secondary: "var(--color-text-secondary)",
					desc: "var(--color-text-description)",
					heading: "var(--color-heading)",
				},

				// Border Colors
				border: {
					DEFAULT: "var(--color-border)",
					hover: "var(--color-border-hover)",
				},
				divider: "var(--color-divider)",

				// Status Colors
				danger: "var(--color-danger)",

				// VT Theme Colors (optional)
				vt: {
					white: {
						DEFAULT: "var(--vt-c-white)",
						soft: "var(--vt-c-white-soft)",
						mute: "var(--vt-c-white-mute)",
					},
					black: {
						DEFAULT: "var(--vt-c-black)",
						soft: "var(--vt-c-black-soft)",
						mute: "var(--vt-c-black-mute)",
					},
					indigo: "var(--vt-c-indigo)",
				},
			},
		},
	},
	plugins: [],
}