
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Subscription Plan": [
			{
				"fieldname": "billing_timing",
				"fieldtype": "Select",
				"label": "Billing Timing",
				"options": "Pre-Paid\nPost-Paid",
				"default": "Pre-Paid",
				"insert_after": "billing_interval_count",
				"description": "Pre-Paid: Subscription starts AFTER initial period. Post-Paid: Subscription starts IMMEDIATELY.",
				"reqd": 1
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
