import frappe
from frappe.utils import cint, flt
from webshop.webshop.shopping_cart.product_info import get_product_info_for_website
from webshop.webshop.doctype.item_review.item_review import get_item_reviews
from erpnext.utilities.product import get_price
import time

@frappe.whitelist(allow_guest=True)
def get_items_home(student=None):
    from webshop.webshop.product_engine.query import ProductQuery
    
    # Initialize filter parameters
    school_unit = None
    grade = None
    
    # If student is provided, fetch their school unit and grade
    if student:
        try:
            student_doc = frappe.get_cached_doc("Student", student)
            school_unit = student_doc.school_unit
            grade = student_doc.grade_level
        except Exception as e:
            frappe.log_error(f"Failed to fetch student details: {str(e)}")
            # Continue without filtering if student fetch fails
    
    # Build cache key based on School Unit and Grade combination
    if school_unit and grade:
        # Sanitize cache key to avoid special characters
        safe_unit = school_unit.replace(" ", "_").replace(":", "_")
        safe_grade = grade.replace(" ", "_").replace(":", "_")
        cache_key = f"webshop:items_home:{safe_unit}:{safe_grade}"
    elif school_unit:
        # Filter by unit only if grade is not available
        safe_unit = school_unit.replace(" ", "_").replace(":", "_")
        cache_key = f"webshop:items_home:{safe_unit}:all_grades"
    else:
        # General cache for guests or users without student context
        cache_key = "webshop:items_home:general"
    
    # Try to get cached data
    cached_data = frappe.cache().get_value(cache_key)
    if cached_data:
        return cached_data
    
    # Get all item groups to show on homepage
    item_groups = frappe.get_all(
        "Item Group",
        filters=[
            ['show_in_website', '=', 1]
        ],
        pluck="name"
    )

    # Limit to first 3 item groups and set items per group
    limited_groups = item_groups[:3]
    items_per_group = 15

    engine = ProductQuery()
    all_items = []
    all_discounts = []

    # Query each item group separately to ensure fair distribution
    for group in limited_groups:
        try:
            # Build query parameters with student filters
            query_params = {
                'item_group': group,
                'page_length': items_per_group
            }
            
            # Add School Unit filter if available
            if school_unit:
                query_params['school_unit'] = school_unit
            
            # Add Grade filter if available
            if grade:
                query_params['grade'] = grade
            
            group_result = engine.query(**query_params)
            
            if group_result and group_result.get('items'):
                all_items.extend(group_result['items'])
            
            # Collect discounts from each result
            if group_result and group_result.get('discounts'):
                all_discounts.extend(group_result['discounts'])
                
        except Exception as e:
            frappe.log_error(f"Product Query failed for group {group}: {str(e)}")
            continue

    # Fallback: If no items found with filters, retry without filters
    if not all_items and (school_unit or grade):
        frappe.log_error(f"No items found for school_unit={school_unit}, grade={grade}. Falling back to unfiltered results.")
        
        for group in limited_groups:
            try:
                group_result = engine.query(
                    item_group=group,
                    page_length=items_per_group
                )
                
                if group_result and group_result.get('items'):
                    all_items.extend(group_result['items'])
                
                if group_result and group_result.get('discounts'):
                    all_discounts.extend(group_result['discounts'])
                    
            except Exception as e:
                frappe.log_error(f"Fallback query failed for group {group}: {str(e)}")
                continue

    # Structure response to match expected format
    filtered_by_item_group = {}
    for group in limited_groups:
        item_by_group = [item for item in all_items if item.get('item_group') == group]
        if item_by_group:
            filtered_by_item_group[group] = item_by_group

    # Calculate overall discount range if any discounts found
    discounts = []
    if all_discounts:
        discounts = [min(all_discounts), max(all_discounts)]

    result = {
        'items': filtered_by_item_group,
        'items_count': len(all_items),
        'discounts': discounts
    }
    
    frappe.cache().set_value(cache_key, result, expires_in_sec=24 * 60 * 60)
    
    return result


@frappe.whitelist(allow_guest=True)
def get_product_detail(route):
    """
    Get comprehensive product detail for a Website Item.
    Includes images, variants, specifications, reviews, and pricing.

    Args:
        route: The Website Item route (URL path)

    Returns:
        dict: Product detail data including:
            - Basic info (title, description, category, rating)
            - Images array (gallery images)
            - Variants array (for items with variants)
            - Specifications
            - Reviews
            - Pricing and stock info
    """
    # Get Website Item by route
    website_item = frappe.db.get_value("Website Item", {"route": route}, "name")

    if not website_item:
        frappe.throw(frappe._("Website Item not found"), frappe.DoesNotExistError)

    # Get the full Website Item document
    doc = frappe.get_doc("Website Item", website_item)

    if not doc.published:
        frappe.throw(frappe._("This item is not published"), frappe.PermissionError)

    # Build response
    product_detail = {
        "id": doc.name,
        "route": doc.route,
        "item_code": doc.item_code,
        "offers": doc.offers,
        "type": "product",  # Default to product type
        "title": doc.web_item_name or doc.item_name,
        "category": doc.item_group,
        "short_description": doc.short_description or doc.description or "",
        "description": doc.web_long_description or doc.description or "",
        "is_subscription_item": doc.is_subscription_item,
        "rating": 0,  # Will be calculated from reviews
        "reviewCount": 0,  # Will be calculated from reviews
    }

    # Get images - combine website_image with gallery images
    images = []
    if doc.website_image:
        images.append(doc.website_image)

    # Add gallery images
    if doc.get("website_item_images"):
        for img in doc.website_item_images:
            if img.image:
                images.append(img.image)

    product_detail["images"] = images if images else None

    # Get pricing info
    product_info = get_product_info_for_website(doc.item_code, skip_quotation_creation=True)
    # frappe.throw(str(product_info))

    if product_info and product_info.product_info:
        price_info = product_info.product_info.get("price")
        if price_info:
            product_detail["price"] = flt(price_info.price_list_rate) if price_info.price_list_rate else 0
            product_detail["originalPrice"] = price_info.formatted_mrp if price_info.formatted_mrp else product_detail["price"]
            
            if price_info.discount_percent:
                product_detail["discountPercent"] = flt(price_info.discount_percent)
                product_detail["hasDiscount"] = True

    # Subscription Logic: Display Price Override for Post-Paid
    # if doc.is_subscription_item and doc.subscription_plan:
    #     plan = frappe.get_cached_doc("Subscription Plan", doc.subscription_plan)
    #     if plan.billing_timing == "Post-Paid":
    #         # Show Plan Cost as the display price (e.g. 100,000)
    #         # Even though Item Price is 0 for signup
    #         # Formatting uses standard helper or raw currency
    #         product_detail["price"] = flt(plan.cost)
    #         product_detail["originalPrice"] = flt(plan.cost)
    #         product_detail["priceLabel"] = f"{frappe.db.get_value('Currency', plan.currency, 'symbol') or plan.currency} {flt(plan.cost):,.0f} / {plan.billing_interval}"

    # Get variants if item has variants
    variants = []
    attributes_list = []
    price_range = None
    if doc.has_variants:
        variants, attributes_list, price_range = get_item_variants(doc.item_code)
        
        # Set price range if available (estimasi tanpa pricing rules)
        if price_range:
            product_detail["priceRange"] = price_range

    product_detail["variants"] = variants if variants else None
    product_detail["attributes"] = attributes_list if attributes_list else None

    # Get specifications
    specifications = []
    if doc.website_specifications:
        for spec in doc.website_specifications:
            specifications.append({
                "label": spec.label,
                "value": spec.description
            })

    # Add default specifications
    if doc.brand:
        specifications.append({"label": "Brand", "value": doc.brand})
    if doc.stock_uom:
        specifications.append({"label": "Unit", "value": doc.stock_uom})

    product_detail["specifications"] = specifications if specifications else None

    # Get reviews
    reviews_data = get_item_reviews(doc.name)
    if reviews_data and reviews_data.get("reviews"):
        product_detail["reviews"] = format_reviews(reviews_data.get("reviews", []))
        product_detail["reviewCount"] = len(reviews_data.get("reviews", []))
        product_detail["rating"] = flt(reviews_data.get("average_rating", 0))

    # Stock information
    product_detail["inStock"] = product_info.product_info.get("in_stock", False) if product_info else False
    product_detail["stockQuantity"] = flt(product_info.product_info.get("stock_qty", 0)) if product_info else None

    return product_detail


@frappe.whitelist(allow_guest=True)
def get_variant_price(item_code):
    """
    Get accurate price for a single variant with pricing rules applied.
    Called when user selects a variant in the frontend.
    
    This endpoint preserves all pricing logic including:
    - Pricing Rules (discount percentages, promotional pricing)
    - Customer-specific pricing
    - Party-based discounts
    - Dynamic pricing calculations
    
    Args:
        item_code: Variant item code
        
    Returns:
        dict: {
            "price": float,              # Discounted price
            "originalPrice": str,         # Formatted MRP/original price
            "discountPercent": float,     # Discount percentage if any
            "formattedPrice": str,        # Formatted currency string
            "formattedDiscount": str,     # Formatted discount string
            "currency": str               # Currency code
        }
    """
    from webshop.webshop.shopping_cart.cart import _set_price_list, get_party
    from webshop.webshop.doctype.webshop_settings.webshop_settings import get_shopping_cart_settings
    from erpnext.utilities.product import get_price
    
    cart_settings = get_shopping_cart_settings()
    
    if not cart_settings or not cart_settings.enabled:
        frappe.throw(frappe._("Shopping cart is not enabled"))
    
    # Check if price should be shown
    is_guest = frappe.session.user == "Guest"
    if is_guest and cart_settings.hide_price_for_guest:
        frappe.throw(frappe._("Price not available for guests"))
    
    price_list = _set_price_list(cart_settings, None)
    party = get_party()
    
    # Call get_price with pricing rules
    price_info = get_price(
        item_code,
        price_list,
        cart_settings.default_customer_group,
        cart_settings.company,
        qty=1,
        party=party
    )
    
    if not price_info:
        return {"price": 0, "error": "Price not found"}
    
    # Build response
    result = {
        "price": flt(price_info.get("price_list_rate", 0)),
        "currency": price_info.get("currency", "IDR"),
        "formattedPrice": price_info.get("formatted_price", ""),
    }
    
    # Add discount info if applicable
    if price_info.get("formatted_mrp"):
        result["originalPrice"] = price_info.get("formatted_mrp")
    
    if price_info.get("discount_percent"):
        result["discountPercent"] = flt(price_info.get("discount_percent"))
    
    if price_info.get("formatted_discount_percent"):
        result["formattedDiscount"] = price_info.get("formatted_discount_percent")
    
    return result


def get_item_variants(item_code):
    """
    Get all variants for a template item with their attributes and stock.
    
    NOTE: Prices are NOT included in variants for performance.
    Use get_variant_price() endpoint to fetch price on-demand when user selects a variant.
    
    Args:
        item_code: Template item code

    Returns:
        tuple: (variants list, attributes list, price_range dict)
            - variants: List of variant dictionaries with attributes and stock (NO PRICES)
            - attributes: List of available attributes with their values
            - price_range: Dict with min_price and max_price (estimasi tanpa pricing rules)
    """
    from webshop.webshop.shopping_cart.cart import _set_price_list
    from webshop.webshop.doctype.webshop_settings.webshop_settings import get_shopping_cart_settings

    # Get all enabled variants
    variants_list = frappe.get_all(
        "Item",
        filters={"variant_of": item_code, "disabled": 0},
        fields=["name", "item_name", "item_code", "stock_uom", "sales_uom", "is_stock_item"],
    )

    if not variants_list:
        return [], [], None

    cart_settings = get_shopping_cart_settings()
    variants = []
    attributes_detail = {}
    
    variant_codes = [v.item_code for v in variants_list]
    variant_attributes = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": ["in", variant_codes]},
        fields=["parent", "attribute", "attribute_value"],
        order_by="idx asc",
    )

    # Group attributes by variant and collect all attribute values
    attributes_by_variant = {}
    for attr in variant_attributes:
        if attr.parent not in attributes_by_variant:
            attributes_by_variant[attr.parent] = []
        attributes_by_variant[attr.parent].append(
            {"attribute": attr.attribute, "attribute_value": attr.attribute_value}
        )
        # Collect unique attribute values for frontend filter
        if attr.attribute not in attributes_detail:
            attributes_detail[attr.attribute] = set()
        attributes_detail[attr.attribute].add(attr.attribute_value)
    
    # Format attributes detail for frontend
    attributes_list = []
    for attr_name, attr_values in attributes_detail.items():
        unique_values = sorted(list(attr_values))
        attributes_list.append({"attribute": attr_name, "values": unique_values})

    # Batch fetch all variant stock in ONE query
    stock_map = {}
    bin_data = frappe.get_all(
        "Bin",
        filters={"item_code": ["in", variant_codes]},
        fields=["item_code", "actual_qty", "warehouse"],
    )
    
    # Aggregate stock by item_code (sum across warehouses)
    for bin_item in bin_data:
        if bin_item.item_code not in stock_map:
            stock_map[bin_item.item_code] = 0
        stock_map[bin_item.item_code] += flt(bin_item.actual_qty)

    # Batch fetch price range (estimasi, WITHOUT pricing rules for speed)
    # Actual prices with pricing rules will be fetched on-demand via get_variant_price()
    price_range = None
    if cart_settings and cart_settings.enabled and cart_settings.show_price:
        is_guest = frappe.session.user == "Guest"
        if not is_guest or not cart_settings.hide_price_for_guest:
            price_list = _set_price_list(cart_settings, None)
            
            # Batch query untuk min/max price (tanpa pricing rules)
            price_data = frappe.get_all(
                "Item Price",
                filters={
                    "item_code": ["in", variant_codes],
                    "price_list": price_list,
                    "selling": 1
                },
                fields=["price_list_rate"],
            )
            
            if price_data:
                prices = [flt(p.price_list_rate) for p in price_data if p.price_list_rate]
                if prices:
                    price_range = {
                        "min_price": min(prices),
                        "max_price": max(prices)
                    }

    # Build variant data - NO PRICES (lazy loaded on demand)
    for variant in variants_list:
        # Use already-fetched attributes
        attributes = attributes_by_variant.get(variant.item_code, [])

        # Determine stock status based on whether item maintains stock
        is_stock_item = variant.get("is_stock_item", 1)
        if is_stock_item:
            # For stock items, check actual stock quantity
            in_stock = stock_map.get(variant.item_code, 0) > 0
            stock_qty = stock_map.get(variant.item_code, 0)
        else:
            # For non-stock items (services, digital goods, etc.), always in stock
            in_stock = True
            stock_qty = 0

        # Build variant data WITHOUT price (will be fetched on-demand)
        variant_data = {
            "id": variant.name,
            "item_code": variant.item_code,
            "sku": variant.item_code,
            "attributes": attributes,
            "inStock": in_stock,
            "stockQuantity": stock_qty
            # NO PRICE FIELD - use get_variant_price() to fetch on-demand
        }

        variants.append(variant_data)

    return variants, attributes_list, price_range


def format_reviews(reviews):
    """
    Format reviews data for frontend consumption.

    Args:
        reviews: List of review dicts from get_item_reviews

    Returns:
        list: Formatted review dictionaries
    """
    formatted_reviews = []

    for review in reviews:
        formatted_review = {
            "id": review.get("name"),
            "productId": review.get("website_item"),
            "author": review.get("customer") or review.get("user"),
            "rating": cint(review.get("rating", 0)),
            "comment": review.get("review"),
            "createdAt": review.get("creation"),
            "helpful": 0  # This would need to be implemented if we add helpful voting
        }
        formatted_reviews.append(formatted_review)

    return formatted_reviews


@frappe.whitelist()
def get_cart_items():
    """
    Get shopping cart items with complete details including variant attributes.

    Returns:
        dict: Cart data with items array containing:
            - Basic item info (name, price, quantity, image)
            - Variant attributes (size, color, etc.) if applicable
            - Stock information
            - Student linkage (if using student-based cart)
    """
    from webshop.webshop.shopping_cart.cart import get_cart_quotation

    try:
        # Get cart quotation with decorated items
        cart_data = get_cart_quotation()

        if not cart_data or not cart_data.get("doc"):
            return {
                "items": [],
                "total": 0,
                "itemCount": 0
            }

        quotation = cart_data.get("doc")
        items = []

        for item in quotation.get("items", []):
            cart_item = {
                "id": item.name,
                "item_code": item.item_code,
                "productId": item.get("route") or item.item_code,
                "title": item.get("web_item_name") or item.item_name,
                "image": item.get("thumbnail") or item.get("website_image") or "",
                "price": flt(item.rate),
                "quantity": flt(item.qty),
                "amount": flt(item.amount),
                "description": item.get("description") or "",
                "route": item.get("route") or "",
                "warehouse": item.get("warehouse") or "",
                "service_start_date": item.get("service_start_date"),
                "service_end_date": item.get("service_end_date"),
                "isSubscription": item.get("is_subscription_item")
            }

            # Get variant attributes if item is a variant
            variant_attributes = get_item_variant_attributes(item.item_code)
            if variant_attributes:
                cart_item["variant_attributes"] = variant_attributes

                # Also set specific fields for common attributes
                for attr in variant_attributes:
                    attr_name = attr.get("attribute", "").lower()
                    if attr_name in ["size", "ukuran"]:
                        cart_item["selectedSize"] = attr.get("value")
                    elif attr_name in ["color", "warna", "colour"]:
                        cart_item["selectedColor"] = attr.get("value")

            # Get stock information
            stock_info = get_product_info_for_website(item.item_code, skip_quotation_creation=True)
            if stock_info and stock_info.product_info:
                cart_item["inStock"] = stock_info.product_info.get("in_stock", False)
                cart_item["stockQuantity"] = flt(stock_info.product_info.get("stock_qty", 0))

            # Student information (if applicable)
            if quotation.get("student_id"):
                cart_item["studentId"] = quotation.student_id
                cart_item["studentName"] = quotation.get("student_name")
                cart_item["schoolUnit"] = quotation.get("school_unit")

            items.append(cart_item)

        return {
            "items": items,
            "total": flt(quotation.grand_total or quotation.total),
            "itemCount": sum([flt(item.qty) for item in quotation.get("items", [])]),
            "quotation_name": quotation.name,
            "shipping_addresses": cart_data.get("shipping_addresses", []),
            "billing_addresses": cart_data.get("billing_addresses", [])
        }

    except Exception as e:
        frappe.log_error(f"Error getting cart items: {str(e)}")
        return {
            "items": [],
            "total": 0,
            "itemCount": 0,
            "error": str(e)
        }


def get_item_variant_attributes(item_code):
    """
    Get variant attributes for an item.

    Args:
        item_code: Item code to check for variant attributes

    Returns:
        list: List of variant attributes with attribute name and value
              Returns None if item has no variant attributes
    """
    # Check if item has variant attributes
    variant_attributes = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"]
    )

    if not variant_attributes:
        return None

    # Format attributes for frontend
    formatted_attributes = []
    for attr in variant_attributes:
        formatted_attributes.append({
            "attribute": attr.attribute,
            "value": attr.attribute_value,
            "label": attr.attribute,  # Can be customized to get translated label
            "displayValue": attr.attribute_value
        })

    return formatted_attributes


@frappe.whitelist()
def add_to_cart(item_code, qty=1, service_start_date=None, additional_notes=None, student=None):
    """
    Add item to shopping cart.

    Args:
        item_code: Item code to add
        qty: Quantity to add (default: 1)
        additional_notes: Optional notes for the item
        student: Optional student name to add item to specific student's cart.
                If provided, temporarily switches to that student's cart,
                adds the item, then restores the original active student.

    Returns:
        dict: Updated cart data
    """
    from webshop.webshop.shopping_cart.cart import update_cart
    from webshop.webshop.shopping_cart.student_utils import set_active_student, get_active_student

    try:
        qty = flt(qty)
        if qty <= 0:
            frappe.throw("Quantity must be greater than 0")

        # If student provided, temporarily set as active student for this operation
        original_student_doc = None
        if student:
            original_student_doc = get_active_student()
            set_active_student(student)

        try:
            # Update cart using existing cart functionality
            update_cart(item_code, qty, service_start_date, additional_notes, with_items=False)

            # Return updated cart
            return get_cart_items()
        finally:
            # Restore original student if we changed it
            if original_student_doc and student and original_student_doc.name != student:
                set_active_student(original_student_doc.name)

    except Exception as e:
        frappe.log_error(f"Error adding to cart: {str(e)}")
        frappe.throw(frappe._("Error adding to cart: {0}").format(str(e)))


@frappe.whitelist()
def update_cart_item_qty(item_code, qty, quotation_name):
    """
    Update quantity of item in cart.

    Args:
        item_code: Item code to update
        qty: New quantity (0 to remove item)
        student_name: Student name (optional) to specify which cart to update

    Returns:
        dict: Updated cart data
    """
    from webshop.webshop.shopping_cart.cart import update_cart

    try:
        qty = flt(qty)

        # Update cart (qty=0 will remove the item)
        update_cart(item_code, qty, with_items=False, quotation_name=quotation_name)

        # Return updated cart
        return get_cart_items()

    except Exception as e:
        frappe.log_error(f"Error updating cart item: {str(e)}")
        frappe.throw(str(e))


@frappe.whitelist()
def remove_from_cart(item_code, quotation_name):
    """
    Remove item from shopping cart.

    Args:
        item_code: Item code to remove
        student_name: Student name (optional) to specify which cart to remove from

    Returns:
        dict: Updated cart data
    """
    return update_cart_item_qty(item_code, 0, quotation_name)


@frappe.whitelist()
def get_all_student_cart_details():
    """
    Get detailed cart information for all students of the current customer.

    This is the primary endpoint for the multi-student cart page. It returns
    comprehensive cart data including items, totals, and student info for all
    students associated with the current customer account.

    Returns:
        dict: {
            "students": [
                {
                    "name": str,  # Student DocType name (unique identifier)
                    "student_name": str,  # Student's display name
                    "school_unit": str,
                    "is_active": int,
                    "items": [...],  # Full cart items array with variant attributes
                    "total": float,
                    "itemCount": int,
                    "quotation_name": str
                }
            ],
            "active_student": str,  # Currently selected student (Student DocType name)
            "grand_total": float,  # Sum of all students' carts
            "total_items": int     # Total item count across all students
        }
    """
    from webshop.webshop.shopping_cart.cart import get_party
    from webshop.webshop.shopping_cart.student_utils import get_active_student

    try:
        # Get current customer
        party = get_party()
        if not party:
            frappe.throw(frappe._("No customer account found"), title=frappe._("Authentication Required"))

        # Get all student cart summaries
        from webshop.webshop.api.student import get_all_student_carts
        student_carts = get_all_student_carts()

        # Get active student from session
        active_student_doc = get_active_student()
        active_student_name = active_student_doc.name if active_student_doc else None

        # Enhance each student cart with detailed items
        detailed_carts = []
        grand_total = 0
        total_items = 0

        for student_cart in student_carts:
            cart_summary = student_cart.get("cart")
            student_detail = {
                "name": student_cart["student_name"],  # Changed from student_id to name (Student DocType name)
                "student_name": student_cart["student_display_name"],  # Changed from student_name to student_display_name
                "school_unit": student_cart["school_unit"],
                "is_active": student_cart["is_active"],
                "items": [],
                "total": 0,
                "itemCount": 0,
                "quotation_name": None
            }

            if cart_summary:
                # Get full quotation details for this student
                quotation = frappe.get_doc("Quotation", cart_summary["name"])
                items = []

                for item in quotation.items:
                    variant_of = frappe.db.get_value("Item", item.item_code, "variant_of")
                    if variant_of:
                        image = frappe.db.get_value("Website Item", {"item_code": variant_of}, "website_image") or None
                    else:  
                        image = frappe.db.get_value("Website Item", {"item_code": item.item_code}, "website_image") or None

                    cart_item = {
                        "id": item.name,
                        "item_code": item.item_code,
                        "productId": item.get("route") or item.item_code,
                        "title": item.get("web_item_name") or item.item_name,
                        "image": image,
                        "price": flt(item.rate),
                        "quantity": flt(item.qty),
                        "amount": flt(item.amount),
                        "description": item.get("description") or "",
                        "route": item.get("route") or "",
                        "warehouse": item.get("warehouse") or "",
                        "student": student_cart["student_name"],  # Changed from studentId to student
                        "studentName": student_cart["student_display_name"],  # Changed from student_name to student_display_name
                        "schoolUnit": student_cart["school_unit"]
                    }

                    # Get variant attributes if item is a variant
                    variant_attributes = get_item_variant_attributes(item.item_code)
                    if variant_attributes:
                        cart_item["variant_attributes"] = variant_attributes
                        
                        # Get image from parent Website Item
                        # image = frappe.db.get_value("Website Item", {"item_code": item.item_code}, "website_image") or ""

                    # Get stock information
                    stock_info = get_product_info_for_website(item.item_code, skip_quotation_creation=True)
                    if stock_info and stock_info.product_info:
                        cart_item["inStock"] = stock_info.product_info.get("in_stock", False)
                        cart_item["stockQuantity"] = flt(stock_info.product_info.get("stock_qty", 0))

                    items.append(cart_item)

                student_detail["items"] = items
                student_detail["total"] = flt(cart_summary.get("grand_total", 0))
                student_detail["itemCount"] = int(cart_summary.get("total_qty", 0))
                student_detail["quotation_name"] = cart_summary["name"]

                grand_total += student_detail["total"]
                total_items += student_detail["itemCount"]

            detailed_carts.append(student_detail)

        return {
            "students": detailed_carts,
            "active_student": active_student_name,  # Changed from active_student_id to active_student
            "grand_total": grand_total,
            "total_items": total_items
        }

    except Exception as e:
        frappe.log_error(f"Error getting all student cart details: {str(e)}")
        return {
            "students": [],
            "active_student": None,  # Changed from active_student_id to active_student
            "grand_total": 0,
            "total_items": 0,
            "error": str(e)
        }


@frappe.whitelist(allow_guest=True)
def get_products(search_term=None, item_group=None, start=0, page_length=1000, price_min=None, price_max=None, school_unit=None, grade=None):
    from webshop.webshop.product_engine.query import ProductQuery
    from webshop.webshop.shopping_cart.student_utils import get_active_student
    import json
    from frappe.utils import cint

    # Handle item_group list
    if isinstance(item_group, str) and item_group.startswith("["):
        try:
             item_group = json.loads(item_group)
        except:
             pass

    # Handle school_unit list
    if isinstance(school_unit, str) and school_unit.startswith("["):
        try:
             school_unit = json.loads(school_unit)
        except:
             pass

    # Handle grade list
    if isinstance(grade, str) and grade.startswith("["):
        try:
             grade = json.loads(grade)
        except:
             pass

    # Auto-filter by active student's school unit if no unit filter provided
    if not school_unit:
        try:
            active_student = get_active_student()
            if active_student and hasattr(active_student, 'school_unit') and active_student.school_unit:
                school_unit = active_student.school_unit
        except Exception as e:
            # Log error but continue without auto-filtering
            frappe.log_error(f"Failed to get active student for auto-filtering: {str(e)}")

    fields = {}
    if price_min or price_max:
        fields["price"] = [flt(price_min), flt(price_max) if price_max else None]

    engine = ProductQuery()

    try:
        result = engine.query(
            fields=fields if fields else None,
            search_term=search_term,
            item_group=item_group,
            start=cint(start),
            page_length=cint(page_length),
            school_unit=school_unit,
            grade=grade
        )
    except Exception as e:
        frappe.log_error("Product Query failed: " + str(e))
        return []

    return result


@frappe.whitelist(allow_guest=True)
def get_item_groups():
    """Get all Item Groups that are enabled for website."""
    item_groups = frappe.get_all(
        "Item Group",
        filters={"show_in_website": 1},
        fields=["name", "item_group_name"],
        order_by="idx asc"
    )
    return item_groups


@frappe.whitelist(allow_guest=True)
def get_school_units():
    """Get all School Units."""
    try:
        return frappe.get_all(
            "School Unit", 
            filters={"is_active": 1},
            fields=["name", "unit_name", "unit_code", "sort_order"], 
            order_by="sort_order asc"
        )
    except Exception:
        return []


@frappe.whitelist(allow_guest=True)
def get_grades(school_unit=None):
    """Get all available grades, optionally filtered by school unit."""
    try:
        filters = {"enabled": 1}
        
        # If school_unit provided, filter by it
        if school_unit:
            filters["school_unit"] = school_unit
        
        grades = frappe.get_all(
            "Grade",
            filters=filters,
            fields=["name", "grade_name", "school_unit", "sort_order"],
            order_by="sort_order asc, name asc"
        )
        
        return grades
    except Exception as e:
        frappe.log_error(f"Error fetching grades", e)
        return []