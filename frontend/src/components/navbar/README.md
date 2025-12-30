# Navbar Components

This directory contains all navigation bar related components for the Webshop frontend.

## Structure

```
navbar/
├── Navbar.vue           # Main navbar container component
├── NavbarLogo.vue       # Logo component with link to home
├── NavbarLinks.vue      # Navigation links component
├── NavbarActions.vue    # Action buttons (search, cart, wishlist, account)
├── index.ts            # Barrel export for easy imports
└── README.md           # This file
```

## Components

### Navbar.vue
Main container component that orchestrates all navbar sub-components.

**Props:**
- `storeName` (string, optional): Store name displayed in logo (default: "Webshop")
- `links` (NavLink[], optional): Array of navigation links
- `transparent` (boolean, optional): Transparent background (default: false)
- `sticky` (boolean, optional): Sticky positioning (default: true)

**Events:**
- `openSearch`: Emitted when search button is clicked
- `openCart`: Emitted when cart button is clicked

**Usage:**
```vue
<Navbar
  store-name="My Store"
  :links="navigationLinks"
  :sticky="true"
  @open-search="handleSearch"
  @open-cart="handleCart"
/>
```

### NavbarLogo.vue
Displays the store logo and name with a link to the home page.

**Props:**
- `storeName` (string, optional): Store name (default: "Webshop")

### NavbarLinks.vue
Renders the main navigation links. Hidden on mobile, shown on desktop.

**Props:**
- `links` (NavLink[], optional): Array of navigation links with default routes

**Default Links:**
- Home (/)
- Shop (/shop)
- Categories (/categories)
- About (/about)

### NavbarActions.vue
Action buttons for user interactions: search, wishlist, cart, account, and mobile menu.

**Features:**
- Search button
- Wishlist with badge counter
- Cart with badge counter
- User account link
- Mobile menu toggle (visible on mobile only)

**Events:**
- `openSearch`: Emitted when search is clicked
- `openCart`: Emitted when cart is clicked

## Types

Navigation types are defined in `@/types/navigation.ts`:

```typescript
interface NavLink {
  label: string
  to: string
  exact?: boolean
}
```

## Styling

All components use TailwindCSS with:
- Responsive design (mobile-first)
- Dark mode support
- Smooth transitions and hover effects
- Consistent spacing using Frappe UI tokens

## Customization

### Changing Navigation Links

```typescript
import type { NavLink } from '@/types/navigation'

const customLinks: NavLink[] = [
  { label: 'Home', to: '/', exact: true },
  { label: 'Products', to: '/products' },
  { label: 'Deals', to: '/deals' },
  { label: 'Contact', to: '/contact' }
]
```

### Customizing Logo

Override the logo appearance by modifying `NavbarLogo.vue` or pass a custom `storeName` prop.

### Adding New Actions

Extend `NavbarActions.vue` to add new action buttons. Follow the existing pattern for consistency.

## Future Enhancements

- [ ] Mobile menu drawer component
- [ ] Search modal/overlay
- [ ] Cart slide-out drawer
- [ ] Mega menu for categories
- [ ] User account dropdown menu
- [ ] Notification badge system
- [ ] Sticky scroll behavior customization
