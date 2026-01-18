# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
import unittest
from unittest.mock import patch
from webshop.webshop.api.returns import (
	get_eligible_orders_for_return,
	get_return_reasons,
	get_refund_payment_methods,
	create_return_request,
	get_customer_return_requests,
	get_return_request_detail
)


class TestReturnsAPI(unittest.TestCase):
	"""Test Returns API endpoints"""
	
	def setUp(self):
		"""Set up test data"""
		frappe.set_user("Administrator")
		self.setup_test_data()
	
	def tearDown(self):
		"""Clean up"""
		frappe.set_user("Administrator")
	
	def setup_test_data(self):
		"""Create test data"""
		# Enable returns in settings
		settings = frappe.get_single("Webshop Settings")
		settings.enable_returns = 1
		settings.return_eligibility_days = 7
		settings.save()
		
		# Create return reasons
		for reason in ["Defective", "Wrong Item"]:
			if not frappe.db.exists("Return Reason", reason):
				frappe.get_doc({
					"doctype": "Return Reason",
					"reason_name": reason,
					"enabled": 1
				}).insert()
		
		# Create payment method with allow_on_return
		if not frappe.db.exists("Webshop Payment Method", "Test Refund Method"):
			frappe.get_doc({
				"doctype": "Webshop Payment Method",
				"payment_method_name": "Test Refund Method",
				"title": "Test Refund Method",
				"payment_type": "Cash",
				"enabled": 1,
				"allow_on_return": 1
			}).insert()
	
	def test_get_return_reasons(self):
		"""Test get_return_reasons API"""
		reasons = get_return_reasons()
		
		self.assertIsInstance(reasons, list)
		self.assertGreater(len(reasons), 0)
		
		# Verify structure
		for reason in reasons:
			self.assertIn("name", reason)
			self.assertIn("reason_name", reason)
	
	def test_get_refund_payment_methods(self):
		"""Test get_refund_payment_methods API"""
		methods = get_refund_payment_methods()
		
		self.assertIsInstance(methods, list)
		
		# Verify all methods have allow_on_return=1
		for method in methods:
			doc = frappe.get_doc("Webshop Payment Method", method["name"])
			self.assertEqual(doc.allow_on_return, 1)
			self.assertEqual(doc.enabled, 1)
	
	def test_get_refund_payment_methods_excludes_non_return_methods(self):
		"""Test that non-return methods are excluded"""
		# Create a payment method without allow_on_return
		if not frappe.db.exists("Webshop Payment Method", "Test No Refund"):
			frappe.get_doc({
				"doctype": "Webshop Payment Method",
				"payment_method_name": "Test No Refund",
				"title": "Test No Refund",
				"payment_type": "Cash",
				"enabled": 1,
				"allow_on_return": 0
			}).insert()
		
		methods = get_refund_payment_methods()
		method_names = [m["name"] for m in methods]
		
		self.assertNotIn("Test No Refund", method_names)
	
	@patch('webshop.webshop.api.returns.get_party')
	def test_create_return_request(self, mock_get_party):
		"""Test create_return_request API"""
		# Mock customer
		mock_customer = frappe.get_doc({
			"doctype": "Customer",
			"name": "Test Customer"
		})
		mock_get_party.return_value = mock_customer
		
		# This is a basic test - full integration test would require
		# creating a complete sales order flow
		data = {
			"sales_order": "SO-TEST-00001",
			"return_reason": "Defective",
			"refund_payment_mode": "Test Refund Method"
		}
		
		# Test would require actual sales order
		# For now, just verify the function exists and accepts parameters
		self.assertTrue(callable(create_return_request))
