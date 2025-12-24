# Navbar Structure Documentation

## Overview

A clean, maintainable, and modular navbar component structure has been created for the Frappe Webshop landing page.

## File Structure

```
src/
├── types/
│   └── navigation.ts                    # TypeScript interfaces for navigation
├── components/
│   ├── navbar/
│   │   ├── Navbar.vue                  # Main navbar container
│   │   ├── NavbarLogo.vue              # Logo component
│   │   ├── NavbarLinks.vue             # Navigation links
│   │   ├── NavbarActions.vue           # Action buttons (search, cart, etc.)
│   │   ├── index.ts                    # Barrel exports
│   │   └── README.md                   # Component documentation
│   └── layout/
│       ├── DefaultLayout.vue           # Main layout wrapper
│       └── index.ts                    # Barrel exports
├── views/
│   └── HomeView.vue                    # Updated landing page
└── App.vue                             # Updated to use DefaultLayout
```

## Architecture Principles

### 1. **Separation of Concerns**
Each component has a single, well-defined responsibility:
- `NavbarLogo` - Handles branding and home link
- `NavbarLinks` - Manages navigation menu items
- `NavbarActions` - Contains action buttons (search, cart, account)
- `Navbar` - Orchestrates all navbar sub-components
- `DefaultLayout` - Provides consistent page structure

### 2. **Composition Over Inheritance**
Components are composed together rather than using complex inheritance hierarchies, making them:
- Easy to understand
- Simple to test
- Flexible to modify

### 3. **Type Safety**
TypeScript interfaces ensure type safety across components:
```typescript
interface NavLink {
  label: string
  to: string
  exact?: boolean
}
```

### 4. **Prop-Driven Configuration**
Components accept props for customization without requiring code changes:
```vue
<Navbar
  store-name="My Store"
  :links="customLinks"
  :sticky="true"
/>
```

### 5. **Event-Driven Communication**
Parent-child communication uses Vue's event system:
```vue
<NavbarActions
  @open-search="handleSearch"
  @open-cart="handleCart"
/>
```

## Component Breakdown

### Navbar.vue (Main Container)
**Purpose**: Orchestrates all navbar sub-components and provides layout structure.

**Features**:
- Sticky positioning support
- Transparent background option
- Responsive layout
- Event aggregation

**Props**:
- `storeName`: Store branding
- `links`: Navigation items
- `transparent`: Background transparency
- `sticky`: Sticky positioning

**Events**:
- `openSearch`: Search modal trigger
- `openCart`: Cart drawer trigger

### NavbarLogo.vue
**Purpose**: Display store branding with home link.

**Features**:
- Auto-generated gradient logo
- First letter initial display
- Smooth hover effects
- RouterLink integration

### NavbarLinks.vue
**Purpose**: Render main navigation menu.

**Features**:
- Responsive (hidden on mobile)
- Active route highlighting
- Smooth underline animation
- Default link set provided

### NavbarActions.vue
**Purpose**: Action buttons for user interactions.

**Features**:
- Search button
- Wishlist with badge counter
- Cart with badge counter
- Account link
- Mobile menu toggle
- Responsive icon sizing

### DefaultLayout.vue
**Purpose**: Consistent page structure wrapper.

**Features**:
- Navbar integration
- Main content slot
- Footer placeholder
- Full viewport height
- Dark mode support

## Styling Approach

### TailwindCSS Utilities
All components use Tailwind utility classes for:
- Responsive design
- Dark mode
- Spacing and layout
- Colors and transitions

### Design Tokens
Colors use Frappe UI's CSS custom properties:
- `text-gray-900 dark:text-white` - Text colors
- `bg-white dark:bg-gray-900` - Backgrounds
- `border-gray-200 dark:border-gray-800` - Borders

### Responsive Breakpoints
- Mobile-first approach
- `md:` breakpoint (768px) for tablet/desktop
- Hidden/shown elements based on screen size

## Best Practices Implemented

### 1. **Component Modularity**
Each component can be used independently or composed together:
```vue
<!-- Use full navbar -->
<Navbar />

<!-- Or compose manually -->
<header>
  <NavbarLogo />
  <NavbarLinks />
  <NavbarActions />
</header>
```

### 2. **Default Props**
Sensible defaults ensure components work out-of-the-box:
```typescript
withDefaults(defineProps<Props>(), {
  storeName: 'Webshop',
  sticky: true,
  transparent: false
})
```

### 3. **TypeScript Integration**
Full TypeScript support with proper type definitions:
```typescript
import type { NavLink } from '@/types/navigation'
```

### 4. **Accessibility**
ARIA labels on interactive elements:
```vue
<button aria-label="Search">
  <!-- Icon -->
</button>
```

### 5. **Maintainable Structure**
- Clear file organization
- Barrel exports for clean imports
- Comprehensive documentation
- Consistent naming conventions

## Usage Examples

### Basic Usage
```vue
<template>
  <DefaultLayout>
    <div>Your content here</div>
  </DefaultLayout>
</template>
```

### Custom Configuration
```vue
<script setup lang="ts">
import { Navbar } from '@/components/navbar'
import type { NavLink } from '@/types/navigation'

const customLinks: NavLink[] = [
  { label: 'Home', to: '/', exact: true },
  { label: 'Products', to: '/products' },
  { label: 'About', to: '/about' }
]

const handleSearch = () => {
  // Open search modal
}

const handleCart = () => {
  // Open cart drawer
}
</script>

<template>
  <Navbar
    store-name="Custom Store"
    :links="customLinks"
    :sticky="true"
    @open-search="handleSearch"
    @open-cart="handleCart"
  />
</template>
```

### Layout Customization
```vue
<script setup lang="ts">
import { DefaultLayout } from '@/components/layout'

const myNavLinks = [
  { label: 'Shop', to: '/shop' },
  { label: 'Blog', to: '/blog' }
]
</script>

<template>
  <DefaultLayout
    store-name="My Shop"
    :nav-links="myNavLinks"
  >
    <RouterView />
  </DefaultLayout>
</template>
```

## Future Enhancements

### Planned Features
1. **Mobile Menu Drawer**
   - Slide-out navigation for mobile
   - Smooth animations
   - Touch gestures

2. **Search Modal**
   - Full-screen search overlay
   - Auto-complete functionality
   - Recent searches

3. **Cart Drawer**
   - Slide-out cart preview
   - Quick actions
   - Real-time updates

4. **Mega Menu**
   - Dropdown for categories
   - Multi-column layout
   - Image previews

5. **User Dropdown**
   - Account menu
   - Order history
   - Quick links

### Extensibility Points
The structure supports easy extension:
- Add new action buttons in `NavbarActions`
- Create new layouts in `components/layout/`
- Add navigation variants for different pages
- Implement custom themes via props

## Testing Strategy

### Component Testing
Each component can be tested independently:
```typescript
import { mount } from '@vue/test-utils'
import NavbarLogo from '@/components/navbar/NavbarLogo.vue'

test('renders store name', () => {
  const wrapper = mount(NavbarLogo, {
    props: { storeName: 'Test Store' }
  })
  expect(wrapper.text()).toContain('Test Store')
})
```

### Integration Testing
Test component composition:
```typescript
import { mount } from '@vue/test-utils'
import Navbar from '@/components/navbar/Navbar.vue'

test('emits openCart event', async () => {
  const wrapper = mount(Navbar)
  await wrapper.find('[aria-label="Shopping Cart"]').trigger('click')
  expect(wrapper.emitted('openCart')).toBeTruthy()
})
```

## Development Workflow

1. **Start Dev Server**
   ```bash
   npm run dev
   ```

2. **Type Check**
   ```bash
   npm run type-check
   ```

3. **Build**
   ```bash
   npm run build
   ```

## Key Benefits

✅ **Clean Structure** - Well-organized, easy to navigate
✅ **Maintainable** - Single responsibility, clear dependencies
✅ **Scalable** - Easy to add new features
✅ **Type-Safe** - Full TypeScript support
✅ **Responsive** - Mobile-first design
✅ **Accessible** - ARIA labels and semantic HTML
✅ **Customizable** - Prop-driven configuration
✅ **Documented** - Comprehensive documentation
✅ **Reusable** - Components can be used independently
✅ **Modern** - Vue 3 Composition API, script setup syntax

## Conclusion

This navbar structure provides a solid foundation for the Frappe Webshop frontend. It follows Vue.js and TypeScript best practices, is fully responsive, supports dark mode, and is designed for easy maintenance and extension.
