# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add payment_method_type custom field to Payment Request DocType
This enables Payment Request to store the selected payment method for any reference doctype
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add payment_method_type custom field to Payment Request
	This field allows Payment Request to store the selected payment method
	for any reference doctype (Sales Order, Sales Invoice, etc.)
	"""
	print("Adding payment_method_type custom field to Payment Request...")

	custom_fields = {
		"Payment Request": [
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Payment Method Type",
				"options": "Webshop Payment Method",
				"insert_after": "mode_of_payment",
				"read_only": 1,
				"description": "Webshop payment method selected by customer",
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()

	print("✓ payment_method_type custom field added to Payment Request successfully")
