import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Subscription": [
			{
				"fieldname": "sales_order_ref",
				"fieldtype": "Link",
				"options": "Sales Order",
				"label": "Source Sales Order",
				"read_only": 1,
				"insert_after": "party"
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
