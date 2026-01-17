import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Quotation": [
			{
				"fieldname": "payment_channel",
				"fieldtype": "Data",
				"label": "Payment Channel",
				"insert_after": "payment_method_type",
				"no_copy": 1
			}
		],
		"Sales Order": [
			{
				"fieldname": "payment_channel",
				"fieldtype": "Data",
				"label": "Payment Channel",
				"insert_after": "payment_method_type",
				"read_only": 1,
				"no_copy": 1
			}
		]
	}
	create_custom_fields(custom_fields, update=True)
