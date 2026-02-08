# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add subscription days child table custom field to Subscription doctype.
This allows admin to view and edit the active days directly on the Subscription.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add custom fields for subscription days to Subscription DocType
	"""
	print("Adding subscription days custom field to Subscription...")

	custom_fields = {
		"Subscription": [
			{
				"fieldname": "days_section",
				"fieldtype": "Section Break",
				"label": "Active Days",
				"insert_after": "plans",
				"collapsible": 1,
			},
			{
				"fieldname": "days",
				"fieldtype": "Table",
				"label": "Days",
				"options": "Subscription Day",
				"insert_after": "days_section",
				"description": "List of active subscription days. Edit to adjust billing days.",
			},
		],
	}

	create_custom_fields(custom_fields, update=True)

	print("✓ Subscription days custom field added successfully")
