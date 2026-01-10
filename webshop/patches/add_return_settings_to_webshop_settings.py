# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""Add return policy settings to Webshop Settings"""
	
	custom_fields = {
		"Webshop Settings": [
			{
				"fieldname": "return_policy_section",
				"label": "Return Policy Settings",
				"fieldtype": "Section Break",
				"insert_after": "guest_display_settings_section",
				"collapsible": 1
			},
			{
				"fieldname": "enable_returns",
				"label": "Enable Returns",
				"fieldtype": "Check",
				"default": "0",
				"insert_after": "return_policy_section"
			},
			{
				"fieldname": "return_eligibility_days",
				"label": "Return Eligibility Days",
				"fieldtype": "Int",
				"default": "7",
				"insert_after": "enable_returns",
				"depends_on": "eval:doc.enable_returns==1",
				"description": "Number of days after delivery within which returns are allowed"
			},
			{
				"fieldname": "return_policy_description",
				"label": "Return Policy Description",
				"fieldtype": "Text Editor",
				"insert_after": "return_eligibility_days",
				"depends_on": "eval:doc.enable_returns==1",
				"description": "Return policy text shown to customers"
			}
		]
	}
	
	create_custom_fields(custom_fields, update=True)
	
	frappe.db.commit()
