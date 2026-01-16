# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to update checkout-related custom fields to use Dynamic Link instead of Select for payment method type
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Update custom fields for checkout flow to use Dynamic Link for payment method type
	"""
	print("Updating checkout custom fields to use Dynamic Link for payment method type...")

	# Delete the existing payment_method_type custom fields
	existing_fields = frappe.get_all("Custom Field", 
		filters={"fieldname": "payment_method_type", "dt": ["in", ["Quotation", "Sales Order"]]}, 
		pluck="name")
	
	for field_name in existing_fields:
		frappe.delete_doc("Custom Field", field_name, force=True)
		print(f"Deleted existing custom field: {field_name}")

	# Create new custom fields with Dynamic Link
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
			},
			{
				"fieldname": "pickup_date",
				"fieldtype": "Date",
				"label": "Hari Pengambilan",
				"insert_after": "payment_method_type",
				"depends_on": "eval:doc.pickup_type=='Ambil di koperasi'",
			},
			{
				"fieldname": "pickup_time_slot",
				"fieldtype": "Data",
				"label": "Jam Pengambilan",
				"insert_after": "pickup_date",
				"depends_on": "eval:doc.pickup_type=='Ambil di koperasi'",
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
			},
			{
				"fieldname": "pickup_date",
				"fieldtype": "Date",
				"label": "Hari Pengambilan",
				"insert_after": "payment_method_type",
			},
			{
				"fieldname": "pickup_time_slot",
				"fieldtype": "Data",
				"label": "Jam Pengambilan",
				"insert_after": "pickup_date",
				"read_only": 1,
			}
		],
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ Checkout custom fields updated successfully with Dynamic Link for payment method type")