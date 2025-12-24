# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.utils import flt

from webshop.webshop.doctype.item_review.item_review import get_customer
from webshop.webshop.shopping_cart.product_info import get_product_info_for_website
from webshop.webshop.utils.product import get_non_stock_item_status


class ProductQuery:
    """Query engine for product listing using raw SQL for maximum performance.

    Attributes:
            settings (Document): Webshop Settings DocType
            page_length (Int): Length of page for the query
    """

    def __init__(self):
        self.settings = frappe.get_doc("Webshop Settings")
        self.page_length = self.settings.products_per_page or 20
        self.base_fields = [
            "web_item_name",
            "name",
            "item_name",
            "item_code",
            "website_image",
            "variant_of",
            "has_variants",
            "item_group",
            "web_long_description",
            "short_description",
            "route",
            "website_warehouse",
            "ranking",
            "on_backorder",
        ]

    def query(self, attributes=None, fields=None, search_term=None, start=0, item_group=None, page_length=None):
        """
        Args:
                attributes (dict, optional): Item Attribute filters
                fields (dict, optional): Field level filters
                search_term (str, optional): Search term to lookup
                start (int, optional): Page start

        Returns:
                dict: Dict containing items, item count & discount range
        """
        if page_length:
            self.page_length = page_length
        
        # Track filters
        self.filter_with_discount = bool(fields.get("discount") if fields else False)
        self.filter_with_price = bool(fields.get("price") if fields else False)

        # Get cart settings and pricing info for SQL calculation
        from webshop.webshop.shopping_cart.cart import _set_price_list, get_party
        from webshop.webshop.doctype.webshop_settings.webshop_settings import (
            get_shopping_cart_settings,
        )

        cart_settings = get_shopping_cart_settings()
        self.selling_price_list = (
            _set_price_list(cart_settings, None) if cart_settings.enabled else None
        )

        # Get customer info for Pricing Rules
        party = get_party() if cart_settings.enabled else None
        self.customer = party.name if party and party.doctype == "Customer" else None
        self.customer_group = (
            cart_settings.default_customer_group if cart_settings.enabled else None
        )
        self.company = cart_settings.company if cart_settings.enabled else None

        self.price_filter_exact = None
        if self.filter_with_price and fields.get("price"):
            price_filter = fields["price"]
            if isinstance(price_filter, list) and len(price_filter) >= 1:
                self.price_filter_exact = {
                    "min": flt(price_filter[0]) if price_filter[0] else 0,
                    "max": (
                        flt(price_filter[1]) if len(price_filter) > 1 and price_filter[1] else None
                    ),
                }

        result, discount_list, cart_items, count = [], [], [], 0

        # Query results using raw SQL with final price calculation
        if attributes:
            result, count = self.query_items_with_attributes_raw_sql(
                attributes, fields, search_term, item_group, start
            )
        else:
            result, count = self.query_items_raw_sql(fields, search_term, item_group, start)

        # Sort by ranking
        result = sorted(result, key=lambda x: x.get("ranking") or 0, reverse=True)

        if self.settings.enabled:
            cart_items = self.get_cart_items()

        # Only add display details if not already calculated in SQL
        if not (self.filter_with_price or self.filter_with_discount):
            result, discount_list = self.add_display_details(result, discount_list, cart_items)
        else:
            # Price already calculated in SQL, just add cart/wishlist info
            for item in result:
                item.in_cart = item.item_code in cart_items
                item.wished = False
                if frappe.db.exists(
                    "Wishlist Item", {"item_code": item.item_code, "parent": frappe.session.user}
                ):
                    item.wished = True
                # Extract discount if available
                if item.get("final_discount_percent"):
                    discount_list.append(item.final_discount_percent)

        discounts = []
        if discount_list:
            discounts = [min(discount_list), max(discount_list)]

        # Calculate pagination info
        has_more = (start or 0) + len(result) < count
        current_start = start or 0
        items_returned = len(result)
        total_count = count

        return {
            "items": result,
            "items_count": count,
            "discounts": discounts,
            "pagination": {
                "has_more": has_more,
                "current_start": current_start,
                "items_returned": items_returned,
                "total_count": total_count,
                "page_length": self.page_length,
                "next_start": current_start + items_returned if has_more else None,
            },
        }

    def query_items_raw_sql(self, fields=None, search_term=None, item_group=None, start=0):
        """Build and execute raw SQL query with base price, then calculate final price in bulk."""

        # Build SELECT fields
        fields_sql = ", ".join([f"wi.`{field}`" for field in self.base_fields])

        # Query items with base price from Item Price
        # Final price will be calculated after query using bulk calculation
        if self.selling_price_list and (self.filter_with_price or self.filter_with_discount):
            query = f"""
				SELECT {fields_sql},
					ip.price_list_rate as base_price
				FROM `tabWebsite Item` wi
				INNER JOIN `tabItem Price` ip ON ip.item_code = wi.item_code
				WHERE wi.published = 1
				AND ip.price_list = %(price_list)s
			"""
        else:
            query = f"""
				SELECT {fields_sql}
				FROM `tabWebsite Item` wi
				WHERE wi.published = 1
			"""

        params = {}

        # Add pricing params if needed
        if self.selling_price_list and (self.filter_with_price or self.filter_with_discount):
            params["price_list"] = self.selling_price_list

        conditions = []

        # Hide variants if setting enabled
        if self.settings.hide_variants:
            conditions.append("wi.variant_of IS NULL")

        # Item group filter
        if item_group:
            item_group_conditions, item_group_params = self.build_item_group_conditions(item_group)
            if item_group_conditions:
                conditions.append(f"({item_group_conditions})")
                params.update(item_group_params)

        # Field filters (except discount and price which are handled separately)
        if fields:
            field_conditions, field_params = self.build_field_filters_raw_sql(fields)
            if field_conditions:
                conditions.extend(field_conditions)
                params.update(field_params)

        # Search term filter
        if search_term:
            search_conditions, search_params = self.build_search_conditions_raw_sql(search_term)
            if search_conditions:
                conditions.append(f"({search_conditions})")
                params.update(search_params)

        # Add all conditions
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Order by ranking first (before price filter)
        query += " ORDER BY wi.ranking DESC"

        # If price/discount filter, fetch all first (no limit)
        # Then calculate final price and filter
        if self.filter_with_price or self.filter_with_discount:
            # Fetch all items for price calculation
            items = frappe.db.sql(query, params, as_dict=True)

            # Calculate final price for all items in bulk
            items = self.calculate_final_prices_bulk(items)

            # Filter by final price/discount
            items = self.filter_by_price_discount(items, fields)

            # Get count after filtering
            count = len(items)

            # Apply pagination after filtering
            start_offset = start or 0
            items = items[start_offset : start_offset + self.page_length]
        else:
            # No price filter, use normal pagination
            count_query = f"""
				SELECT COUNT(DISTINCT wi.name) as total
				FROM `tabWebsite Item` wi
				WHERE wi.published = 1
			"""
            if conditions:
                count_query += " AND " + " AND ".join(conditions)

            count_result = frappe.db.sql(count_query, params, as_dict=True)
            count = count_result[0].total if count_result else 0

            # Add limit for pagination
            query += " LIMIT %(limit)s OFFSET %(offset)s"
            params["limit"] = self.page_length
            params["offset"] = start or 0

            items = frappe.db.sql(query, params, as_dict=True)

        # Map base_price to price_list_rate for items without final_price
        for item in items:
            if "base_price" in item and "price_list_rate" not in item:
                item.price_list_rate = item.base_price
            elif "final_price" in item and item.final_price is not None:
                item.price_list_rate = item.final_price

        return items, count

    def query_items_with_attributes_raw_sql(
        self, attributes, fields=None, search_term=None, item_group=None, start=0
    ):
        """Build and execute raw SQL query with attribute filters."""

        # First, get item_codes that match all attributes
        attribute_item_codes = self.get_items_by_attributes_raw_sql(attributes)

        if not attribute_item_codes:
            return [], 0

        # Build SELECT fields
        fields_sql = ", ".join([f"wi.`{field}`" for field in self.base_fields])

        # Base query with item_code filter using named parameters
        placeholder_list = []
        for i in range(len(attribute_item_codes)):
            placeholder_list.append(f"%({'item_code_' + str(i)})s")
        item_codes_placeholders = ", ".join(placeholder_list)
        query = f"""
			SELECT {fields_sql}
			FROM `tabWebsite Item` wi
			WHERE wi.published = 1
			AND wi.item_code IN ({item_codes_placeholders})
		"""

        params = {f"item_code_{i}": code for i, code in enumerate(attribute_item_codes)}
        conditions = []

        # Hide variants if setting enabled
        if self.settings.hide_variants:
            conditions.append("wi.variant_of IS NULL")

        # Item group filter
        if item_group:
            item_group_conditions, item_group_params = self.build_item_group_conditions(item_group)
            if item_group_conditions:
                conditions.append(f"({item_group_conditions})")
                params.update(item_group_params)

        # Field filters
        if fields:
            field_conditions, field_params = self.build_field_filters_raw_sql(fields)
            if field_conditions:
                conditions.extend(field_conditions)
                params.update(field_params)

        # Search term filter
        if search_term:
            search_conditions, search_params = self.build_search_conditions_raw_sql(search_term)
            if search_conditions:
                conditions.append(f"({search_conditions})")
                params.update(search_params)

        # Add all conditions
        if conditions:
            query += " AND " + " AND ".join(conditions)

        # Order by
        query += " ORDER BY wi.ranking DESC"

        # Count query
        count_query = f"""
			SELECT COUNT(DISTINCT wi.name) as total
			FROM `tabWebsite Item` wi
			WHERE wi.published = 1
			AND wi.item_code IN ({item_codes_placeholders})
		"""
        count_params = params.copy()
        if conditions:
            count_query += " AND " + " AND ".join(conditions)

        # Get count
        count_result = frappe.db.sql(count_query, count_params, as_dict=True)
        count = count_result[0].total if count_result else 0

        # If discount or price filter, fetch all (no limit)
        if self.filter_with_discount or self.filter_with_price:
            items = frappe.db.sql(query, params, as_dict=True)
        else:
            # Add limit for pagination
            query += " LIMIT %(limit)s OFFSET %(offset)s"
            params["limit"] = self.page_length
            params["offset"] = start
            items = frappe.db.sql(query, params, as_dict=True)

        return items, count

    def get_items_by_attributes_raw_sql(self, attributes):
        """Get item codes that match all attributes using raw SQL."""
        if not attributes:
            return []

        attribute_filters = []

        for attr_idx, (attribute, values) in enumerate(attributes.items()):
            if not values:
                continue

            if not isinstance(values, list):
                values = [values]

            # Get items with this attribute and value using named parameters
            placeholder_list = []
            for i in range(len(values)):
                param_name = f"attr_{attr_idx}_val_{i}"
                placeholder_list.append(f"%({param_name})s")
            value_placeholders = ", ".join(placeholder_list)
            attr_query = f"""
				SELECT DISTINCT iva.parent as item_code
				FROM `tabItem Variant Attribute` iva
				INNER JOIN `tabItem` i ON i.name = iva.parent
				WHERE i.published_in_website = 1
				AND iva.attribute = %(attr_{attr_idx}_name)s
				AND iva.attribute_value IN ({value_placeholders})
			"""

            attr_params = {f"attr_{attr_idx}_name": attribute}
            attr_params.update({f"attr_{attr_idx}_val_{i}": v for i, v in enumerate(values)})

            attr_result = frappe.db.sql(attr_query, attr_params, as_dict=True)

            if attribute_filters:
                # Intersect with previous results
                prev_codes = {row.item_code for row in attribute_filters}
                curr_codes = {row.item_code for row in attr_result}
                attribute_filters = [{"item_code": code} for code in prev_codes & curr_codes]
            else:
                attribute_filters = attr_result

        return [row.item_code for row in attribute_filters] if attribute_filters else []

    def build_item_group_conditions(self, item_group):
        """Build SQL conditions for item group filter using parameterized queries."""
        from webshop.webshop.doctype.override_doctype.item_group import (
            get_child_groups_for_website,
        )

        conditions = []
        params = {}

        # Normalize to list
        if isinstance(item_group, str):
            item_groups = [item_group]
        else:
            item_groups = item_group

        if not item_groups:
            return "", {}

        # 1. Expand groups to include descendants where applicable (for primary category check)
        expanded_groups = set(item_groups)
        for group in item_groups:
            # Check include_descendants setting provided behavior needs it
            # We use db.get_value. To avoid N items queries, we could optimize, but for a few categories it's fine.
            include_descendants = frappe.db.get_value("Item Group", group, "include_descendants")
            if include_descendants:
                children = get_child_groups_for_website(group, include_self=True)
                expanded_groups.update([x.name for x in children])
        
        expanded_list = list(expanded_groups)

        # Condition 1: Primary Category Match (using expanded groups)
        if expanded_list:
             ex_placeholders = []
             for i, g in enumerate(expanded_list):
                 p_name = f"ex_group_{i}"
                 params[p_name] = g
                 ex_placeholders.append(f"%({p_name})s")
             
             conditions.append(f"wi.item_group IN ({', '.join(ex_placeholders)})")

        # Condition 2: Website Item Group Match (secondary categories - direct match only)
        # We generally don't check descendants for secondary assignment unless logic dictates otherwise,
        # but original code didn't check descendants for this part either.
        if item_groups:
             dir_placeholders = []
             for i, g in enumerate(item_groups):
                 p_name = f"dir_group_{i}"
                 params[p_name] = g
                 dir_placeholders.append(f"%({p_name})s")
                 
             conditions.append(
                f"""wi.name IN (
                    SELECT parent 
                    FROM `tabWebsite Item Group` 
                    WHERE item_group IN ({', '.join(dir_placeholders)})
                )"""
             )

        return " OR ".join(conditions), params

    def build_field_filters_raw_sql(self, fields):
        """Build SQL conditions for field filters using parameterized queries."""
        conditions = []
        params = {}

        for field, values in fields.items():
            if not values or field in ("discount", "price"):
                continue

            # Get field metadata
            meta = frappe.get_meta("Website Item", cached=True)
            df = meta.get_field(field)

            if not df:
                continue

            # Handle Table MultiSelect fields
            if df.fieldtype == "Table MultiSelect":
                child_doctype = df.options
                child_meta = frappe.get_meta(child_doctype, cached=True)
                child_fields = child_meta.get("fields")
                if child_fields:
                    child_field = child_fields[0].fieldname
                    if isinstance(values, list):
                        placeholder_list = []
                        for i in range(len(values)):
                            param_name = f"field_{field}_{i}"
                            placeholder_list.append(f"%({param_name})s")
                        placeholders = ", ".join(placeholder_list)
                        conditions.append(
                            f"""wi.name IN (
							SELECT parent 
							FROM `tab{child_doctype}` 
							WHERE `{child_field}` IN ({placeholders})
						)"""
                        )
                        # Add values to params
                        for i, v in enumerate(values):
                            params[f"field_{field}_{i}"] = v
                    else:
                        conditions.append(
                            f"""wi.name IN (
							SELECT parent 
							FROM `tab{child_doctype}` 
							WHERE `{child_field}` = %(field_{field})s
						)"""
                        )
                        params[f"field_{field}"] = values
            # Handle regular fields
            elif isinstance(values, list):
                placeholder_list = []
                for i in range(len(values)):
                    param_name = f"field_{field}_{i}"
                    placeholder_list.append(f"%({param_name})s")
                placeholders = ", ".join(placeholder_list)
                conditions.append(f"wi.`{field}` IN ({placeholders})")
                for i, v in enumerate(values):
                    params[f"field_{field}_{i}"] = v
            else:
                conditions.append(f"wi.`{field}` = %(field_{field})s")
                params[f"field_{field}"] = values

        return conditions, params

    def build_search_conditions_raw_sql(self, search_term):
        """Build SQL conditions for search term."""
        # Default fields to search
        default_fields = ["item_code", "item_name", "item_group"]

        # Get meta search fields
        meta = frappe.get_meta("Website Item")
        meta_fields = set(meta.get_search_fields())

        search_fields = default_fields
        search_fields.extend(meta_fields)

        # Remove web_long_description if too many items
        if frappe.db.count("Website Item", cache=True) > 50000:
            search_fields = [f for f in search_fields if f != "web_long_description"]

        conditions = []
        search_pattern = f"%{frappe.db.escape(search_term)}%"

        for field in search_fields:
            if field in self.base_fields:
                conditions.append(f"wi.`{field}` LIKE %(search_term)s")

        params = {"search_term": f"%{search_term}%"}

        return " OR ".join(conditions) if conditions else "", params

    def add_display_details(self, result, discount_list, cart_items):
        """Add price and availability details in result."""
        # Bulk fetch variant prices for template items
        variant_prices_map = self._get_variant_prices_bulk(result)

        for item in result:
            # Handle template items with variants
            if item.get("has_variants") and item.item_code in variant_prices_map:
                self._set_template_item_price(item, variant_prices_map[item.item_code], discount_list)
            else:
                # Regular item or template without variant prices
                product_info = get_product_info_for_website(
                    item.item_code, skip_quotation_creation=True
                ).get("product_info")

                if product_info and product_info["price"]:
                    print("product_info", product_info)
                    self.get_price_discount_info(item, product_info["price"], discount_list)
                else:
                    item.price_list_rate = None
                    item.formatted_price = None
                    item.formatted_max_price = None
                    item.formatted_mrp = None

            if self.settings.show_stock_availability:
                self.get_stock_availability(item)

            item.in_cart = item.item_code in cart_items

            item.wished = False
            if frappe.db.exists(
                "Wishlist Item", {"item_code": item.item_code, "parent": frappe.session.user}
            ):
                item.wished = True

        return result, discount_list

    def _get_variant_prices_bulk(self, result):
        """Bulk fetch variant prices for all template items in the result."""
        from frappe.utils import fmt_money
        from webshop.webshop.shopping_cart.cart import get_party
        from erpnext.utilities.product import get_price

        # Identify template items
        template_items = [item.item_code for item in result if item.get("has_variants")]

        if not template_items or not self.selling_price_list:
            return {}

        # Bulk fetch all variants for all templates
        variants = frappe.get_all(
            "Item",
            filters={"variant_of": ["in", template_items], "disabled": 0},
            fields=["name", "variant_of"]
        )

        if not variants:
            return {}

        # Create mapping of template to variants
        template_to_variants = {}
        for variant in variants:
            parent = variant.variant_of
            if parent not in template_to_variants:
                template_to_variants[parent] = []
            template_to_variants[parent].append(variant.name)

        # Get party info for pricing rules
        from webshop.webshop.doctype.webshop_settings.webshop_settings import (
            get_shopping_cart_settings,
        )
        cart_settings = get_shopping_cart_settings()
        is_guest = frappe.session.user == "Guest"
        party = get_party() if cart_settings.enabled else None

        # Calculate prices for each template's variants
        variant_prices_map = {}

        for template_code, variant_codes in template_to_variants.items():
            variant_price_objects = []

            # Check if price should be shown
            if not cart_settings.show_price or (is_guest and cart_settings.hide_price_for_guest):
                continue

            # Get price for each variant with pricing rules applied
            for variant_code in variant_codes:
                try:
                    price_obj = get_price(
                        variant_code,
                        self.selling_price_list,
                        self.customer_group,
                        self.company,
                        party=party,
                    )
                    if price_obj and price_obj.get("price_list_rate"):
                        variant_price_objects.append({
                            "item_code": variant_code,
                            "price_list_rate": price_obj.get("price_list_rate"),
                            "currency": price_obj.get("currency"),
                            "formatted_price": price_obj.get("formatted_price"),
                        })
                except Exception:
                    # Skip variants with price errors
                    continue

            if variant_price_objects:
                variant_prices_map[template_code] = variant_price_objects

        return variant_prices_map

    def _set_template_item_price(self, item, variant_price_objects, discount_list):
        """Set price range for template items based on variant prices."""
        from frappe.utils import fmt_money

        if not variant_price_objects:
            item.price_list_rate = None
            item.formatted_price = None
            item.formatted_max_price = None
            item.formatted_mrp = None
            return

        # Calculate min and max prices
        prices = [p["price_list_rate"] for p in variant_price_objects]
        min_price = min(prices)
        max_price = max(prices)
        currency = variant_price_objects[0].get("currency")

        # Set price fields
        item.price_list_rate = min_price
        item.min_price = min_price
        item.max_price = max_price
        item.formatted_price = fmt_money(min_price, currency=currency) if currency else None
        item.formatted_max_price = fmt_money(max_price, currency=currency) if currency else None
        item.formatted_mrp = None
        item.is_price_range = True if min_price != max_price else False

    def get_price_discount_info(self, item, price_object, discount_list):
        """Modify item object and add price details."""
        fields = ["formatted_mrp", "formatted_price", "price_list_rate"]
        for field in fields:
            item[field] = price_object.get(field)

        if price_object.get("discount_percent"):
            item.discount_percent = flt(price_object.discount_percent)
            discount_list.append(price_object.discount_percent)

        if item.formatted_mrp:
            item.discount = price_object.get("formatted_discount_percent") or price_object.get(
                "formatted_discount_rate"
            )

    def get_stock_availability(self, item):
        """Modify item object and add stock details."""
        from webshop.templates.pages.wishlist import (
            get_stock_availability as get_stock_availability_from_template,
        )

        item.in_stock = False
        warehouse = item.get("website_warehouse")
        is_stock_item = frappe.get_cached_value("Item", item.item_code, "is_stock_item")

        if item.get("on_backorder"):
            return

        if not is_stock_item:
            if warehouse:
                item.in_stock = get_non_stock_item_status(item.item_code, "website_warehouse")
            else:
                item.in_stock = True
        elif warehouse:
            item.in_stock = get_stock_availability_from_template(item.item_code, warehouse)

    def get_cart_items(self):
        """Get items in cart for current user."""
        customer = get_customer(silent=True)
        if customer:
            quotation = frappe.get_all(
                "Quotation",
                fields=["name"],
                filters={
                    "party_name": customer,
                    "contact_email": frappe.session.user,
                    "order_type": "Shopping Cart",
                    "docstatus": 0,
                },
                order_by="modified desc",
                limit_page_length=1,
            )
            if quotation:
                items = frappe.get_all(
                    "Quotation Item",
                    fields=["item_code"],
                    filters={"parent": quotation[0].get("name")},
                )
                items = [row.item_code for row in items]
                return items

        return []

    def _get_cached_product_info(self, item_code):
        """Get cached product info to avoid redundant calculations."""
        from webshop.webshop.shopping_cart.product_info import get_product_info_for_website

        # Create unique cache key
        cache_key = f"{item_code}_{self.selling_price_list}_{self.customer or ''}_{self.customer_group or ''}"

        def generate_product_info():
            return get_product_info_for_website(item_code, skip_quotation_creation=True).get(
                "product_info"
            )

        # Use frappe.local_cache to cache per request
        return frappe.local_cache("product_info_cache", cache_key, generate_product_info)

    def calculate_final_prices_bulk(self, items):
        """Calculate final prices for all items using bulk Pricing Rules lookup with caching."""
        from frappe.utils import fmt_money

        if not items or not self.selling_price_list:
            return items

        # Bulk fetch variant prices for template items
        variant_prices_map = self._get_variant_prices_bulk(items)

        # Calculate final price for each item using cached product info
        for item in items:
            # Handle template items with variants
            if item.get("has_variants") and item.item_code in variant_prices_map:
                variant_price_objects = variant_prices_map[item.item_code]
                if variant_price_objects:
                    prices = [p["price_list_rate"] for p in variant_price_objects]
                    min_price = min(prices)
                    max_price = max(prices)
                    currency = variant_price_objects[0].get("currency")

                    item.final_price = min_price
                    item.price_list_rate = min_price
                    item.min_price = min_price
                    item.max_price = max_price
                    item.formatted_price = fmt_money(min_price, currency=currency) if currency else None
                    item.formatted_max_price = fmt_money(max_price, currency=currency) if currency else None
                    item.is_price_range = True if min_price != max_price else False
                    item.final_discount_percent = 0
                else:
                    item.final_price = None
                    item.price_list_rate = None
                    item.formatted_price = None
                    item.formatted_max_price = None
                    item.final_discount_percent = 0
                continue

            # Regular items
            if (
                not hasattr(item, "item_code")
                or not hasattr(item, "base_price")
                or item.base_price is None
            ):
                # Skip items without base_price
                item.final_price = None
                item.price_list_rate = None
                item.final_discount_percent = 0
                continue

            try:
                product_info = self._get_cached_product_info(item.item_code)

                if product_info and product_info.get("price"):
                    price_obj = product_info["price"]
                    final_price = price_obj.get("price_list_rate", item.base_price)
                    item.final_price = final_price
                    item.price_list_rate = final_price

                    # Calculate discount percent
                    base_price = flt(item.base_price) or 0
                    if base_price > 0:
                        discount_percent = ((base_price - flt(final_price)) / base_price) * 100
                        item.final_discount_percent = (
                            max(0, discount_percent) if discount_percent > 0 else 0
                        )
                    else:
                        item.final_discount_percent = 0
                else:
                    item.final_price = item.base_price
                    item.price_list_rate = item.base_price
                    item.final_discount_percent = 0
            except Exception:
                # Fallback to base price on error
                item.final_price = item.base_price
                item.price_list_rate = item.base_price
                item.final_discount_percent = 0

        return items

    def filter_by_price_discount(self, items, fields):
        """Filter items by final price and/or discount after bulk calculation."""
        filtered = []

        for item in items:
            # Filter by price
            if self.filter_with_price and self.price_filter_exact:
                min_price = self.price_filter_exact.get("min", 0)
                max_price = self.price_filter_exact.get("max")

                final_price = getattr(item, "final_price", None) or getattr(
                    item, "base_price", None
                )
                if final_price is None:
                    continue

                if min_price > 0 and final_price < min_price:
                    continue
                if max_price and final_price > max_price:
                    continue

            # Filter by discount
            if self.filter_with_discount and fields and fields.get("discount"):
                max_discount = flt(fields["discount"][0])
                discount_percent = getattr(item, "final_discount_percent", 0)

                if discount_percent > max_discount:
                    continue

            filtered.append(item)

        return filtered

    def build_final_price_subquery(self):
        """Build subquery to calculate final price after Pricing Rules discount."""
        # Get highest priority Pricing Rule and calculate final price
        # This is simplified version - handles most common cases
        subquery = """
		COALESCE(
			(SELECT 
				CASE 
					WHEN pr.rate_or_discount = 'Rate' THEN pr.rate
					WHEN pr.rate_or_discount = 'Discount Percentage' THEN 
						ip.price_list_rate * (1 - COALESCE(pr.discount_percentage, 0) / 100.0)
					WHEN pr.rate_or_discount = 'Discount Amount' THEN 
						GREATEST(ip.price_list_rate - COALESCE(pr.discount_amount, 0), 0)
					ELSE ip.price_list_rate
				END
			FROM `tabPricing Rule` pr
			LEFT JOIN `tabPricing Rule Item Code` pr_item ON pr_item.parent = pr.name AND pr_item.item_code = wi.item_code
			LEFT JOIN `tabPricing Rule Item Group` pr_ig ON pr_ig.parent = pr.name 
				AND pr_ig.item_group IN (SELECT name FROM `tabItem Group` WHERE lft <= (SELECT lft FROM `tabItem Group` WHERE name = wi.item_group) AND rgt >= (SELECT rgt FROM `tabItem Group` WHERE name = wi.item_group))
			WHERE pr.disable = 0
				AND pr.selling = 1
				AND pr.price_or_product_discount = 'Price'
				AND (pr_item.name IS NOT NULL OR pr_ig.name IS NOT NULL OR pr.apply_on = 'Transaction')
				AND IFNULL(pr.for_price_list, '') IN (%(price_list)s, '')
				AND IFNULL(pr.customer_group, '') IN (%(customer_group)s, '')
				AND IFNULL(pr.customer, '') IN (%(customer)s, '')
				AND %(transaction_date)s BETWEEN IFNULL(pr.valid_from, '2000-01-01') AND IFNULL(pr.valid_upto, '2500-12-31')
				AND IFNULL(pr.company, '') IN (%(company)s, '')
				AND IFNULL(pr.min_qty, 0) <= %(qty)s
				AND (IFNULL(pr.max_qty, 999999999) >= %(qty)s OR pr.max_qty IS NULL)
			ORDER BY 
				IFNULL(pr.priority, 999) DESC,
				pr.name DESC
			LIMIT 1),
			ip.price_list_rate
		)
		"""
        return subquery

    def build_discount_percent_subquery(self):
        """Build subquery to calculate discount percentage from Pricing Rules."""
        subquery = """
		COALESCE(
			(SELECT 
				CASE 
					WHEN pr.rate_or_discount = 'Discount Percentage' THEN pr.discount_percentage
					WHEN pr.rate_or_discount = 'Rate' THEN 
						CASE 
							WHEN ip.price_list_rate > 0 THEN 
								((ip.price_list_rate - pr.rate) / ip.price_list_rate) * 100
							ELSE 0
						END
					WHEN pr.rate_or_discount = 'Discount Amount' THEN 
						CASE 
							WHEN ip.price_list_rate > 0 THEN 
								(pr.discount_amount / ip.price_list_rate) * 100
							ELSE 0
						END
					ELSE 0
				END
			FROM `tabPricing Rule` pr
			LEFT JOIN `tabPricing Rule Item Code` pr_item ON pr_item.parent = pr.name AND pr_item.item_code = wi.item_code
			LEFT JOIN `tabPricing Rule Item Group` pr_ig ON pr_ig.parent = pr.name 
				AND pr_ig.item_group IN (SELECT name FROM `tabItem Group` WHERE lft <= (SELECT lft FROM `tabItem Group` WHERE name = wi.item_group) AND rgt >= (SELECT rgt FROM `tabItem Group` WHERE name = wi.item_group))
			WHERE pr.disable = 0
				AND pr.selling = 1
				AND pr.price_or_product_discount = 'Price'
				AND (pr_item.name IS NOT NULL OR pr_ig.name IS NOT NULL OR pr.apply_on = 'Transaction')
				AND IFNULL(pr.for_price_list, '') IN (%(price_list)s, '')
				AND IFNULL(pr.customer_group, '') IN (%(customer_group)s, '')
				AND IFNULL(pr.customer, '') IN (%(customer)s, '')
				AND %(transaction_date)s BETWEEN IFNULL(pr.valid_from, '2000-01-01') AND IFNULL(pr.valid_upto, '2500-12-31')
				AND IFNULL(pr.company, '') IN (%(company)s, '')
				AND IFNULL(pr.min_qty, 0) <= %(qty)s
				AND (IFNULL(pr.max_qty, 999999999) >= %(qty)s OR pr.max_qty IS NULL)
			ORDER BY 
				IFNULL(pr.priority, 999) DESC,
				pr.name DESC
			LIMIT 1),
			0
		)
		"""
        return subquery

    def build_count_query(self, fields=None, search_term=None, item_group=None):
        """Build count query with same filters as main query."""
        # This will be called from query_items_raw_sql
        # For now, return simple count query - will be enhanced
        return """
			SELECT COUNT(DISTINCT wi.name) as total
			FROM `tabWebsite Item` wi
			WHERE wi.published = 1
		"""
