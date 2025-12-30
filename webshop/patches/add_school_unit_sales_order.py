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
	# Create new custom fields with Dynamic Link
	custom_fields = {
		"Quotation": [
			{
				"fieldname": "school_unit",
				"fieldtype": "Link",
				"label": "School Unit",
				"options": "School Unit",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"fetch_from": "student.school_unit",
    			"read_only": 1
			}
		],
		"Sales Order": [
			{
				"fieldname": "school_unit",
				"fieldtype": "Link",
				"label": "School Unit",
				"options": "School Unit",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
    			"fetch_from": "student.school_unit",
    			"read_only": 1
			}
		],
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ School Unit fields updated successfully.")