# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Delivery Note Event Handlers

Handles Delivery Note submission events to update Sales Order e-commerce delivery status
"""

import frappe
from frappe import _
from frappe.utils import now


def on_delivery_note_submit(doc, method):
	"""
	Update linked Sales Order e-commerce delivery status to 'Shipped' when DN is submitted
	
	Args:
		doc: Delivery Note document
		method: Event method name
	"""
	if not doc.items:
		return
	
	# Get unique Sales Orders linked to this Delivery Note
	sales_orders = set()
	for item in doc.items:
		if item.against_sales_order:
			sales_orders.add(item.against_sales_order)
	
	if not sales_orders:
		return
	
	# Update each Sales Order
	for sales_order_name in sales_orders:
		try:
			update_sales_order_delivery_status(sales_order_name, "Shipped")
		except Exception as e:
			frappe.log_error(
				f"Error updating Sales Order {sales_order_name} delivery status: {str(e)}",
				title="Delivery Note Submit - Sales Order Update Failed"
			)


def update_sales_order_delivery_status(sales_order_name, status):
	"""
	Update Sales Order e-commerce delivery status
	
	Args:
		sales_order_name (str): Name of Sales Order to update
		status (str): New status (Shipped, Delivered, etc.)
	"""
	# Only update if Sales Order exists and has the ecommerce_delivery_status field
	if not frappe.db.exists("Sales Order", sales_order_name):
		return
	
	update_data = {
		"ecommerce_delivery_status": status
	}
	
	# Set timestamp based on status
	if status == "Shipped":
		update_data["shipped_date"] = now()
	elif status == "Delivered":
		update_data["delivered_date"] = now()
	
	# Use db_set to update without triggering workflow
	frappe.db.set_value("Sales Order", sales_order_name, update_data)
	
	frappe.log(f"Updated Sales Order {sales_order_name} ecommerce_delivery_status to {status}")
