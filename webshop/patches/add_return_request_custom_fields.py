import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Delivery Note": [
			{
				"fieldname": "return_request",
				"label": "Return Request",
				"fieldtype": "Link",
				"options": "Return Request",
				"insert_after": "is_return",
				"read_only": 1,
				"print_hide": 1
			}
		],
		"Sales Invoice": [
			{
				"fieldname": "return_request",
				"label": "Return Request",
				"fieldtype": "Link",
				"options": "Return Request",
				"insert_after": "is_return",
				"read_only": 1,
				"print_hide": 1
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
