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
		history_statuses = ["Completed", "Cancelled", "Canceled"]
		
		if tab == "history":
			# History tab: Only show Completed/Cancelled
			if status:
				# If specific status requested, ensure it belongs to history
				if status not in history_statuses:
					return {"orders": []} # Invalid status for this tab
				filters["status"] = status
			else:
				filters["status"] = ["in", history_statuses]
		else:
			# Orders tab: Show everything ELSE
			if status:
				# If specific status requested, ensure it belongs to active orders
				if status in history_statuses:
					return {"orders": []} # Invalid status for this tab
				filters["status"] = status
			else:
				filters["status"] = ["not in", history_statuses]

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
				"payment_method_type"
			],
			filters=filters,
			order_by="transaction_date desc",
			start=start,
			page_length=page_length
		)

		if orders:
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

			# Fetch items for these orders (optimized)
			all_items = frappe.get_all(
				"Sales Order Item",
				filters={"parent": ["in", order_names]},
				fields=["parent", "item_code", "item_name", "qty", "image", "amount"],
				order_by="idx asc"
			)
			
			# Map items to orders
			items_map = {}
			for item in all_items:
				if item.parent not in items_map:
					items_map[item.parent] = []
				items_map[item.parent].append(item)
				
			for order in orders:
				order.items = items_map.get(order.name, [])

		return {"orders": orders}

	except Exception as e:
		frappe.log_error(f"Error fetching orders: {str(e)}")
		frappe.throw(_("Error fetching orders"), title=_("Error"))


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

		# Get order items
		items = frappe.get_all(
			"Sales Order Item",
			fields=[
				"item_code",
				"item_name",
				"qty",
				"rate",
				"amount",
				"description",
				"image"
			],
			filters={"parent": order_name},
			order_by="idx asc"
		)

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

		return order_data

	except Exception as e:
		frappe.log_error(f"Error fetching order details: {str(e)}")
		frappe.throw(_("Error fetching order details"), title=_("Error"))
