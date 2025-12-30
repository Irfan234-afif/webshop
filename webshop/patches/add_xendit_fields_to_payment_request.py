import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Payment Request": [
			{
				"fieldname": "payment_channel_code",
				"fieldtype": "Data",
				"label": "Payment Channel Code",
				"read_only": 1,
				"insert_after": "payment_channel"
			},
			{
				"fieldname": "virtual_account_number",
				"fieldtype": "Data",
				"label": "Virtual Account Number",
				"read_only": 1,
				"insert_after": "payment_channel_code"
			},
			{
				"fieldname": "virtual_account_bank",
				"fieldtype": "Data",
				"label": "Virtual Account Bank",
				"read_only": 1,
				"insert_after": "virtual_account_number"
			}
		]
	}
	create_custom_fields(custom_fields, update=True)
