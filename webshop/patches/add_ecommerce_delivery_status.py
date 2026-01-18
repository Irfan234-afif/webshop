# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add e-commerce delivery status custom fields to Sales Order
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add e-commerce delivery status tracking fields to Sales Order
	"""
	print("Adding e-commerce delivery status custom fields to Sales Order...")

	custom_fields = {
		"Sales Order": [
			{
				"fieldname": "ecommerce_delivery_section",
				"fieldtype": "Section Break",
				"label": "E-commerce Delivery Status",
				"insert_after": "status",
				"collapsible": 1
			},
			{
				"fieldname": "ecommerce_delivery_status",
				"fieldtype": "Select",
				"label": "E-commerce Delivery Status",
				"options": "\nPending\nProcessing\nShipped\nDelivered\nCompleted",
				"default": "Pending",
				"insert_after": "ecommerce_delivery_section",
				"description": "Customer-facing delivery status for e-commerce orders"
			},
			{
				"fieldname": "column_break_ecommerce_delivery",
				"fieldtype": "Column Break",
				"insert_after": "ecommerce_delivery_status"
			},
			{
				"fieldname": "shipped_date",
				"fieldtype": "Datetime",
				"label": "Shipped Date",
				"insert_after": "column_break_ecommerce_delivery",
				"read_only": 1,
				"description": "Timestamp when order was marked as Shipped"
			},
			{
				"fieldname": "delivered_date",
				"fieldtype": "Datetime",
				"label": "Delivered Date",
				"insert_after": "shipped_date",
				"read_only": 1,
				"description": "Timestamp when customer confirmed delivery"
			}
		]
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ E-commerce delivery status custom fields added successfully")
