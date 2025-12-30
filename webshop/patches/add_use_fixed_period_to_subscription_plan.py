import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add use_fixed_period field to Subscription Plan"""
	custom_fields = {
		"Subscription Plan": [
			{
				"fieldname": "use_fixed_period",
				"label": "Use Fixed Period",
				"fieldtype": "Check",
				"insert_after": "billing_interval_count",
				"description": (
					"If checked, subscription will use the Subscription End Date as invoice end date "
					"instead of calculating from billing interval. Useful for one-time fixed period "
					"subscriptions (e.g., catering service for specific date range)."
				),
				"default": 0,
			}
		]
	}
	create_custom_fields(custom_fields, update=True)
