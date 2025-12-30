# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add delivery_date field to Quotation doctype
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add delivery_date field to Quotation doctype
	"""
	print("Adding delivery_date field to Quotation...")

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

	print("✓ Delivery date field added to Quotation successfully")