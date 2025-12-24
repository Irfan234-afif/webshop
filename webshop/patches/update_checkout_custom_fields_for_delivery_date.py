# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to update checkout-related custom fields to use delivery date instead of pickup date/time
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Update custom fields for checkout flow to use delivery date instead of pickup date/time
	"""
	print("Updating checkout custom fields to use delivery date instead of pickup date/time...")

	# Delete the existing pickup date and time slot custom fields
	existing_fields = frappe.get_all("Custom Field", 
		filters={"fieldname": ["in", ["pickup_date", "pickup_time_slot"]], "dt": ["in", ["Quotation", "Sales Order"]]}, 
		pluck="name")
	
	for field_name in existing_fields:
		frappe.delete_doc("Custom Field", field_name, force=True)
		print(f"Deleted existing custom field: {field_name}")

		# Create new custom fields without delivery date (using default delivery_date field)
	custom_fields = {
		"Quotation": [
			{
				"fieldname": "checkout_section",
				"fieldtype": "Section Break",
				"label": "Checkout Information",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"collapsible": 1,
			},
			{
				"fieldname": "pickup_type",
				"fieldtype": "Select",
				"label": "Jenis Pengambilan",
				"options": "\nAmbil di koperasi\nAmbil secara online",
				"insert_after": "checkout_section",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			},
			{
				"fieldname": "column_break_checkout",
				"fieldtype": "Column Break",
				"insert_after": "pickup_type",
			},
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Metode Pembayaran",
				"options": "Webshop Payment Method",
				"insert_after": "column_break_checkout",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			}
		],
		"Sales Order": [
			{
				"fieldname": "checkout_section",
				"fieldtype": "Section Break",
				"label": "Checkout Information",
				"insert_after": "student",
				"collapsible": 1,
			},
			{
				"fieldname": "pickup_type",
				"fieldtype": "Select",
				"label": "Jenis Pengambilan",
				"options": "\nAmbil di koperasi\nAmbil secara online",
				"insert_after": "checkout_section",
				"read_only": 1,
			},
			{
				"fieldname": "column_break_checkout",
				"fieldtype": "Column Break",
				"insert_after": "pickup_type",
			},
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Metode Pembayaran",
				"options": "Webshop Payment Method",
				"insert_after": "column_break_checkout",
				"read_only": 1,
			}
		],
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ Checkout custom fields updated successfully with delivery date instead of pickup date/time")