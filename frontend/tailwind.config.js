import frappeUIPreset from "frappe-ui/tailwind"
import typography from "@tailwindcss/typography"

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
			fontFamily: {
				sans: ['Inter', 'sans-serif'],
			},
			screens: {
				standalone: {
					raw: "(display-mode: standalone)",
				},
			},
			fontSize: {
				"4xl": ["2.25rem", { lineHeight: "2.5rem" }],
				"5xl": ["3rem", { lineHeight: "1" }],
				"6xl": ["3.75rem", { lineHeight: "1" }],
				"7xl": ["4.5rem", { lineHeight: "1" }],
				"8xl": ["6rem", { lineHeight: "1" }],
				"9xl": ["8rem", { lineHeight: "1" }],
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
					surface: "#8d1a721a",
				},
				success: "var(--color-success)",

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
	plugins: [typography],
}