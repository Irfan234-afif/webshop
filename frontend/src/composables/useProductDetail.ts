import { ref } from 'vue'
import type { ProductVariant, VariantAttribute } from '../types/productDetail'
import { useProductDetailStore } from '../stores/productDetail'

/**
 * Composable for managing product detail UI state
 * Handles image gallery, size selection, quantity, and tabs
 */
export function useProductDetail() {
  const productStore = useProductDetailStore()

  // Image gallery state
  const selectedImageIndex = ref(0)

  // Size selection state
  const selectedSize = ref<string | null>(null)

  // Variant selection state
  const selectedVariant = ref<VariantAttribute[] | []>([])

  // Final selected item variant
  const selectedItemVariant = ref<ProductVariant | null>(null)

  // Quantity state
  const quantity = ref(1)

  // Tab state
  const activeTab = ref<'details' | 'size-chart' | 'reviews'>('details')

  // Image gallery methods
  const selectImage = (index: number) => {
    selectedImageIndex.value = index
  }

  const nextImage = (totalImages: number) => {
    if (totalImages === 0) return
    selectedImageIndex.value = (selectedImageIndex.value + 1) % totalImages
  }

  const previousImage = (totalImages: number) => {
    if (totalImages === 0) return
    selectedImageIndex.value =
      (selectedImageIndex.value - 1 + totalImages) % totalImages
  }

  // Size selection methods
  const selectSize = (size: string) => {
    selectedSize.value = size
  }

  const clearSize = () => {
    selectedSize.value = null
  }

  // Variant selection methods
  const selectVariant = (variant: VariantAttribute) => {
    // Select: remove existing variant with the same attribute_name and add new one
    selectedVariant.value = selectedVariant.value?.filter(
      v => v.attribute !== variant.attribute
    ) ?? [];
    selectedVariant.value?.push(variant)

    // Update Selected Item Variant
    selectedItemVariant.value = productStore.currentProduct?.variants?.find(
      variant => variant.attributes.every(
        attribute => selectedVariant.value?.some(
          selected_variant => selected_variant.attribute_value == attribute.attribute_value &&
            selected_variant.attribute == attribute.attribute
        )
      )
    ) ?? null;

  }

  const hasVariantStock = (variant: VariantAttribute) => {
    const attribute = variant.attribute
    const attributeValue = variant.attribute_value

    const test_selection = selectedVariant.value?.filter(
      v => v.attribute !== attribute
    ) ?? [];
    test_selection.push({
      attribute: attribute,
      attribute_value: attributeValue
    });

    let has_stock = false;
    if (productStore.currentProduct?.variants && productStore.currentProduct?.variants?.length > 0) {
      has_stock = productStore.currentProduct?.variants.some(variant => {
        // Check if this variant matches the test selection
        const matches_selection = test_selection.every(selected_attr => {
          return variant.attributes && variant.attributes.some(
            attr => attr.attribute === selected_attr.attribute &&
              attr.attribute_value == selected_attr.attribute_value
          );
        });

        // If variant matches, check if it has stock
        if (matches_selection) {
          // Check inStock boolean instead of quantity
          return variant.inStock;
        }
        return false;
      });
    }
    return has_stock;
  }

  const someSelectedVariant = (variant: VariantAttribute): boolean => {
    return selectedVariant.value?.some(v => v.attribute === variant.attribute && v.attribute_value === variant.attribute_value) ?? false;
  }

  const clearVariant = () => {
    selectedVariant.value = []
  }

  // Quantity management methods
  const incrementQuantity = (max?: number) => {
    if (!max || quantity.value < max) {
      quantity.value++
    }
  }

  const decrementQuantity = () => {
    if (quantity.value > 1) {
      quantity.value--
    }
  }

  const setQuantity = (value: number, max?: number) => {
    if (value < 1) {
      quantity.value = 1
    } else if (max && value > max) {
      quantity.value = max
    } else {
      quantity.value = value
    }
  }

  // Tab management methods
  const setActiveTab = (tab: 'details' | 'size-chart' | 'reviews') => {
    activeTab.value = tab
  }

  // Validation methods
  const canAddToCart = (requiresSize: boolean): boolean => {
    if (requiresSize && !selectedSize.value) {
      return false
    }
    return quantity.value >= 1
  }

  // Reset all state
  const reset = () => {
    selectedImageIndex.value = 0
    selectedSize.value = null
    selectedVariant.value = []
    quantity.value = 1
    activeTab.value = 'details'
  }

  return {
    // State
    selectedImageIndex,
    selectedSize,
    selectedVariant,
    quantity,
    activeTab,
    selectedItemVariant,
    // Image gallery methods
    selectImage,
    nextImage,
    previousImage,
    // Size selection methods
    selectSize,
    clearSize,
    // Variant selection methods
    hasVariantStock,
    someSelectedVariant,
    selectVariant,
    clearVariant,
    // Quantity methods
    incrementQuantity,
    decrementQuantity,
    setQuantity,
    // Tab methods
    setActiveTab,
    // Validation
    canAddToCart,
    // Reset
    reset
  }
}
