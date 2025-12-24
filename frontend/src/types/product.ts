// Product type definitions for the product listing page

export type PriceRange = 'under-50k' | '50k-100k' | '100k-200k' | 'over-200k'

export interface Product {
  web_item_name:        string;
  name:                 string;
  item_name:            string;
  item_code:            string;
  website_image:        string;
  variant_of:           null;
  has_variants:         number;
  item_group:           string;
  web_long_description: string;
  short_description:    string;
  route:                string;
  website_warehouse:    string;
  ranking:              number;
  on_backorder:         number;
  formatted_mrp:        null | string;
  formatted_price:      string;
  price_list_rate:      number;
  in_stock:             boolean;
  in_cart:              boolean;
  wished:               boolean;
  discount_percent?:    number;
  discount?:            string;
  min_price?:           number;
  max_price?:           number;
  formatted_max_price?: string;
  is_price_range?:      boolean;
}

// export interface Service {
//   id: string
//   type: 'service'
//   icon: string
//   iconColor: string
//   category: string
//   rating: number
//   title: string
//   description: string
//   pricePerMonth: number
//   priceLabel: string
//   infoNotes?: string[]
//   bgGradient: string

//   priceRange: PriceRange
// }

// export type ProductOrService = Product | Service

export interface ProductFilters {
  categories: string[]

  priceRanges: PriceRange[]
}

export interface FilterOption {
  value: string | number
  label: string
  count?: number
}
