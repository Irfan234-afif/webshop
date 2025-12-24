
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Payment Request": [
			{
				"fieldname": "payment_due_date",
				"label": "Payment Due Date",
				"fieldtype": "Datetime",
				"insert_after": "transaction_date",
				"no_copy": 1,
				"print_hide": 1
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
