
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Delivery Note": [
			{
				"fieldname": "image",
				"label": "Image",
				"fieldtype": "Attach Image",
				"insert_after": "driver_name",
				"print_hide": 1,
				"reqd": 1
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
