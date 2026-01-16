# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
import unittest
from webshop.webshop.api.checkout import calculate_service_charges


class TestServiceCharges(unittest.TestCase):
	"""Test service charge calculation and application"""
	
	def setUp(self):
		"""Set up test data"""
		# Create test company
		if not frappe.db.exists("Company", "_Test Company"):
			frappe.get_doc({
				"doctype": "Company",
				"company_name": "_Test Company",
				"default_currency": "IDR",
				"country": "Indonesia",
				"abbr": "_TC"
			}).insert(ignore_permissions=True)
		
		# Create income account for charges
		income_account = frappe.db.get_value("Account", {
			"company": "_Test Company",
			"root_type": "Income",
			"is_group": 0
		}, "name")
		
		if not income_account:
			root_income = frappe.db.get_value("Account", {
				"company": "_Test Company",
				"root_type": "Income",
				"is_group": 1
			}, "name")
			
			if root_income:
				income_account = frappe.get_doc({
					"doctype": "Account",
					"account_name": "Service Fee Income",
					"parent_account": root_income,
					"company": "_Test Company",
					"is_group": 0,
					"root_type": "Income",
					"account_type": "Income Account",
					"currency": "IDR"
				}).insert(ignore_permissions=True).name
		
		self.income_account = income_account
		
		# Create test payment method with multiple charges
		self.payment_method_name = "Test Payment with Service Charges"
		
		if frappe.db.exists("Webshop Payment Method", self.payment_method_name):
			frappe.delete_doc("Webshop Payment Method", self.payment_method_name, force=1)
		
		frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": self.payment_method_name,
			"title": "Test Payment",
			"payment_type": "Cash",  # Use Cash to avoid validation requirements
			"enabled": 1,
			"payment_charges": [
				{
					"charge_type": "On Net Total",
					"description": "Platform Fee",
					"rate": 2.0,  # 2%
					"account_head": self.income_account
				},
				{
					"charge_type": "Actual",
					"description": "Gateway Fee",
					"tax_amount": 5000,  # Fixed Rp 5,000
					"account_head": self.income_account
				}
			]
		}).insert(ignore_permissions=True)
	
	def tearDown(self):
		"""Clean up"""
		if frappe.db.exists("Webshop Payment Method", self.payment_method_name):
			frappe.delete_doc("Webshop Payment Method", self.payment_method_name, force=1)
	
	def test_calculate_service_charges_percentage(self):
		"""Test calculating percentage-based service charge"""
		subtotal = 100000  # Rp 100,000
		
		result = calculate_service_charges(self.payment_method_name, subtotal)
		
		self.assertIn("charges", result)
		self.assertIn("total", result)
		
		charges = result["charges"]
		self.assertEqual(len(charges), 2)
		
		# Check percentage charge (2% of 100,000 = 2,000)
		percentage_charge = charges[0]
		self.assertEqual(percentage_charge["charge_type"], "On Net Total")
		self.assertEqual(percentage_charge["description"], "Platform Fee")
		self.assertEqual(percentage_charge["rate"], 2.0)
		self.assertEqual(percentage_charge["charge_amount"], 2000)
		
		# Check fixed charge
		fixed_charge = charges[1]
		self.assertEqual(fixed_charge["charge_type"], "Actual")
		self.assertEqual(fixed_charge["description"], "Gateway Fee")
		self.assertEqual(fixed_charge["charge_amount"], 5000)
		
		# Check total (2,000 + 5,000 = 7,000)
		self.assertEqual(result["total"], 7000)
	
	def test_calculate_service_charges_different_subtotal(self):
		"""Test calculation with different subtotal amounts"""
		test_cases = [
			(50000, 1000, 6000),   # 2% of 50k = 1k, total = 6k
			(200000, 4000, 9000),  # 2% of 200k = 4k, total = 9k
			(0, 0, 5000),          # 2% of 0 = 0, total = 5k (only fixed)
		]
		
		for subtotal, expected_percentage, expected_total in test_cases:
			result = calculate_service_charges(self.payment_method_name, subtotal)
			percentage_charge = result["charges"][0]
			
			self.assertEqual(
				percentage_charge["charge_amount"], 
				expected_percentage,
				f"Failed for subtotal {subtotal}"
			)
			self.assertEqual(
				result["total"], 
				expected_total,
				f"Failed total for subtotal {subtotal}"
			)
	
	def test_calculate_service_charges_no_charges(self):
		"""Test calculation for payment method without charges"""
		# Create method without charges
		method_name = "Test No Charges"
		
		if frappe.db.exists("Webshop Payment Method", method_name):
			frappe.delete_doc("Webshop Payment Method", method_name, force=1)
		
		frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": method_name,
			"title": "No Charges",
			"payment_type": "Cash",
			"enabled": 1
		}).insert(ignore_permissions=True)
		
		result = calculate_service_charges(method_name, 100000)
		
		self.assertEqual(len(result["charges"]), 0)
		self.assertEqual(result["total"], 0)
		
		# Cleanup
		frappe.delete_doc("Webshop Payment Method", method_name, force=1)
	
	def test_calculate_service_charges_only_percentage(self):
		"""Test calculation with only percentage charge"""
		method_name = "Test Only Percentage"
		
		if frappe.db.exists("Webshop Payment Method", method_name):
			frappe.delete_doc("Webshop Payment Method", method_name, force=1)
		
		frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": method_name,
			"title": "Only Percentage",
			"payment_type": "Cash",
			"enabled": 1,
			"payment_charges": [{
				"charge_type": "On Net Total",
				"description": "Service Fee",
				"rate": 1.5,
				"account_head": self.income_account
			}]
		}).insert(ignore_permissions=True)
		
		result = calculate_service_charges(method_name, 100000)
		
		self.assertEqual(len(result["charges"]), 1)
		self.assertEqual(result["charges"][0]["charge_amount"], 1500)  # 1.5% of 100k
		self.assertEqual(result["total"], 1500)
		
		# Cleanup
		frappe.delete_doc("Webshop Payment Method", method_name, force=1)
	
	def test_calculate_service_charges_only_fixed(self):
		"""Test calculation with only fixed charge"""
		method_name = "Test Only Fixed"
		
		if frappe.db.exists("Webshop Payment Method", method_name):
			frappe.delete_doc("Webshop Payment Method", method_name, force=1)
		
		frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": method_name,
			"title": "Only Fixed",
			"payment_type": "Cash",
			"enabled": 1,
			"payment_charges": [{
				"charge_type": "Actual",
				"description": "Admin Fee",
				"tax_amount": 3000,
				"account_head": self.income_account
			}]
		}).insert(ignore_permissions=True)
		
		result = calculate_service_charges(method_name, 100000)
		
		self.assertEqual(len(result["charges"]), 1)
		self.assertEqual(result["charges"][0]["charge_amount"], 3000)
		self.assertEqual(result["total"], 3000)
		
		# Cleanup
		frappe.delete_doc("Webshop Payment Method", method_name, force=1)


if __name__ == "__main__":
	unittest.main()
