import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add student field to Subscription DocType"""
	
	custom_fields = {
		"Subscription": [
			{
				"fieldname": "student",
				"label": "Student",
				"fieldtype": "Link",
				"options": "Student",
				"insert_after": "party",
				"translatable": 0,
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
