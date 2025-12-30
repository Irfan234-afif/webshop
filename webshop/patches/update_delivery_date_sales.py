# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to 
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Update delivery_date field to Sales Order
	"""
	print("Updating delivery_date field to Sales Order...")

    # Delete the existing payment_method_type custom fields
	existing_fields = frappe.get_all("Custom Field", 
		filters={"fieldname": "delivery_date", "dt": ["in", ["Quotation"]]}, 
		pluck="name")
	
	for field_name in existing_fields:
		frappe.delete_doc("Custom Field", field_name, force=True)
		print(f"Deleted existing custom field: {field_name}")

	custom_fields = {
		"Quotation": [
			{
				"fieldname": "delivery_date",
				"fieldtype": "Date",
				"label": "Delivery Date",
				"insert_after": "transaction_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			},
			{
				"fieldname": "delivery_time",
				"fieldtype": "Time",
				"label": "Delivery Time",
				"insert_after": "delivery_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			}
		],
		"Sales Order": [
			{
				"fieldname": "delivery_time",
				"fieldtype": "Time",
				"label": "Delivery Time",
				"insert_after": "delivery_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			}
		]
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ Delivery date field update to Quotation and Sales Order successfully")