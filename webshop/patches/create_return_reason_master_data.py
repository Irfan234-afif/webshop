# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe


def execute():
	"""Create default return reasons"""
	
	# Check if Return Reason table exists
	if not frappe.db.table_exists("Return Reason"):
		print("Return Reason DocType not yet created, skipping...")
		return
	
	reasons = [
		{
			"reason_name": "Defective Product",
			"description": "Product has manufacturing defects or quality issues",
			"enabled": 1
		},
		{
			"reason_name": "Wrong Item Received",
			"description": "Received incorrect item or different from what was ordered",
			"enabled": 1
		},
		{
			"reason_name": "Size/Color Mismatch",
			"description": "Size or color does not match the description",
			"enabled": 1
		},
		{
			"reason_name": "Damaged During Delivery",
			"description": "Product was damaged during shipping",
			"enabled": 1
		},
		{
			"reason_name": "Changed Mind",
			"description": "Customer changed their mind about the purchase",
			"enabled": 1
		},
		{
			"reason_name": "Other",
			"description": "Other reason (please specify)",
			"enabled": 1
		}
	]
	
	for reason_data in reasons:
		if not frappe.db.exists("Return Reason", reason_data["reason_name"]):
			doc = frappe.get_doc({
				"doctype": "Return Reason",
				**reason_data
			})
			doc.insert(ignore_permissions=True)
			print(f"Created Return Reason: {reason_data['reason_name']}")
		else:
			print(f"Return Reason already exists: {reason_data['reason_name']}")
	
	frappe.db.commit()
