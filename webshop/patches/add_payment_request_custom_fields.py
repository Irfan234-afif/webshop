# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to add custom fields to Payment Request DocType for webshop manual payment approval workflow
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	"""
	Add custom fields to Payment Request for handling manual payment approvals with proof uploads
	"""
	print("Adding custom fields to Payment Request for webshop payment approval...")

	custom_fields = {
		"Payment Request": [
			{
				"fieldname": "webshop_approval_section",
				"fieldtype": "Section Break",
				"label": "Webshop Approval Details",
				"insert_after": "payment_url",
				"collapsible": 1,
			},
			{
				"fieldname": "payment_proof",
				"fieldtype": "Attach",
				"label": "Payment Proof",
				"insert_after": "webshop_approval_section",
				"description": "Upload proof of payment (bank transfer receipt, etc.)",
			},
			{
				"fieldname": "column_break_webshop",
				"fieldtype": "Column Break",
				"insert_after": "payment_proof",
			},
			{
				"fieldname": "remarks",
				"fieldtype": "Text",
				"label": "Remarks",
				"insert_after": "column_break_webshop",
				"description": "Admin notes or rejection reasons",
			},
			{
				"fieldname": "approval_metadata_section",
				"fieldtype": "Section Break",
				"label": "Approval Metadata",
				"insert_after": "remarks",
				"collapsible": 1,
				"depends_on": "eval:doc.docstatus > 0",
			},
			{
				"fieldname": "admin_approval_by",
				"fieldtype": "Link",
				"label": "Approved/Rejected By",
				"options": "User",
				"insert_after": "approval_metadata_section",
				"read_only": 1,
			},
			{
				"fieldname": "admin_approval_time",
				"fieldtype": "Datetime",
				"label": "Approval/Rejection Time",
				"insert_after": "admin_approval_by",
				"read_only": 1,
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.db.commit()

	print("✓ Custom fields added to Payment Request successfully")
