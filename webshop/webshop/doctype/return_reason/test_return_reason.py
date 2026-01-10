# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
import unittest


class TestReturnReason(unittest.TestCase):
	"""Test Return Reason DocType"""
	
	def test_create_return_reason(self):
		"""Test creating a return reason"""
		# Clean up if exists
		if frappe.db.exists("Return Reason", "Test Defective Product"):
			frappe.delete_doc("Return Reason", "Test Defective Product")
		
		# Create return reason
		reason = frappe.get_doc({
			"doctype": "Return Reason",
			"reason_name": "Test Defective Product",
			"description": "Product has manufacturing defects",
			"enabled": 1
		})
		reason.insert()
		
		# Verify
		self.assertEqual(reason.reason_name, "Test Defective Product")
		self.assertEqual(reason.enabled, 1)
		
		# Clean up
		frappe.delete_doc("Return Reason", "Test Defective Product")
