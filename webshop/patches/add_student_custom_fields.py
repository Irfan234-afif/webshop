# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add student-related custom fields to Customer, Quotation, and Sales Order
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add custom fields for student management to existing DocTypes
	"""
	print("Adding student custom fields to Customer, Quotation, and Sales Order...")

	custom_fields = {
		"Quotation": [
			{
				"fieldname": "school_section",
				"fieldtype": "Section Break",
				"label": "School Information",
				"insert_after": "party_name",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"collapsible": 1,
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "school_section",
				"read_only": 1,
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
			}
		],
		"Sales Order": [
			{
				"fieldname": "school_section",
				"fieldtype": "Section Break",
				"label": "School Information",
				"insert_after": "customer",
				"collapsible": 1,
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "school_section",
				"read_only": 1,
			}
		],
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ Custom fields added successfully")
