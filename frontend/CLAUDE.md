# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **frontend** application for **Frappe Webshop**, an open source e-commerce platform built on the Frappe Framework. The frontend is a **Vue 3 + TypeScript + Vite** application that integrates with the Frappe backend (ERPNext) to provide the user-facing e-commerce interface.

The parent webshop application is a Frappe app that includes both backend (Python) and frontend (Vue) components. This frontend directory builds the UI that gets deployed to the Frappe backend.

## Technology Stack

- **Vue 3** with Composition API (`<script setup>`)
- **TypeScript** for type safety
- **Vite** for fast development and optimized builds
- **Vue Router** for client-side routing
- **Pinia** for state management
- **Frappe UI** - Custom component library and utilities for Frappe integration
- **TailwindCSS** with Frappe UI preset for styling
- **Node.js** 20.19.0+ or 22.12.0+

## Code Quality Standards

**CRITICAL: All code must meet these standards before implementation or modification.**

### Core Principles

1. **Clean Architecture**: Maintain clear separation between UI components, business logic (stores), and utilities
2. **State Management First**: Use Pinia stores for all shared state. Never prop-drill data through multiple components
3. **Type Safety**: TypeScript is mandatory. No `any` types without explicit justification
4. **Single Responsibility**: Each file/function/component does one thing well
5. **DRY Code**: Extract repeated logic into composables, utilities, or shared components

### Folder Structure Requirements

- **Feature-based organization**: Group related files by feature, not by technical type
- **Clear boundaries**: Components, stores, composables, utils, types must be in separate directories
- **No deep nesting**: Maximum 3 levels of folder depth
- **Consistent naming**: Follow Vue/TypeScript conventions strictly (see naming section below)

### State Management Requirements

- **Pinia for global state**: User session, shopping cart, product catalog, orders
- **Composables for reusable logic**: Form validation, API patterns, DOM utilities
- **Component state for UI only**: Loading states, modal visibility, form inputs
- **No prop drilling**: If data passes through more than 2 components, use a store

### Code Review Checklist

Every code change must pass:
- [ ] TypeScript compiles without errors (`npm run type-check`)
- [ ] No hardcoded values (use constants/environment variables)
- [ ] Proper error handling on all async operations
- [ ] Components under 300 lines
- [ ] No code duplication
- [ ] Descriptive variable/function names
- [ ] Imports organized by category (Vue → external → internal → types → assets)

## Docker Terminal Access

**CRITICAL: This frontend runs inside a Frappe Docker development container. All terminal commands must be executed inside the Docker container.**

### Accessing the Container for Frontend Work

```bash
# Access container with working directory set to frontend
docker exec -it -w /workspace/development/frappe-bench/apps/webshop/frontend \
  frappe_docker_devcontainer-frappe-1 \
  /bin/bash

# Once inside the container, run frontend commands normally:
npm install
npm run dev
npm run type-check
```

### Quick Command Execution

For one-off commands without entering the container:

```bash
# Type-check from host
docker exec -it -w /workspace/development/frappe-bench/apps/webshop/frontend \
  frappe_docker_devcontainer-frappe-1 \
  npm run type-check

# Build from host
docker exec -it -w /workspace/development/frappe-bench/apps/webshop/frontend \
  frappe_docker_devcontainer-frappe-1 \
  npm run build
```

### VSCode Terminal

If using VSCode with the configured terminal profile, you can access the Docker terminal directly from the IDE. The terminal will automatically connect to the container.

## Key Development Commands

**Note: Run these commands inside the Docker container (see Docker Terminal Access section above).**

```bash
# Install dependencies
npm install

# Start development server with hot-reload
npm run dev

# Type-check TypeScript
npm run type-check

# Build for production (type-check + build)
npm run build

# Build only (without type-checking)
npm run build-only

# Preview production build
npm run preview
```

## Architecture & Integration

### Frappe Backend Integration

The frontend integrates with a Frappe backend through:

1. **Frappe UI Library** (`frappe-ui`): Provides pre-built components and resource fetching utilities designed for Frappe backends
2. **Resource Fetcher Setup** ([src/setupFrappeUIResources.ts:1-3](src/setupFrappeUIResources.ts#L1-L3)): Configures the Frappe UI resource fetcher before the app loads
3. **Vite Proxy** ([vite.config.ts:16-19](vite.config.ts#L16-L19)): Proxies requests to backend at port 8000 for paths like `/app`, `/api`, `/assets`, etc.

### Build Output

The production build outputs to `../builder/public/frontend` ([vite.config.ts:28](vite.config.ts#L28)), which places the built frontend assets into the parent Frappe app structure where they can be served by the Frappe backend.

### Developer Mode Detection

The app includes special handling for Frappe's developer mode ([src/main.ts:17-33](src/main.ts#L17-L33)):
- Normalizes `window.is_developer_mode` from string to boolean
- Handles template placeholders in development builds
- Sets `window.builder_version` to "develop" when using template placeholders

## Project Structure

### Folder Organization Principles

**CRITICAL: Maintain clean, organized folder structure at all times.**

```
src/
├── assets/          # Static assets (CSS, images, fonts)
├── components/      # Reusable Vue components
│   ├── common/      # Generic reusable components (buttons, inputs, cards)
│   ├── layout/      # Layout components (headers, footers, sidebars)
│   ├── features/    # Feature-specific components (product cards, cart items)
│   └── icons/       # Icon components
├── composables/     # Vue composables for shared logic (useAuth, useCart)
├── router/          # Vue Router configuration
│   ├── index.ts     # Main router setup
│   └── routes.ts    # Route definitions
├── stores/          # Pinia stores (state management)
│   ├── auth.ts      # Authentication store
│   ├── cart.ts      # Shopping cart store
│   └── products.ts  # Product catalog store
├── types/           # TypeScript type definitions
│   ├── models.ts    # Data models (Product, Order, User)
│   └── api.ts       # API response types
├── utils/           # Utility functions
│   ├── formatters.ts  # Data formatting utilities
│   ├── validators.ts  # Validation functions
│   └── constants.ts   # Application constants
├── views/           # Page-level view components
│   ├── Home.vue
│   ├── Products/    # Product-related views
│   ├── Cart/        # Cart-related views
│   └── Checkout/    # Checkout flow views
├── App.vue          # Root application component
├── main.ts          # Application entry point
└── setupFrappeUIResources.ts  # Frappe integration setup
```

### Component Organization Guidelines

**Follow these strict rules for component organization:**

1. **Single Responsibility**: Each component should do one thing well
2. **Feature-Based Grouping**: Group related components by feature, not type
3. **Naming Convention**:
   - Components: PascalCase (`ProductCard.vue`, `UserProfile.vue`)
   - Composables: camelCase with 'use' prefix (`useAuth.ts`, `useCart.ts`)
   - Stores: camelCase (`auth.ts`, `cart.ts`)
   - Utils: camelCase (`formatters.ts`, `validators.ts`)

4. **Component Size**: Keep components under 300 lines. Extract logic to composables if larger
5. **Props vs State**: Use props for parent-child data flow, stores for global state
6. **No Business Logic in Views**: Views orchestrate components, business logic goes in stores/composables

## State Management with Pinia

**MANDATORY: Use Pinia for all global state management. Never use component-level state for shared data.**

### Store Organization Patterns

Each Pinia store should follow this structure:

```typescript
// stores/cart.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, Product } from '@/types/models'

export const useCartStore = defineStore('cart', () => {
  // State (use ref for reactive state)
  const items = ref<CartItem[]>([])
  const isLoading = ref(false)

  // Getters (use computed for derived state)
  const itemCount = computed(() => items.value.length)
  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  // Actions (methods that mutate state)
  const addItem = async (product: Product, quantity: number) => {
    isLoading.value = true
    try {
      // API call or business logic
      items.value.push({ ...product, quantity })
    } catch (error) {
      console.error('Failed to add item:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const removeItem = (itemId: string) => {
    items.value = items.value.filter(item => item.id !== itemId)
  }

  const clearCart = () => {
    items.value = []
  }

  return {
    // State
    items,
    isLoading,
    // Getters
    itemCount,
    totalPrice,
    // Actions
    addItem,
    removeItem,
    clearCart,
  }
})
```

### Store Best Practices

1. **Setup Stores Syntax**: Always use Composition API syntax (`defineStore(() => { ... })`) for consistency
2. **Type Everything**: Use TypeScript types for all state, parameters, and return values
3. **No Direct Mutations**: Only mutate state through actions, never from components
4. **Computed for Derived State**: Use `computed()` for values derived from state
5. **Async Actions**: Handle all API calls within store actions
6. **Error Handling**: Always catch and handle errors in actions
7. **Store Granularity**: Create separate stores for distinct domains (auth, cart, products, orders)
8. **No Cross-Store Mutations**: Stores should not directly mutate other stores' state

### When to Use Stores vs Composables

- **Stores (Pinia)**: Global state that persists across components (user session, cart, product catalog)
- **Composables**: Reusable logic without persistent state (form validation, API fetching patterns, DOM manipulation)

Example composable:

```typescript
// composables/useApi.ts
import { ref } from 'vue'
import type { Ref } from 'vue'

export function useApi<T>(apiFunc: () => Promise<T>) {
  const data: Ref<T | null> = ref(null)
  const error: Ref<Error | null> = ref(null)
  const isLoading = ref(false)

  const execute = async () => {
    isLoading.value = true
    error.value = null
    try {
      data.value = await apiFunc()
    } catch (e) {
      error.value = e as Error
    } finally {
      isLoading.value = false
    }
  }

  return { data, error, isLoading, execute }
}
```

## Clean Code Practices

**MANDATORY: Follow these clean code principles for all new code and refactoring.**

### General Principles

1. **Self-Documenting Code**: Write code that explains itself. Use descriptive names over comments
2. **DRY (Don't Repeat Yourself)**: Extract repeated logic into composables or utilities
3. **KISS (Keep It Simple)**: Simplest solution that works is usually the best
4. **YAGNI (You Aren't Gonna Need It)**: Don't add functionality until it's actually needed
5. **Type Safety First**: Leverage TypeScript, avoid `any` type unless absolutely necessary

### File Organization Rules

1. **One Component Per File**: Each `.vue` file contains exactly one component
2. **Consistent Import Order**:
   ```typescript
   // Vue core
   import { ref, computed } from 'vue'

   // External libraries
   import { useRoute } from 'vue-router'

   // Internal stores
   import { useCartStore } from '@/stores/cart'

   // Internal composables
   import { useApi } from '@/composables/useApi'

   // Internal components
   import ProductCard from '@/components/features/ProductCard.vue'

   // Types
   import type { Product } from '@/types/models'

   // Assets
   import logo from '@/assets/logo.png'
   ```

3. **Barrel Exports**: Use `index.ts` files to export multiple related modules:
   ```typescript
   // components/common/index.ts
   export { default as Button } from './Button.vue'
   export { default as Input } from './Input.vue'
   export { default as Card } from './Card.vue'
   ```

### Vue Component Structure

Always structure Vue components in this order:

```vue
<script setup lang="ts">
// 1. Imports
import { ref, computed, onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import type { Product } from '@/types/models'

// 2. Props & Emits
interface Props {
  product: Product
  quantity?: number
}

const props = withDefaults(defineProps<Props>(), {
  quantity: 1
})

const emit = defineEmits<{
  addToCart: [product: Product, quantity: number]
}>()

// 3. Stores
const cartStore = useCartStore()

// 4. Reactive State
const isAdding = ref(false)

// 5. Computed Properties
const totalPrice = computed(() => props.product.price * props.quantity)

// 6. Methods
const handleAddToCart = async () => {
  isAdding.value = true
  try {
    await cartStore.addItem(props.product, props.quantity)
    emit('addToCart', props.product, props.quantity)
  } finally {
    isAdding.value = false
  }
}

// 7. Lifecycle Hooks
onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <!-- Keep template simple, extract complex logic to computed or methods -->
  <div class="product-card">
    <h3>{{ product.name }}</h3>
    <p>{{ totalPrice }}</p>
    <button @click="handleAddToCart" :disabled="isAdding">
      Add to Cart
    </button>
  </div>
</template>

<style scoped>
/* Scoped styles only, prefer Tailwind classes in template */
</style>
```

### Naming Conventions

- **Components**: `PascalCase` - `ProductCard.vue`, `ShoppingCartItem.vue`
- **Composables**: `camelCase` with `use` prefix - `useAuth.ts`, `useProductFilter.ts`
- **Stores**: `camelCase` - `auth.ts`, `shoppingCart.ts`
- **Utils/Helpers**: `camelCase` - `formatPrice.ts`, `validateEmail.ts`
- **Types/Interfaces**: `PascalCase` - `Product`, `CartItem`, `ApiResponse<T>`
- **Constants**: `SCREAMING_SNAKE_CASE` - `MAX_CART_ITEMS`, `API_BASE_URL`

### TypeScript Best Practices

1. **Interface over Type** for object shapes:
   ```typescript
   // Preferred
   interface Product {
     id: string
     name: string
   }

   // Use type for unions, intersections
   type Status = 'pending' | 'success' | 'error'
   ```

2. **Generic Types** for reusable patterns:
   ```typescript
   interface ApiResponse<T> {
     data: T
     status: number
     message: string
   }
   ```

3. **Avoid `any`**: Use `unknown` if type is truly unknown, then narrow with type guards:
   ```typescript
   function processData(data: unknown) {
     if (typeof data === 'string') {
       return data.toUpperCase()
     }
   }
   ```

### Code Quality Checklist

Before committing code, verify:

- [ ] All functions and variables have descriptive names
- [ ] No code duplication (DRY principle applied)
- [ ] TypeScript types defined for all data structures
- [ ] Components under 300 lines (extract composables if larger)
- [ ] All async operations have proper error handling
- [ ] Console.logs removed (use proper debugging or logging utility)
- [ ] No hardcoded values (use constants or environment variables)
- [ ] Imports organized in correct order
- [ ] Consistent code formatting (run `npm run type-check` before commit)

### Anti-Patterns to Avoid

**NEVER do these things:**

1. **Prop Drilling**: Passing props through multiple component levels
   ```typescript
   // BAD: Prop drilling
   <ParentComponent :user="user" />
     → <MiddleComponent :user="user" />
       → <ChildComponent :user="user" />

   // GOOD: Use store
   const userStore = useUserStore()
   const user = userStore.currentUser
   ```

2. **Business Logic in Components**: Keep components presentational
   ```typescript
   // BAD: Business logic in component
   const calculateTotal = () => {
     return items.value.reduce((sum, item) => {
       const discount = item.onSale ? item.price * 0.1 : 0
       return sum + (item.price - discount) * item.quantity
     }, 0)
   }

   // GOOD: Business logic in store
   const cartStore = useCartStore()
   const total = cartStore.totalWithDiscounts
   ```

3. **Direct DOM Manipulation**: Use Vue's reactivity
   ```typescript
   // BAD: Direct DOM manipulation
   document.getElementById('modal').style.display = 'block'

   // GOOD: Reactive state
   const isModalOpen = ref(false)
   ```

4. **Mutation of Props**: Props are read-only
   ```typescript
   // BAD: Mutating props
   props.user.name = 'New Name'

   // GOOD: Emit event to parent
   emit('updateUser', { ...props.user, name: 'New Name' })
   ```

5. **Using `any` Type**: Defeats TypeScript's purpose
   ```typescript
   // BAD: Using any
   const processData = (data: any) => { ... }

   // GOOD: Proper typing
   const processData = (data: Product[]) => { ... }
   // Or use unknown if truly unknown
   const processData = (data: unknown) => {
     if (isProductArray(data)) { ... }
   }
   ```

6. **Inline Complex Logic in Templates**: Keep templates readable
   ```vue
   <!-- BAD: Complex logic in template -->
   <template>
     <div>
       {{ items.filter(i => i.active).map(i => i.price * i.quantity).reduce((a, b) => a + b, 0) }}
     </div>
   </template>

   <!-- GOOD: Use computed property -->
   <template>
     <div>{{ activeItemsTotal }}</div>
   </template>

   <script setup lang="ts">
   const activeItemsTotal = computed(() =>
     items.value
       .filter(i => i.active)
       .reduce((sum, i) => sum + i.price * i.quantity, 0)
   )
   </script>
   ```

7. **Multiple Responsibilities in One File**: Violates Single Responsibility Principle
   ```typescript
   // BAD: Component handling API, validation, and UI
   const fetchUser = async () => { /* API call */ }
   const validateForm = () => { /* validation */ }
   const renderUI = () => { /* rendering */ }

   // GOOD: Separate concerns
   // useApi.ts composable handles API
   // validators.ts utility handles validation
   // Component only handles UI
   ```

8. **Global State in Components**: Use stores for shared state
   ```typescript
   // BAD: Shared reactive state in component
   export const sharedCart = ref([])

   // GOOD: Pinia store
   export const useCartStore = defineStore('cart', () => {
     const items = ref([])
     return { items }
   })
   ```

## Styling Architecture

- Uses **TailwindCSS** with **Frappe UI preset** ([tailwind.config.js:3](tailwind.config.js#L3))
- Custom color system using CSS variables that map to Frappe theme colors ([tailwind.config.js:23-70](tailwind.config.js#L23-L70))
- Main CSS file at [src/assets/main.css](src/assets/main.css)
- Supports both light/dark modes through CSS variables (defined in backend)
- Safe area insets for mobile/PWA support ([tailwind.config.js:17-22](tailwind.config.js#L17-L22))

## Vite Configuration Notes

- **Frappe UI Plugin** ([vite.config.ts:15-21](vite.config.ts#L15-L21)): Provides backend proxy and Lucide icon support
- **Dev Server**: Uses polling for file watching (useful in Docker/VM environments) ([vite.config.ts:40-44](vite.config.ts#L40-L44))
- **Build Target**: ES2015 for broad browser compatibility ([vite.config.ts:30](vite.config.ts#L30))
- **Source Maps**: Enabled in production builds ([vite.config.ts:31](vite.config.ts#L31))
- **Optimized Dependencies**: Pre-bundles frappe-ui components and common libraries ([vite.config.ts:46-48](vite.config.ts#L46-L48))

## Type Safety

- TypeScript is configured with project references ([tsconfig.json:3-10](tsconfig.json#L3-L10))
- Separate configs for app code (`tsconfig.app.json`) and build tools (`tsconfig.node.json`)
- Use `vue-tsc` instead of `tsc` for type-checking Vue files
- Path alias `@` maps to `./src` ([vite.config.ts:34-36](vite.config.ts#L34-L36))

## Working with Frappe UI

The `frappe-ui` package provides:
- Pre-built components for common UI patterns
- Resource management utilities (`frappeRequest`, `setConfig`)
- Frappe-specific styling and themes
- Automatic Lucide icon support when enabled in Vite config

When adding components, include frappe-ui component paths in Tailwind content config ([tailwind.config.js:7-8](tailwind.config.js#L7-L8)).

## Development Workflow

### Standard Development Process

1. **Setup**: Ensure Frappe backend is running (typically on port 8000)
2. **Start Dev Server**: Run `npm run dev` to start Vite dev server with hot-reload
3. **Code Structure**: Before writing code, plan your folder structure:
   - Is this a new feature? Create a feature folder in `src/components/features/`
   - Need shared state? Create a Pinia store in `src/stores/`
   - Reusable logic? Create a composable in `src/composables/`
   - Utility function? Add to `src/utils/`
   - New data model? Define types in `src/types/`

4. **Type-First Development**:
   - Define TypeScript interfaces BEFORE writing component code
   - Use `npm run type-check` frequently during development
   - Never use `any` - if uncertain, use `unknown` and narrow the type

5. **Component Development**:
   - Start with props interface and emits definition
   - Identify if component needs store access (global state) or props (parent data)
   - Keep components under 300 lines - extract logic to composables if needed
   - Use computed properties for derived values
   - Handle loading/error states properly

6. **State Management**:
   - For new global state, create a Pinia store first
   - Use Composition API syntax (`defineStore(() => { ... })`)
   - Define state, computed, and actions clearly
   - Add proper TypeScript types for all store properties

7. **Testing & Validation**:
   - Run `npm run type-check` before committing
   - Test in browser with hot-reload
   - Verify error handling and loading states
   - Check responsive design

8. **Production Build**: Run `npm run build` which:
   - Type-checks all code
   - Builds optimized bundle
   - Outputs to `../builder/public/frontend` for Frappe backend

### Code Organization During Development

When adding a new feature (e.g., "Product Reviews"):

1. Create types first:
   ```typescript
   // src/types/models.ts
   export interface Review {
     id: string
     productId: string
     rating: number
     comment: string
     author: string
     createdAt: Date
   }
   ```

2. Create store for state management:
   ```typescript
   // src/stores/reviews.ts
   export const useReviewsStore = defineStore('reviews', () => {
     const reviews = ref<Review[]>([])
     const isLoading = ref(false)

     const fetchReviews = async (productId: string) => { ... }
     const addReview = async (review: Review) => { ... }

     return { reviews, isLoading, fetchReviews, addReview }
   })
   ```

3. Create feature components:
   ```
   src/components/features/reviews/
   ├── ReviewList.vue       # Displays list of reviews
   ├── ReviewCard.vue       # Individual review display
   └── ReviewForm.vue       # Form to add new review
   ```

4. Create view if needed:
   ```typescript
   // src/views/Reviews/ReviewsPage.vue
   // Orchestrates ReviewList and ReviewForm components
   ```

### Quick Reference: Where Does Code Go?

- **Pinia Store** (`src/stores/`): Cart items, user session, product catalog, global loading states
- **Composable** (`src/composables/`): Form validation, API fetch patterns, debounce/throttle utilities
- **Component** (`src/components/`): UI elements (buttons, cards, forms, modals)
- **Utility** (`src/utils/`): Pure functions (formatters, validators, converters)
- **Type** (`src/types/`): Interfaces and type definitions
- **View** (`src/views/`): Page-level components that compose smaller components

## E-Commerce Context

This frontend is part of a larger e-commerce cooperative platform that integrates with:
- ERPNext for inventory, orders, and product management
- Payment gateways (PayPal, Stripe)
- Product catalogs with variants, inventory tracking
- Shopping cart and wishlist functionality
- User accounts and order tracking

The backend Python code handles business logic, while this Vue frontend provides the customer-facing interface.
