# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
import unittest
from frappe.utils import add_days, add_months, nowdate, getdate, date_diff


class TestSubscriptionRequest(unittest.TestCase):
	"""Test Subscription Request DocType - Core Logic Tests"""
	
	@classmethod
	def setUpClass(cls):
		"""Setup test data once for all tests"""
		# Use ERPNext's standard test customer (already exists with proper setup)
		# No need to create, it's loaded by ERPNext test framework
		
		# Create Pre-Paid subscription plan
		if not frappe.db.exists("Subscription Plan", "_Test Pre-Paid Monthly"):
			plan = frappe.get_doc({
				"doctype": "Subscription Plan",
				"plan_name": "_Test Pre-Paid Monthly",
				"item": "_Test Item",
				"price_determination": "Fixed Rate",
				"billing_interval": "Month",
				"billing_interval_count": 1,
				"billing_timing": "Pre-Paid",
				"cost": 1000,
				"currency": "INR"
			})
			plan.insert(ignore_permissions=True)
			frappe.db.commit()
		
		# Create Post-Paid subscription plan
		if not frappe.db.exists("Subscription Plan", "_Test Post-Paid Daily"):
			plan = frappe.get_doc({
				"doctype": "Subscription Plan",
				"plan_name": "_Test Post-Paid Daily",
				"item": "_Test Item",
				"price_determination": "Fixed Rate",
				"billing_interval": "Day",
				"billing_interval_count": 1,
				"billing_timing": "Post-Paid",
				"cost": 100,
				"currency": "INR"
			})
			plan.insert(ignore_permissions=True)
			frappe.db.commit()
	
	def tearDown(self):
		"""Cleanup after each test"""
		frappe.db.rollback()
	
	def test_calculate_effective_days_without_holidays(self):
		"""Test effective days calculation without holiday list"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"start_date": "2026-03-01",
			"end_date": "2026-03-10"
		})
		
		effective_days = sub_req.calculate_effective_days()
		
		# 9 days (date_diff between Jan 1 and Jan 10)
		expected_days = date_diff("2026-03-10", "2026-03-01")
		self.assertEqual(effective_days, expected_days)
	
	def test_calculate_effective_days_with_same_dates(self):
		"""Test effective days when start and end are same"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"start_date": "2026-03-01",
			"end_date": "2026-03-01"
		})
		
		effective_days = sub_req.calculate_effective_days()
		self.assertEqual(effective_days, 0)
	
	def test_calculate_effective_days_returns_zero_when_no_dates(self):
		"""Test that effective days returns 0 when dates are missing"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request"
		})
		
		effective_days = sub_req.calculate_effective_days()
		self.assertEqual(effective_days, 0)
	
	def test_end_date_preserved_if_manually_set(self):
		"""Test that manually set end_date is not overwritten"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"start_date": "2026-03-01",
			"end_date": "2026-03-01"
		})
		
		# Call calculate_end_date
		sub_req.calculate_end_date()
		
		# Should not change
		self.assertEqual(getdate(sub_req.end_date), getdate("2026-03-01"))
	
	def test_effective_days_calculation_with_30_days(self):
		"""Test effective days for typical monthly subscription"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"start_date": "2026-03-01",
			"end_date": "2026-03-31"
		})
		
		effective_days = sub_req.calculate_effective_days()
		self.assertEqual(effective_days, 30)
	
	def test_effective_days_calculation_with_one_year(self):
		"""Test effective days for yearly subscription"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"start_date": "2026-03-01",
			"end_date": "2027-01-01"
		})
		
		effective_days = sub_req.calculate_effective_days()
		self.assertEqual(effective_days, 365)
	
	def test_create_prepaid_subscription_with_dynamic_number_of_days(self):
		"""Test Pre-Paid subscription creation with dynamic number_of_days"""
		# Create subscription request with start date 7 days in future
		future_start = add_days(nowdate(), 7)
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": "_Test Customer",
			"subscription_plan": "_Test Pre-Paid Monthly",
			"start_date": future_start,
			"company": "_Test Company"  # Required for currency validation
		})
		sub_req.insert(ignore_permissions=True)
		sub_req.submit()
		
		# Verify subscription was created
		self.assertIsNotNone(sub_req.subscription_ref)
		self.assertTrue(frappe.db.exists("Subscription", sub_req.subscription_ref))
		
		# Get created subscription
		subscription = frappe.get_doc("Subscription", sub_req.subscription_ref)
		
		# Verify dynamic number_of_days calculation
		expected_days = date_diff(future_start, nowdate())
		self.assertEqual(subscription.number_of_days, expected_days)
		self.assertEqual(subscription.generate_invoice_at, "Days before the current subscription period")
		
		# Verify invoice was auto-generated for Pre-Paid
		invoices = frappe.get_all("Sales Invoice", filters={"subscription": subscription.name})
		self.assertGreater(len(invoices), 0, "Invoice should be auto-generated for Pre-Paid subscription")
		
		# Cleanup
		frappe.delete_doc("Subscription", subscription.name, force=1)
	
	def test_create_postpaid_subscription_without_auto_invoice(self):
		"""Test Post-Paid subscription does not auto-generate invoice"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": "_Test Customer",
			"subscription_plan": "_Test Post-Paid Daily",
			"start_date": nowdate(),
			"end_date": add_days(nowdate(), 30),
			"company": "_Test Company"  # Required for currency validation
		})
		sub_req.insert(ignore_permissions=True)
		sub_req.submit()
		
		# Verify subscription was created
		self.assertIsNotNone(sub_req.subscription_ref)
		self.assertTrue(frappe.db.exists("Subscription", sub_req.subscription_ref))
		
		# Get created subscription
		subscription = frappe.get_doc("Subscription", sub_req.subscription_ref)
		
		# Verify Post-Paid settings
		self.assertEqual(subscription.generate_invoice_at, "End of the current subscription period")
		
		# Verify NO invoice was auto-generated for Post-Paid
		invoices = frappe.get_all("Sales Invoice", filters={"subscription": subscription.name})
		self.assertEqual(len(invoices), 0, "Invoice should NOT be auto-generated for Post-Paid subscription")
		
		# Cleanup
		frappe.delete_doc("Subscription", subscription.name, force=1)

	def test_days_populated_without_holidays(self):
		"""Test that days child table is populated with all dates when no holiday list"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": "_Test Customer",
			"subscription_plan": "_Test Post-Paid Daily",
			"start_date": "2026-03-01",
			"end_date": "2026-03-05",
			"company": "_Test Company"
		})
		sub_req.insert(ignore_permissions=True)
		
		# Should have 5 days (Jan 1, 2, 3, 4, 5)
		self.assertEqual(len(sub_req.days), 5)
		
		# Verify dates
		dates = [getdate(d.date) for d in sub_req.days]
		self.assertEqual(dates[0], getdate("2026-03-01"))
		self.assertEqual(dates[-1], getdate("2026-03-05"))
	
	def test_effective_days_matches_days_count(self):
		"""Test that effective_days equals count of non-excluded days in child table"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": "_Test Customer",
			"subscription_plan": "_Test Post-Paid Daily",
			"start_date": "2026-03-01",
			"end_date": "2026-03-10",
			"company": "_Test Company"
		})
		sub_req.insert(ignore_permissions=True)
		
		# effective_days should equal number of days in child table
		self.assertEqual(sub_req.effective_days, len(sub_req.days))
	
	def test_postpaid_qty_uses_days_count(self):
		"""Test Post-Paid subscription quantity uses days child table count"""
		sub_req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": "_Test Customer",
			"subscription_plan": "_Test Post-Paid Daily",
			"start_date": "2026-03-01",
			"end_date": "2026-03-10",
			"company": "_Test Company"
		})
		sub_req.insert(ignore_permissions=True)
		sub_req.submit()
		
		# Get created subscription
		subscription = frappe.get_doc("Subscription", sub_req.subscription_ref)
		
		# Quantity should match days count
		expected_qty = len([d for d in sub_req.days if not d.is_excluded])
		self.assertEqual(subscription.plans[0].qty, expected_qty)
		
		# Cleanup
		frappe.delete_doc("Subscription", subscription.name, force=1)
