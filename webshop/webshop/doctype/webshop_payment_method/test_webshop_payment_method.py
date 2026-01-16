# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from webshop.webshop.doctype.webshop_payment_method.webshop_payment_method import get_payment_method_charges


class TestWebshopPaymentMethod(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test company if not exists
		if not frappe.db.exists("Company", "_Test Company"):
			frappe.get_doc({
				"doctype": "Company",
				"company_name": "_Test Company",
				"default_currency": "IDR",
				"country": "Indonesia",
				"abbr": "_TC"
			}).insert(ignore_permissions=True)
		
		company_abbr = frappe.db.get_value("Company", "_Test Company", "abbr")
		
		# Create test account for service charges
		income_account = frappe.db.get_value("Account", {
			"company": "_Test Company",
			"root_type": "Income",
			"is_group": 0
		}, "name")
		
		if not income_account:
			# Create income account
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
		
		# Create test payment method with service charges
		self.payment_method_name = "Test Payment Method with Charges"
		
		if frappe.db.exists("Webshop Payment Method", self.payment_method_name):
			frappe.delete_doc("Webshop Payment Method", self.payment_method_name, force=1)
		
		self.payment_method = frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": self.payment_method_name,
			"title": "Test Payment with Charges",
			"description": "Test payment method",
			"payment_type": "Cash",  # Use Cash to avoid validation requirements
			"enabled": 1,
			"payment_charges": [
				{
					"charge_type": "On Net Total",
					"description": "Platform Fee (Percentage)",
					"rate": 1.5,
					"account_head": self.income_account
				},
				{
					"charge_type": "Actual",
					"description": "Admin Fee (Fixed)",
					"tax_amount": 2500,
					"account_head": self.income_account
				}
			]
		})
		self.payment_method.insert(ignore_permissions=True)
	
	def tearDown(self):
		"""Clean up test data"""
		if frappe.db.exists("Webshop Payment Method", self.payment_method_name):
			frappe.delete_doc("Webshop Payment Method", self.payment_method_name, force=1)
	
	def test_get_payment_method_charges(self):
		"""Test getting charges configuration from payment method"""
		charges = get_payment_method_charges(self.payment_method_name)
		
		self.assertEqual(len(charges), 2)
		
		# Test percentage charge
		percentage_charge = charges[0]
		self.assertEqual(percentage_charge["charge_type"], "On Net Total")
		self.assertEqual(percentage_charge["description"], "Platform Fee (Percentage)")
		self.assertEqual(percentage_charge["rate"], 1.5)
		self.assertEqual(percentage_charge["account_head"], self.income_account)
		
		# Test fixed charge
		fixed_charge = charges[1]
		self.assertEqual(fixed_charge["charge_type"], "Actual")
		self.assertEqual(fixed_charge["description"], "Admin Fee (Fixed)")
		self.assertEqual(fixed_charge["tax_amount"], 2500)
		self.assertEqual(fixed_charge["account_head"], self.income_account)
	
	def test_get_payment_method_charges_empty(self):
		"""Test getting charges from payment method without charges"""
		# Create payment method without charges
		method_name = "Test Payment Method No Charges"
		
		if frappe.db.exists("Webshop Payment Method", method_name):
			frappe.delete_doc("Webshop Payment Method", method_name, force=1)
		
		frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": method_name,
			"title": "No Charges Method",
			"payment_type": "Cash",
			"enabled": 1
		}).insert(ignore_permissions=True)
		
		charges = get_payment_method_charges(method_name)
		self.assertEqual(len(charges), 0)
		
		# Cleanup
		frappe.delete_doc("Webshop Payment Method", method_name, force=1)
	
	def test_get_payment_method_charges_nonexistent(self):
		"""Test getting charges from non-existent payment method"""
		charges = get_payment_method_charges("Non Existent Method")
		self.assertEqual(len(charges), 0)
