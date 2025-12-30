# Figma Design System Integration Guide

This document provides comprehensive rules for integrating Figma designs into the Frappe Webshop frontend using the Model Context Protocol (MCP).

## Table of Contents

1. [Design Token Definitions](#1-design-token-definitions)
2. [Component Library Architecture](#2-component-library-architecture)
3. [Frameworks & Build System](#3-frameworks--build-system)
4. [Asset Management](#4-asset-management)
5. [Icon System](#5-icon-system)
6. [Styling Approach](#6-styling-approach)
7. [Project Structure](#7-project-structure)
8. [Figma-to-Code Workflow](#8-figma-to-code-workflow)

---

## 1. Design Token Definitions

### Color Tokens

All colors use CSS custom properties (CSS variables) defined in `src/assets/base.css` and mapped to Tailwind classes in `tailwind.config.js`.

#### Primary Color System

```css
/* src/assets/base.css */
:root {
  /* Primary & Secondary Colors */
  --color-primary: #AC208E;           /* Brand primary (purple-pink) */
  --color-secondary: #653870;          /* Brand secondary (dark purple) */
  --color-secondary-alt: #8DC73C;      /* Accent color (lime green) */
}
```

**Tailwind Usage:**
```vue
<!-- Primary button -->
<button class="bg-primary text-white">Click Me</button>

<!-- Secondary button -->
<button class="bg-secondary text-white">Learn More</button>

<!-- Accent/Alternative button -->
<button class="bg-secondary-alt text-white">Shop Now</button>
```

#### Background Colors

```css
:root {
  /* Background Colors */
  --color-background: var(--vt-c-white);        /* #ffffff */
  --color-background-soft: var(--vt-c-white-soft);  /* #f8f8f8 */
  --color-background-mute: var(--vt-c-white-mute);  /* #f2f2f2 */
}
```

**Tailwind Usage:**
```vue
<!-- Default background -->
<div class="bg-background">Content</div>

<!-- Soft background (cards, sections) -->
<div class="bg-background-soft">Card Content</div>

<!-- Muted background (disabled states, subtle sections) -->
<div class="bg-background-mute">Muted Content</div>
```

#### Text Colors

```css
:root {
  /* Text Colors */
  --color-text: #1E1E1E;                    /* Primary text */
  --color-text-secondary: #1E1E1E80;        /* Secondary text (50% opacity) */
  --color-text-description: #FFFFFFCC;      /* Description text (light, 80% opacity) */
  --color-heading: var(--vt-c-text-light-1); /* Headings (#2c3e50) */
}
```

**Tailwind Usage:**
```vue
<!-- Primary text -->
<p class="text-text">Main content text</p>

<!-- Secondary/muted text -->
<p class="text-text-secondary">Less important text</p>

<!-- Description text (for dark backgrounds) -->
<p class="text-text-desc">Description on dark background</p>

<!-- Headings -->
<h1 class="text-heading">Page Title</h1>
```

#### Border & Divider Colors

```css
:root {
  /* Border Colors */
  --color-border: #1E1E1E26;                    /* Default border (15% opacity) */
  --color-border-hover: var(--vt-c-divider-light-1); /* Hover state */
  --color-divider: #1E1E1E1A;                   /* Divider lines (10% opacity) */
}
```

**Tailwind Usage:**
```vue
<!-- Default border -->
<div class="border border-border">Bordered content</div>

<!-- Hover border -->
<div class="border border-border hover:border-border-hover">Interactive element</div>

<!-- Divider -->
<hr class="border-divider" />
```

#### Status Colors

```css
:root {
  /* Status Colors */
  --color-danger: #F92D46;  /* Error/danger state */
}
```

**Tailwind Usage:**
```vue
<!-- Danger button -->
<button class="bg-danger text-white">Delete</button>

<!-- Error text -->
<p class="text-danger">Error message</p>
```

### Typography Tokens

Typography is defined in `src/assets/base.css`:

```css
body {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 15px;           /* Base font size */
  line-height: 1.6;          /* Base line height */
  font-weight: normal;       /* Default weight (400) */
}
```

**Font Weight Guidelines:**
- `font-normal` (400): Body text
- `font-semibold` (600): Navigation, labels
- `font-bold` (700): Buttons, headings, emphasis

**Font Size Scale (Tailwind defaults + custom):**
```
text-xs:   12px   (small labels, badges)
text-sm:   14px   (secondary text, captions)
text-base: 16px   (body text) - Note: base.css sets 15px, but Tailwind uses 16px
text-lg:   18px   (subheadings)
text-xl:   20px   (headings)
text-2xl:  24px   (large headings)
text-3xl:  30px   (hero headings)
```

### Spacing Tokens

The project uses Tailwind's default spacing scale (based on 4px increments):

```
gap-2:  0.5rem  (8px)   - Tight spacing
gap-3:  0.75rem (12px)  - Default icon-text spacing
gap-4:  1rem    (16px)  - Standard component spacing
gap-6:  1.5rem  (24px)  - Medium spacing
gap-8:  2rem    (32px)  - Large spacing
```

**Custom Spacing:**
```css
:root {
  --section-gap: 160px;  /* Large section spacing */
}
```

### Responsive Breakpoints

Tailwind default breakpoints apply:

```javascript
// tailwind.config.js
screens: {
  sm: '640px',   // Tablets
  md: '768px',   // Small laptops
  lg: '1024px',  // Desktops
  xl: '1280px',  // Large desktops
  '2xl': '1536px', // Extra large screens
  standalone: { raw: "(display-mode: standalone)" }  // PWA mode
}
```

### Border Radius Scale

Common border radius values used in components:

```
rounded-lg:   8px  - Cards, inputs
rounded-xl:   12px - Buttons, containers
rounded-full: 50%  - Circular elements, badges, search bars
```

---

## 2. Component Library Architecture

### Component Organization

Components follow a **feature-based organization** with clear separation by purpose:

```
src/components/
├── common/          # Reusable UI primitives
│   ├── PrimaryButton.vue
│   └── ServiceCard.vue
├── layout/          # Layout components
│   ├── DefaultLayout.vue
│   └── Container.vue
├── navbar/          # Navigation-specific components
│   ├── Navbar.vue
│   ├── NavbarLogo.vue
│   ├── NavbarLinks.vue
│   └── NavbarActions.vue
└── icons/           # SVG icon components
    ├── Logo.vue
    ├── CartIcon.vue
    ├── WishlistIcon.vue
    ├── SearchIcon.vue
    └── [feature]Icon.vue
```

### Component Architecture Patterns

#### 1. **PrimaryButton Component** (`src/components/common/PrimaryButton.vue`)

**Design Pattern:** Variant-based button system with computed classes.

```vue
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'small' | 'medium' | 'large'
  icon?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'medium',
  disabled: false
})

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center gap-3 font-bold rounded-xl transition-all duration-300 cursor-pointer'

  const variants = {
    primary: 'bg-secondary-alt text-white hover:opacity-90',
    secondary: 'bg-primary text-white hover:opacity-90',
    outline: 'border-2 border-white text-white hover:bg-white hover:text-primary'
  }

  const sizes = {
    small: 'px-6 py-2 text-sm',
    medium: 'px-8 py-4 text-base',
    large: 'px-10 py-5 text-lg'
  }

  const disabled = props.disabled ? 'opacity-50 cursor-not-allowed' : ''

  return `${base} ${variants[props.variant]} ${sizes[props.size]} ${disabled}`
})
</script>

<template>
  <button :class="buttonClasses" :disabled="disabled">
    <slot />
  </button>
</template>
```

**Usage in Figma Integration:**
- **Primary variant:** Use `--color-secondary-alt` (#8DC73C) background
- **Secondary variant:** Use `--color-primary` (#AC208E) background
- **Outline variant:** White border with transparent background
- **Sizes:** Map Figma button sizes to small/medium/large variants
- **States:** Hover reduces opacity to 90%

#### 2. **Layout Container** (`src/components/layout/Container.vue`)

**Design Pattern:** Max-width container with responsive padding.

```vue
<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <slot />
  </div>
</template>
```

**Usage in Figma Integration:**
- Max content width: `1280px` (max-w-7xl)
- Horizontal padding: `16px` mobile → `24px` tablet → `32px` desktop
- Always center content with `mx-auto`

#### 3. **Navbar Component** (`src/components/navbar/Navbar.vue`)

**Design Pattern:** Responsive navigation with adaptive layout.

**Key Features:**
- Sticky positioning with blur backdrop
- Mobile-first responsive design
- Adaptive search (full input on desktop, icon on mobile)
- Badge notification system for cart
- Hamburger menu for mobile

**Responsive Behavior:**
```vue
<!-- Desktop (lg+): Full navigation + search bar -->
<nav class="hidden lg:flex items-center gap-4 ml-8">
  <a href="#" class="flex items-center h-12 px-3">Link</a>
</nav>

<!-- Tablet (sm-lg): Search bar visible, nav links hidden -->
<div class="hidden sm:flex bg-background-soft items-center h-10 lg:h-12">
  <input type="text" placeholder="Search..." />
</div>

<!-- Mobile (<sm): Icon buttons only -->
<button class="sm:hidden w-7 h-7">
  <SearchIcon />
</button>
```

**Usage in Figma Integration:**
- **Height:** `64px` mobile → `80px` tablet → `96px` desktop
- **Border:** 2px bottom border with `--color-border`
- **Spacing:** Use `gap-2` (8px) mobile → `gap-4` (16px) tablet → `gap-8` (32px) desktop
- **Cart Badge:** Circular badge with `bg-secondary-alt`, absolute positioned `-top-2 -right-2`

### Component Naming Conventions

**CRITICAL: Follow these naming rules when creating components from Figma:**

1. **Component Files:** PascalCase with descriptive names
   - ✅ `ProductCard.vue`, `UserProfile.vue`, `ShoppingCart.vue`
   - ❌ `product_card.vue`, `userprofile.vue`, `shopping-cart.vue`

2. **Props Interface:** Named `Props` within each component
   ```typescript
   interface Props {
     variant?: 'primary' | 'secondary'
     size?: 'small' | 'medium' | 'large'
   }
   ```

3. **Emits:** Use camelCase for event names
   ```typescript
   const emit = defineEmits<{
     openSearch: []
     openCart: []
     updateValue: [value: string]
   }>()
   ```

4. **Computed Classes:** Use descriptive names ending in `Classes`
   ```typescript
   const buttonClasses = computed(() => { ... })
   const containerClasses = computed(() => { ... })
   ```

### Component Composition Patterns

**MANDATORY: Use composition over monolithic components.**

**Example: Navbar decomposition**

```
Navbar.vue (orchestrator)
├── NavbarLogo.vue (logo + brand name)
├── NavbarLinks.vue (navigation links)
└── NavbarActions.vue (search, cart, profile)
```

**When to extract a sub-component:**
- Component exceeds 300 lines
- Logic is reusable elsewhere
- Distinct visual/functional unit
- Improves testability

---

## 3. Frameworks & Build System

### Technology Stack

```json
{
  "frameworks": {
    "frontend": "Vue 3.5.25",
    "routing": "Vue Router 4.6.3",
    "state": "Pinia 3.0.4",
    "language": "TypeScript 5.9.0"
  },
  "styling": {
    "framework": "TailwindCSS 3.4.3",
    "preset": "frappe-ui/tailwind",
    "processor": "PostCSS 8.5.6"
  },
  "build": {
    "bundler": "Vite 7.2.4",
    "compiler": "vue-tsc 3.1.5"
  }
}
```

### Vite Configuration

**File:** `vite.config.ts`

```typescript
export default defineConfig({
  plugins: [
    frappeui({
      frappeProxy: {
        port: 8000,
        source: "^/(app|desk|login|api|assets|files|pages|builder_assets)",
      },
      lucideIcons: true,  // Enable Lucide icon library
    }),
    vue(),
    vueDevTools(),
  ],
  build: {
    outDir: `../builder/public/frontend`,  // Output to Frappe app structure
    emptyOutDir: true,
    target: "es2015",
    sourcemap: true,
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))  // @ maps to src/
    },
  },
  optimizeDeps: {
    include: ["frappe-ui > feather-icons", "showdown", "engine.io-client"],
  },
})
```

**Key Configuration Notes:**

1. **Frappe UI Plugin:** Provides backend proxy and icon support
2. **Path Alias:** `@` always maps to `src/` directory
3. **Build Output:** Goes to `../builder/public/frontend` (Frappe app structure)
4. **Source Maps:** Enabled for production debugging
5. **Lucide Icons:** Available globally when `lucideIcons: true`

### TypeScript Configuration

**Project References Structure:**

```json
{
  "references": [
    { "path": "./tsconfig.app.json" },    // App code
    { "path": "./tsconfig.node.json" }    // Build tools
  ]
}
```

**Type-Check Command:**
```bash
npm run type-check  # Runs vue-tsc --build (required for Vue 3 + TypeScript)
```

### Build Commands

```bash
# Development
npm run dev          # Starts Vite dev server with HMR

# Production Build
npm run build        # Type-check + build
npm run build-only   # Build without type-checking (faster)

# Preview
npm run preview      # Preview production build locally
```

---

## 4. Asset Management

### Asset Directory Structure

```
src/assets/
├── main.css         # Main stylesheet (imports base.css)
├── base.css         # Design tokens, CSS reset, global styles
└── logo.svg         # Brand logo (SVG format)
```

### Asset Import Patterns

#### 1. **CSS/Stylesheets**

```typescript
// src/main.ts
import './assets/main.css'  // Global styles loaded at app entry
```

#### 2. **Static Assets (Images, SVGs)**

**Option A: Direct import (recommended for small assets)**
```vue
<script setup lang="ts">
import logo from '@/assets/logo.svg'
</script>

<template>
  <img :src="logo" alt="Logo" />
</template>
```

**Option B: Inline SVG components (recommended for icons)**
```vue
<!-- src/components/icons/Logo.vue -->
<template>
  <svg width="239" height="33" viewBox="0 0 239 33" fill="none">
    <path d="M0..." fill="#AC208E"/>
    <path d="M144..." fill="#8DC73C"/>
  </svg>
</template>
```

### Asset Optimization

**Vite automatically optimizes:**
- **Images:** Copied to `assets/` in build output
- **SVGs:** Can be imported as URLs or inlined as components
- **Fonts:** Should be loaded via CSS `@font-face` or CDN

**Large Assets:** Store in Frappe backend `public/` directory, reference via absolute paths:
```vue
<img src="/files/hero-image.jpg" alt="Hero" />
```

### Asset Naming Conventions

- **Images:** kebab-case with descriptive names
  - ✅ `hero-banner.jpg`, `product-thumbnail.png`
  - ❌ `image1.jpg`, `IMG_0001.png`

- **Icons (SVG components):** PascalCase with `Icon` suffix
  - ✅ `CartIcon.vue`, `SearchIcon.vue`, `WishlistIcon.vue`
  - ❌ `cart.vue`, `search-icon.vue`, `wishlist.svg`

- **Stylesheets:** kebab-case
  - ✅ `main.css`, `base.css`, `theme-overrides.css`
  - ❌ `Main.css`, `BASE.CSS`, `themeOverrides.css`

### CDN Configuration

**Not currently configured.** For CDN integration:

1. Add environment variables:
   ```env
   VITE_CDN_URL=https://cdn.example.com
   ```

2. Configure in `vite.config.ts`:
   ```typescript
   build: {
     assetsInlineLimit: 4096,  // Inline assets < 4kb
     rollupOptions: {
       output: {
         assetFileNames: 'assets/[name].[hash][extname]'
       }
     }
   }
   ```

---

## 5. Icon System

### Icon Architecture

Icons are implemented as **dedicated Vue components** (not imported symbols).

**Location:** `src/components/icons/`

**Pattern:** Inline SVG components with exposed size/color props.

### Icon Component Pattern

```vue
<!-- src/components/icons/CartIcon.vue -->
<script setup lang="ts">
interface Props {
  size?: string
  color?: string
}

withDefaults(defineProps<Props>(), {
  size: '24',
  color: 'currentColor'
})
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M9 2L7.17 4H4C2.9 4 2 4.9 2 6V19C2 20.1 2.9 21 4 21H20C21.1 21 22 20.1 22 19V6C22 4.9 21.1 4 20 4H16.83L15 2H9Z"
      :fill="color"
    />
  </svg>
</template>
```

### Icon Usage

```vue
<script setup lang="ts">
import CartIcon from '@/components/icons/CartIcon.vue'
import SearchIcon from '@/components/icons/SearchIcon.vue'
</script>

<template>
  <!-- Default size (24px) and color (currentColor) -->
  <CartIcon />

  <!-- Custom size -->
  <SearchIcon size="32" />

  <!-- Custom color -->
  <WishlistIcon color="#AC208E" />

  <!-- Use with Tailwind classes -->
  <div class="w-6 h-6 text-primary">
    <CartIcon />  <!-- Inherits color via currentColor -->
  </div>
</template>
```

### Icon Naming Convention

**Format:** `[Feature]Icon.vue` in PascalCase

**Examples:**
- `CartIcon.vue` - Shopping cart
- `WishlistIcon.vue` - Wishlist/favorites
- `SearchIcon.vue` - Search functionality
- `HumbergerIcon.vue` - Mobile menu (hamburger)
- `UniformIcon.vue` - Product category icon
- `BookIcon.vue` - Educational product icon
- `CateringIcon.vue` - Catering service icon
- `BusIcon.vue` - Transportation icon

### Lucide Icons (via Frappe UI)

The project has Lucide icons enabled via Vite config:

```typescript
// vite.config.ts
frappeui({
  lucideIcons: true
})
```

**Usage (when available):**
```vue
<script setup lang="ts">
import { ShoppingCart, Search, Heart } from 'lucide-vue-next'
</script>

<template>
  <ShoppingCart :size="24" />
  <Search :size="20" />
  <Heart :size="18" />
</template>
```

### Icon Design Guidelines for Figma Export

**When exporting icons from Figma:**

1. **Size:** Design at 24×24px base size (1x grid)
2. **Stroke:** Use 2px stroke width for consistency
3. **Color:** Use `currentColor` for fill/stroke (inherits text color)
4. **ViewBox:** Always `0 0 24 24` for base size icons
5. **Format:** Export as SVG, clean up with SVGO
6. **Naming:** Descriptive, feature-based names

**SVGO Configuration (if used):**
```json
{
  "plugins": [
    "removeDoctype",
    "removeXMLProcInst",
    "removeComments",
    "removeMetadata",
    "removeEditorsNSData",
    "cleanupAttrs",
    "mergeStyles",
    "inlineStyles"
  ]
}
```

---

## 6. Styling Approach

### Methodology: Utility-First with TailwindCSS

The project uses **utility-first CSS** via TailwindCSS with minimal custom styles.

### Styling Architecture

```
1. TailwindCSS Utilities (primary) → 90% of styling
2. Scoped Component Styles       → 5% (animations, complex selectors)
3. Global Styles (base.css)      → 5% (resets, CSS variables)
```

### Tailwind Configuration

**File:** `tailwind.config.js`

```javascript
import frappeUIPreset from "frappe-ui/tailwind"

export default {
  presets: [frappeUIPreset],  // Extends Frappe UI design system
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        secondary: {
          DEFAULT: "var(--color-secondary)",
          alt: "var(--color-secondary-alt)",
        },
        background: {
          DEFAULT: "var(--color-background)",
          soft: "var(--color-background-soft)",
          mute: "var(--color-background-mute)",
        },
        text: {
          DEFAULT: "var(--color-text)",
          secondary: "var(--color-text-secondary)",
          desc: "var(--color-text-description)",
          heading: "var(--color-heading)",
        },
        border: {
          DEFAULT: "var(--color-border)",
          hover: "var(--color-border-hover)",
        },
        divider: "var(--color-divider)",
        danger: "var(--color-danger)",
      },
      screens: {
        standalone: { raw: "(display-mode: standalone)" },  // PWA detection
      },
      padding: {
        "safe-top": "env(safe-area-inset-top)",
        "safe-right": "env(safe-area-inset-right)",
        "safe-bottom": "env(safe-area-inset-bottom)",
        "safe-left": "env(safe-area-inset-left)",
      },
    },
  },
  plugins: [],
}
```

### Global Styles

**File:** `src/assets/base.css`

Contains:
1. **Tailwind Directives:**
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```

2. **CSS Custom Properties:** All design tokens (colors, spacing)

3. **CSS Reset:** Box-sizing, margin reset, font smoothing
   ```css
   *,
   *::before,
   *::after {
     box-sizing: border-box;
     margin: 0;
     font-weight: normal;
   }
   ```

4. **Base Element Styles:**
   ```css
   body {
     min-height: 100vh;
     color: var(--color-text);
     background: var(--color-background);
     font-family: 'Instrument Sans', sans-serif;
     font-size: 15px;
     line-height: 1.6;
     -webkit-font-smoothing: antialiased;
     -moz-osx-font-smoothing: grayscale;
   }
   ```

### Scoped Component Styles

**Use scoped styles ONLY for:**
- Complex animations/transitions
- Pseudo-elements (::before, ::after)
- Deep selectors (:deep())
- Media queries too complex for Tailwind

**Example:**
```vue
<template>
  <button class="btn">Click Me</button>
</template>

<style scoped>
/* Only use scoped styles for custom animations */
.btn {
  @apply px-6 py-3 bg-primary text-white rounded-xl;  /* Prefer @apply */
}

.btn::before {
  content: '';
  /* Complex pseudo-element styling */
}
</style>
```

### Responsive Design Pattern

**Mobile-First Approach:**

```vue
<template>
  <!-- Base: Mobile styles (no prefix) -->
  <!-- sm: Tablet (640px+) -->
  <!-- md: Small desktop (768px+) -->
  <!-- lg: Desktop (1024px+) -->

  <div class="
    px-4 sm:px-6 lg:px-8
    text-sm sm:text-base lg:text-lg
    gap-2 sm:gap-4 lg:gap-8
  ">
    Content
  </div>
</template>
```

### Class Organization Best Practices

**Order classes by category:**

```vue
<div class="
  <!-- Layout -->
  flex flex-col items-center justify-between
  <!-- Spacing -->
  gap-4 px-6 py-8
  <!-- Sizing -->
  w-full max-w-7xl h-screen
  <!-- Colors -->
  bg-background text-text border border-border
  <!-- Typography -->
  text-base font-semibold uppercase
  <!-- Effects -->
  rounded-xl shadow-lg
  <!-- States -->
  hover:bg-background-soft transition-all duration-300
  <!-- Responsive -->
  sm:flex-row sm:px-8 lg:px-12
">
  Content
</div>
```

### Dark Mode (Currently Disabled)

Dark mode CSS is defined but commented out in `base.css`:

```css
/* @media (prefers-color-scheme: dark) {
  :root {
    --color-background: var(--vt-c-black);
    --color-text: var(--vt-c-text-dark-2);
  }
} */
```

**To enable:** Uncomment and test with Tailwind's `dark:` variant.

---

## 7. Project Structure

### Directory Overview

```
frontend/
├── public/                    # Static assets (served as-is)
├── src/
│   ├── assets/               # Stylesheets, images, fonts
│   │   ├── base.css          # Design tokens + CSS reset
│   │   ├── main.css          # Main entry stylesheet
│   │   └── logo.svg          # Brand assets
│   │
│   ├── components/           # Vue components (feature-based)
│   │   ├── common/           # Reusable UI primitives
│   │   │   ├── PrimaryButton.vue
│   │   │   └── ServiceCard.vue
│   │   ├── layout/           # Layout components
│   │   │   ├── DefaultLayout.vue
│   │   │   └── Container.vue
│   │   ├── navbar/           # Navigation components
│   │   │   ├── Navbar.vue
│   │   │   ├── NavbarLogo.vue
│   │   │   ├── NavbarLinks.vue
│   │   │   └── NavbarActions.vue
│   │   └── icons/            # Icon components
│   │       ├── Logo.vue
│   │       ├── CartIcon.vue
│   │       ├── WishlistIcon.vue
│   │       └── SearchIcon.vue
│   │
│   ├── composables/          # Vue composables (reusable logic)
│   │   └── (empty - add as needed)
│   │
│   ├── stores/               # Pinia stores (state management)
│   │   └── counter.ts        # Example store
│   │
│   ├── router/               # Vue Router configuration
│   │   └── index.ts          # Route definitions
│   │
│   ├── types/                # TypeScript type definitions
│   │   └── navigation.ts     # Navigation types
│   │
│   ├── utils/                # Utility functions
│   │   └── (empty - add as needed)
│   │
│   ├── views/                # Page-level view components
│   │   ├── Home/
│   │   │   ├── Home.vue
│   │   │   └── components/
│   │   │       ├── HeroSection.vue
│   │   │       └── ProductServicesSection.vue
│   │   └── AboutView.vue
│   │
│   ├── App.vue               # Root component
│   ├── main.ts               # Application entry point
│   └── setupFrappeUIResources.ts  # Frappe integration setup
│
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
├── package.json              # Dependencies
└── CLAUDE.md                 # Development guidelines
```

### File Naming Conventions

| Type | Convention | Examples |
|------|------------|----------|
| **Components** | PascalCase.vue | `ProductCard.vue`, `UserProfile.vue` |
| **Views** | PascalCase.vue | `HomeView.vue`, `AboutView.vue` |
| **Composables** | camelCase.ts | `useAuth.ts`, `useCart.ts` |
| **Stores** | camelCase.ts | `auth.ts`, `cart.ts`, `products.ts` |
| **Types** | camelCase.ts | `navigation.ts`, `api.ts`, `models.ts` |
| **Utils** | camelCase.ts | `formatters.ts`, `validators.ts` |
| **Stylesheets** | kebab-case.css | `main.css`, `base.css` |
| **Assets** | kebab-case | `hero-image.jpg`, `logo.svg` |

### Import Path Aliases

**Configured Alias:** `@` → `src/`

```typescript
// vite.config.ts
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

**Usage:**
```typescript
// ✅ Good: Use @ alias
import { useCartStore } from '@/stores/cart'
import ProductCard from '@/components/common/ProductCard.vue'

// ❌ Bad: Relative paths from deep nesting
import { useCartStore } from '../../../stores/cart'
import ProductCard from '../../components/common/ProductCard.vue'
```

### Feature-Based Organization

**For large features, group related files:**

```
src/views/Products/
├── Products.vue               # Main view
├── components/
│   ├── ProductCard.vue
│   ├── ProductFilter.vue
│   └── ProductGrid.vue
├── composables/
│   └── useProductFilter.ts
└── types/
    └── product.ts
```

### Component vs View

- **Views** (`src/views/`): Page-level components mapped to routes
  - Orchestrate multiple components
  - Handle route params/query
  - Load data for entire page

- **Components** (`src/components/`): Reusable UI elements
  - Receive data via props
  - Emit events for actions
  - Can be used in multiple views

---

## 8. Figma-to-Code Workflow

### Step-by-Step Integration Process

#### Phase 1: Design Token Extraction

1. **Extract Colors from Figma:**
   - Open Figma file → Inspect → Styles → Colors
   - Map to CSS variables in `src/assets/base.css`
   - Add Tailwind mappings in `tailwind.config.js`

   ```css
   /* Example: Adding a new brand color */
   :root {
     --color-accent: #FF6B35;  /* From Figma color style */
   }
   ```

   ```javascript
   // tailwind.config.js
   colors: {
     accent: "var(--color-accent)",
   }
   ```

2. **Extract Typography:**
   - Note font families, weights, sizes from Figma text styles
   - Update `base.css` if new fonts needed
   - Map to Tailwind classes or create custom utilities

3. **Extract Spacing:**
   - Identify consistent spacing values (padding, margins, gaps)
   - Use existing Tailwind scale (4px increments) when possible
   - Add custom spacing only if absolutely necessary

#### Phase 2: Component Analysis

1. **Identify Component Hierarchy:**
   - Break Figma design into logical components
   - Determine parent-child relationships
   - Plan component folder structure

2. **Determine Component Type:**
   - **Common component:** Used across multiple features
   - **Feature component:** Specific to one feature/domain
   - **Layout component:** Structural (headers, containers, grids)
   - **Icon component:** SVG illustrations

3. **Plan Props & State:**
   - What data comes from parent? → Props
   - What data is global? → Pinia store
   - What data is local? → Component state

#### Phase 3: Component Implementation

1. **Create Component File:**
   ```bash
   # Example: Creating a ProductCard component
   touch src/components/common/ProductCard.vue
   ```

2. **Define TypeScript Interface:**
   ```vue
   <script setup lang="ts">
   interface Props {
     title: string
     price: number
     imageUrl: string
     variant?: 'default' | 'compact'
   }

   const props = withDefaults(defineProps<Props>(), {
     variant: 'default'
   })
   </script>
   ```

3. **Implement Template with Tailwind:**
   ```vue
   <template>
     <div class="bg-white rounded-xl shadow-lg overflow-hidden">
       <img :src="imageUrl" :alt="title" class="w-full h-48 object-cover" />
       <div class="p-6">
         <h3 class="text-lg font-bold text-heading">{{ title }}</h3>
         <p class="text-2xl font-bold text-primary mt-2">
           {{ formatPrice(price) }}
         </p>
       </div>
     </div>
   </template>
   ```

4. **Add Scoped Styles (if needed):**
   ```vue
   <style scoped>
   /* Only for complex animations or pseudo-elements */
   .product-card:hover::after {
     content: '';
     /* Custom hover effect */
   }
   </style>
   ```

#### Phase 4: Responsive Implementation

1. **Mobile-First Design:**
   ```vue
   <template>
     <div class="
       grid
       grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
       gap-4 sm:gap-6 lg:gap-8
     ">
       <ProductCard v-for="product in products" :key="product.id" />
     </div>
   </template>
   ```

2. **Test Breakpoints:**
   - Mobile: < 640px
   - Tablet: 640px - 1024px
   - Desktop: > 1024px

#### Phase 5: State Integration

1. **Create Pinia Store (if needed):**
   ```typescript
   // src/stores/products.ts
   import { defineStore } from 'pinia'
   import { ref } from 'vue'

   export const useProductsStore = defineStore('products', () => {
     const products = ref([])
     const isLoading = ref(false)

     const fetchProducts = async () => {
       isLoading.value = true
       try {
         // API call
       } finally {
         isLoading.value = false
       }
     }

     return { products, isLoading, fetchProducts }
   })
   ```

2. **Connect Component to Store:**
   ```vue
   <script setup lang="ts">
   import { useProductsStore } from '@/stores/products'

   const productsStore = useProductsStore()
   </script>

   <template>
     <ProductGrid :products="productsStore.products" />
   </template>
   ```

#### Phase 6: Icon Integration

1. **Export SVG from Figma:**
   - Right-click icon → Copy/Paste as → Copy as SVG
   - Clean up SVG code (remove unnecessary attributes)

2. **Create Icon Component:**
   ```vue
   <!-- src/components/icons/NewFeatureIcon.vue -->
   <script setup lang="ts">
   interface Props {
     size?: string
     color?: string
   }

   withDefaults(defineProps<Props>(), {
     size: '24',
     color: 'currentColor'
   })
   </script>

   <template>
     <svg
       :width="size"
       :height="size"
       viewBox="0 0 24 24"
       fill="none"
       xmlns="http://www.w3.org/2000/svg"
     >
       <!-- Paste cleaned SVG path here -->
       <path d="..." :fill="color" />
     </svg>
   </template>
   ```

### Figma Export Settings

**Recommended export settings:**

- **Images:** 2x PNG or WebP for raster graphics
- **Icons:** SVG with "Outline Stroke" enabled
- **Spacing:** 4px grid alignment
- **Colors:** Use Figma color styles (map to CSS variables)

### Code Quality Checklist

Before committing Figma-to-code implementations:

- [ ] TypeScript types defined for all props
- [ ] Component under 300 lines (extract if larger)
- [ ] Responsive breakpoints tested (mobile/tablet/desktop)
- [ ] Colors use CSS variables (no hardcoded hex values)
- [ ] Spacing uses Tailwind scale (no arbitrary values)
- [ ] Icons exported as components (not inline SVG)
- [ ] Accessibility: alt text, ARIA labels, keyboard navigation
- [ ] Type-check passes: `npm run type-check`

### Common Pitfalls to Avoid

1. **Hardcoding Colors:**
   ```vue
   <!-- ❌ Bad -->
   <div class="bg-primary">Content</div>

   <!-- ✅ Good -->
   <div class="bg-primary">Content</div>
   ```

2. **Ignoring Responsive Design:**
   ```vue
   <!-- ❌ Bad: Fixed desktop size -->
   <div class="w-[1280px] px-8">Content</div>

   <!-- ✅ Good: Responsive container -->
   <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">Content</div>
   ```

3. **Over-Nesting Components:**
   ```vue
   <!-- ❌ Bad: Unnecessary wrapper components -->
   <OuterWrapper>
     <MiddleWrapper>
       <InnerWrapper>
         <Content />
       </InnerWrapper>
     </MiddleWrapper>
   </OuterWrapper>

   <!-- ✅ Good: Flat structure -->
   <div class="wrapper">
     <Content />
   </div>
   ```

4. **Inline Styles:**
   ```vue
   <!-- ❌ Bad -->
   <div style="background-color: #AC208E; padding: 16px;">Content</div>

   <!-- ✅ Good -->
   <div class="bg-primary p-4">Content</div>
   ```

5. **Not Using TypeScript:**
   ```vue
   <!-- ❌ Bad -->
   <script setup>
   const props = defineProps(['title', 'price'])
   </script>

   <!-- ✅ Good -->
   <script setup lang="ts">
   interface Props {
     title: string
     price: number
   }
   const props = defineProps<Props>()
   </script>
   ```

---

## Quick Reference: MCP Integration Commands

### Extracting Design Context from Figma

```bash
# Using Figma MCP tools (when available)
# Get design context for a specific Figma node
mcp__figma__get_design_context(
  nodeId: "123:456",
  fileKey: "abc123def456"
)

# Get screenshot of Figma design
mcp__figma__get_screenshot(
  nodeId: "123:456",
  fileKey: "abc123def456"
)

# Get metadata structure
mcp__figma__get_metadata(
  nodeId: "123:456",
  fileKey: "abc123def456"
)
```

### Color Extraction Template

```typescript
// From Figma color inspection:
// Primary: #AC208E
// Secondary: #653870
// Accent: #8DC73C

// Add to src/assets/base.css:
:root {
  --color-primary: #AC208E;
  --color-secondary: #653870;
  --color-accent: #8DC73C;
}

// Add to tailwind.config.js:
colors: {
  primary: "var(--color-primary)",
  secondary: "var(--color-secondary)",
  accent: "var(--color-accent)",
}
```

### Component Scaffold Template

```vue
<!-- src/components/[category]/[ComponentName].vue -->
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  // Define props from Figma component properties
  variant?: 'default' | 'alternate'
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'medium'
})

// Computed styles based on props
const componentClasses = computed(() => {
  const base = 'base-classes-here'
  const variants = {
    default: 'default-styles',
    alternate: 'alternate-styles'
  }
  const sizes = {
    small: 'small-size-classes',
    medium: 'medium-size-classes',
    large: 'large-size-classes'
  }

  return `${base} ${variants[props.variant]} ${sizes[props.size]}`
})
</script>

<template>
  <div :class="componentClasses">
    <slot />
  </div>
</template>

<style scoped>
/* Only add scoped styles if absolutely necessary */
</style>
```

---

## Appendix: Design System Checklist

### Pre-Implementation Checklist

Before coding from Figma designs:

- [ ] Design tokens extracted (colors, typography, spacing)
- [ ] Component hierarchy planned
- [ ] Responsive breakpoints identified
- [ ] State management strategy defined
- [ ] Asset export completed (images, icons, SVGs)
- [ ] TypeScript interfaces drafted

### Implementation Checklist

- [ ] Component created in correct folder
- [ ] Props interface defined with TypeScript
- [ ] Tailwind utilities used (no hardcoded values)
- [ ] Responsive classes applied (mobile-first)
- [ ] Accessibility attributes added (aria-*, alt text)
- [ ] Type-check passes (`npm run type-check`)

### Post-Implementation Checklist

- [ ] Component tested on mobile/tablet/desktop
- [ ] Dark mode compatibility verified (if enabled)
- [ ] Performance optimized (lazy loading, code splitting)
- [ ] Documentation added (JSDoc comments)
- [ ] Design system consistency verified

---

## Support & Resources

- **Project Documentation:** `/CLAUDE.md`
- **Frappe UI Documentation:** [https://frappeui.com](https://frappeui.com)
- **TailwindCSS Documentation:** [https://tailwindcss.com](https://tailwindcss.com)
- **Vue 3 Documentation:** [https://vuejs.org](https://vuejs.org)
- **TypeScript Documentation:** [https://www.typescriptlang.org](https://www.typescriptlang.org)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-18
**Maintained By:** Development Team
