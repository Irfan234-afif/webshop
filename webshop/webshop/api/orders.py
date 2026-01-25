# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Orders API Endpoints

Provides API endpoints for managing order history
"""

import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import get_party


@frappe.whitelist()
def get_orders(search_text=None, status=None, student=None, tab="orders", start=0, page_length=20):
	"""
	Get all orders for the currently logged-in customer

	Args:
		search_text (str, optional): Search by order name.
		status (str, optional): Filter by specific order status.
		student (str, optional): Filter by student name.
		tab (str, optional): 'orders' (active) or 'history' (completed). Defaults to 'orders'.
		start (int, optional): Start index for pagination. Defaults to 0.
		page_length (int, optional): Number of records to return. Defaults to 20.

	Returns:
		dict: Dictionary containing list of orders
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		filters = {"customer": party.name}

		if search_text:
			filters["name"] = ["like", f"%{search_text}%"]

		if student:
			filters["student"] = student

		# Tab scoping logic
		or_filters = None
		
		if tab == "history":
			# History tab: Completed (ecommerce) or Cancelled (standard)
			if status:
				if status in ["Cancelled", "Canceled"]:
					filters["status"] = status
				elif status == "Completed":
					filters["ecommerce_delivery_status"] = "Completed"
				else:
					return {"orders": []}
			else:
				# Show Completed OR Cancelled
				filters = {"customer": party.name} # Reset filters to avoid conflict
				if search_text: filters["name"] = ["like", f"%{search_text}%"]
				if student: filters["student"] = student
				
				or_filters = {
					"ecommerce_delivery_status": "Completed",
					"status": ["in", ["Cancelled", "Canceled"]]
				}
		else:
			# Orders tab: Show everything NOT Completed and NOT Cancelled
			if status:
				# Status from frontend: Pending, Processing, Shipped, Delivered, To Pay
				filters["ecommerce_delivery_status"] = status
			else:
				filters["ecommerce_delivery_status"] = ["!=", "Completed"]
				filters["status"] = ["not in", ["Cancelled", "Canceled"]]

		# Get sales orders for the customer
		orders = frappe.get_all(
			"Sales Order",
			fields=[
				"name", 
				"grand_total", 
				"total_qty", 
				"transaction_date", 
				"delivery_date",
				"status", 
				"student", 
				"school_unit",
				"order_type",
				"customer",
				"per_billed",
				"per_delivered",
				"payment_method_type",
				"coupon_code",
				"discount_amount",
				"ecommerce_delivery_status",
				"shipped_date",
				"delivered_date",
				"payment_method_type.payment_type",
			],
			filters=filters,
			or_filters=or_filters,
			order_by="transaction_date desc",
			start=start,
			page_length=page_length
		)

		if orders:
			order_names = [order.name for order in orders]

			# Filter out returned orders (per_delivered=0 and linked to a Return DN)
			returned_sos = frappe.db.sql("""
				SELECT distinct dni.against_sales_order
				FROM `tabDelivery Note Item` dni
				JOIN `tabDelivery Note` dn ON dn.name = dni.parent
				WHERE dni.against_sales_order IN %(orders)s
				AND dn.is_return = 1 AND dn.docstatus = 1
			""", {"orders": tuple(order_names)}, as_dict=True)
			
			returned_so_names = set([r.against_sales_order for r in returned_sos])
			
			orders = [
				order for order in orders 
				if not (order.per_delivered <= 0 and order.name in returned_so_names)
			]

			# Re-calculate order_names after filtering
			if not orders:
				return {"orders": []}

			order_names = [order.name for order in orders]
			
			# Fetch Payment Requests for these orders
			payment_requests = frappe.get_all(
				"Payment Request",
				filters={
					"reference_doctype": "Sales Order",
					"reference_name": ["in", order_names],
					"docstatus": ["!=", 2] # Exclude cancelled
				},
				fields=["reference_name", "status"],
				order_by="creation desc"
			)
			
			# Map Payment Request status to Orders
			pr_map = {}
			for pr in payment_requests:
				# Since we order by creation desc, the first one encountered for an order is the latest
				if pr.reference_name not in pr_map:
					pr_map[pr.reference_name] = pr.status

			for order in orders:
				order.payment_request_status = pr_map.get(order.name)

			all_items = frappe.db.sql("""
				SELECT 
					soi.parent,
					soi.item_code,
					soi.item_name,
					soi.qty,
					soi.amount,
					soi.idx,
					COALESCE(wi_parent.website_image, wi_direct.website_image, soi.image) as image
				FROM `tabSales Order Item` soi
				LEFT JOIN `tabItem` item ON item.name = soi.item_code
				LEFT JOIN `tabWebsite Item` wi_parent ON wi_parent.item_code = item.variant_of
				LEFT JOIN `tabWebsite Item` wi_direct ON wi_direct.item_code = soi.item_code
				WHERE soi.parent IN ({order_names})
				ORDER BY soi.parent, soi.idx ASC
			""".format(
				order_names=', '.join(['%s'] * len(order_names))
			), order_names, as_dict=True)
			
			# Map items to orders
			items_map = {}
			for item in all_items:
				if item.parent not in items_map:
					items_map[item.parent] = []
				items_map[item.parent].append(item)
				
			for order in orders:
				order.items = items_map.get(order.name, [])
			
			# Fetch Sales Taxes and Charges (for service fees display)
			all_taxes = frappe.db.sql("""
				SELECT 
					parent,
					description,
					tax_amount,
					idx
				FROM `tabSales Taxes and Charges`
				WHERE parent IN ({order_names})
				ORDER BY parent, idx ASC
			""".format(
				order_names=', '.join(['%s'] * len(order_names))
			), order_names, as_dict=True)
			
			# Map taxes to orders
			taxes_map = {}
			for tax in all_taxes:
				if tax.parent not in taxes_map:
					taxes_map[tax.parent] = []
				taxes_map[tax.parent].append(tax)
			
			for order in orders:
				order.taxes = taxes_map.get(order.name, [])
			
			# Fetch Delivery Note Image for history orders (completed/shipped)
			if tab == "history" or filters.get("status") == "Completed":
				# Find Delivery Note Items linked to these orders
				dn_items = frappe.get_all(
					"Delivery Note Item",
					filters={
						"against_sales_order": ["in", order_names],
						"docstatus": 1
					},
					fields=["parent", "against_sales_order", "item_code"]
				)
				
				if dn_items:
					dn_names = list(set([d.parent for d in dn_items]))
					
					# Get Delivery Notes with image
					delivery_notes = frappe.get_all(
						"Delivery Note",
						filters={"name": ["in", dn_names]},
						fields=["name", "image"],
						order_by="creation desc"
					)
					
					dn_image_map = {d.name: d.image for d in delivery_notes}
					
					# Map Sales Order -> Delivery Note Image (use latest DN if multiple)
					so_dn_map = {}
					for item in dn_items:
						if item.against_sales_order not in so_dn_map:
							# Since we don't have easy linking here without more queries or logic,
							# let's try to map the first one found or rely on the order?
							# Better approach: Group DNs by SO.
							pass
					
					# Re-map: specific logic
					# We have list of DN items. We want the image from the DN that contains items from this SO.
					# A SO can have multiple DNs. We'll pick the latest one that has an image.
					
					# Create a map of SO -> List of DN names
					so_to_dns = {}
					for item in dn_items:
						if item.against_sales_order not in so_to_dns:
							so_to_dns[item.against_sales_order] = set()
						so_to_dns[item.against_sales_order].add(item.parent)
						
					# Assign image to order
					for order in orders:
						if order.name in so_to_dns:
							# Check associated DNs for an image
							associated_dns = so_to_dns[order.name]
							# Find the first DN that has an image (checking in order of creation desc if possible, but our dn_names list is just names)
							# We have `delivery_notes` ordered by creation desc.
							found_image = None
							for dn in delivery_notes:
								if dn.name in associated_dns and dn.image:
									found_image = dn.image
									break # Found latest DN with image
							
							if found_image:
								order.delivery_image = found_image

		return {"orders": orders}

	except Exception as e:
		frappe.log_error(f"Error fetching orders: {str(e)}")
		frappe.throw(_("Error fetching orders"), title=_("Error"))

@frappe.whitelist()
def get_orders_count():
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	# Convert filters to SQL
	return frappe.db.sql("""
		SELECT count(so.name)
		FROM `tabSales Order` so
		WHERE so.customer = %(customer)s
		AND so.ecommerce_delivery_status != 'Completed'
		AND so.status NOT IN ('Cancelled', 'Canceled')
		AND NOT (
			so.per_delivered <= 0 AND EXISTS (
				SELECT 1 FROM `tabDelivery Note Item` dni
				JOIN `tabDelivery Note` dn ON dn.name = dni.parent
				WHERE dni.against_sales_order = so.name
				AND dn.is_return = 1 AND dn.docstatus = 1
			)
		)
	""", {"customer": party.name})[0][0]

@frappe.whitelist()
def get_order_filter_options():
	"""
	Get filter options for orders (students, etc.)

	Returns:
		dict: Dictionary containing students list
	"""
	party = get_party()
	if not party:
		return {"students": []}

	try:
		# Get distinct students
		students = frappe.db.get_list(
			"Sales Order",
			filters={"customer": party.name},
			fields=["student"],
			distinct=1,
			order_by="student asc"
		)
		
		student_list = [s.student for s in students if s.student]
		
		return {
			"students": student_list
		}
	except Exception as e:
		frappe.log_error(f"Error fetching filter options: {str(e)}")
		return {"students": []}


@frappe.whitelist()
def get_order_details(order_name):
	"""
	Get details for a specific order

	Args:
		order_name (str): Name of the order to get details for

	Returns:
		dict: Order details with items
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		# Get order details
		order = frappe.get_doc("Sales Order", order_name)

		# Verify that the order belongs to the current customer
		if order.customer != party.name:
			frappe.throw(_("You don't have permission to view this order"), title=_("Access Denied"))

		# Get order items with images in a single optimized query
		items = frappe.db.sql("""
			SELECT 
				soi.item_code,
				soi.item_name,
				soi.qty,
				soi.rate,
				soi.amount,
				soi.description,
				soi.idx,
				COALESCE(wi_parent.website_image, wi_direct.website_image, soi.image) as image
			FROM `tabSales Order Item` soi
			LEFT JOIN `tabItem` item ON item.name = soi.item_code
			LEFT JOIN `tabWebsite Item` wi_parent ON wi_parent.item_code = item.variant_of
			LEFT JOIN `tabWebsite Item` wi_direct ON wi_direct.item_code = soi.item_code
			WHERE soi.parent = %s
			ORDER BY soi.idx ASC
		""", order_name, as_dict=True)

		# Get student name if applicable
		student_name = None
		if order.student:
			student_name = frappe.get_value("Student", order.student, "student_name")

		order_data = {
			"name": order.name,
			"status": order.status,
			"transaction_date": order.transaction_date,
			"grand_total": order.grand_total,
			"total_qty": order.total_qty,
			"customer": order.customer_name or order.customer,
			"order_type": order.order_type,
			"student": order.student,
			"student_name": student_name,
			"items": items,
			"currency": order.currency
		}
		
		# Fetch Delivery Note Image
		dn = frappe.db.get_value("Delivery Note Item", {"against_sales_order": order_name}, "parent")
		if dn:
			image = frappe.db.get_value("Delivery Note", dn, "image")
			if image:
				order_data["delivery_image"] = image

		return order_data

	except Exception as e:
		frappe.log_error(f"Error fetching order details: {str(e)}")
		frappe.throw(_("Error fetching order details"), title=_("Error"))


@frappe.whitelist()
def confirm_order_delivery(order_name):
	"""
	Customer confirms they have received the order
	
	Args:
		order_name (str): Name of the Sales Order to confirm
	
	Returns:
		dict: Success status and message
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))
	
	try:
		# Get and verify order ownership
		order = frappe.get_doc("Sales Order", order_name)
		
		if order.customer != party.name:
			frappe.throw(_("You don't have permission to update this order"), title=_("Access Denied"))
		
		# Check if order can be confirmed (should be in Shipped status)
		if order.ecommerce_delivery_status != "Shipped":
			frappe.throw(
				_("Order cannot be confirmed. Current status: {0}").format(order.ecommerce_delivery_status),
				title=_("Invalid Status")
			)
		
		# Update status to Delivered
		from webshop.webshop.crud_events.delivery_note_events import update_sales_order_delivery_status
		update_sales_order_delivery_status(order_name, "Delivered")
		
		return {
			"success": True,
			"message": _("Order marked as delivered successfully")
		}
		
	except frappe.DoesNotExistError:
		frappe.throw(_("Order not found"), title=_("Error"))
	except Exception as e:
		frappe.log_error(f"Error confirming order delivery: {str(e)}")
		frappe.throw(_("Error confirming order delivery"), title=_("Error"))
