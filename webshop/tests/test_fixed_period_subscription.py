# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, getdate, nowdate

from erpnext.accounts.doctype.subscription.test_subscription import create_plan


class TestFixedPeriodSubscription(FrappeTestCase):
	"""Test cases for fixed period subscription feature"""

	def setUp(self):
		"""Set up test data"""
		# Create required test items for subscription plans
		self._create_test_items()
		
		# Create test customer if not exists
		if not frappe.db.exists("Customer", "_Test Customer Fixed Period"):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": "_Test Customer Fixed Period",
					"customer_type": "Individual",
					"customer_group": "Individual",
					"territory": "All Territories",
				}
			).insert(ignore_permissions=True)

	def _create_test_items(self):
		"""Create test items required by subscription plans"""
		# ERPNext create_plan helper expects _Test Non Stock Item
		if not frappe.db.exists("Item", "_Test Non Stock Item"):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": "_Test Non Stock Item",
					"item_name": "_Test Non Stock Item",
					"item_group": "Products",
					"stock_uom": "Nos",
					"is_stock_item": 0,
				}
			).insert(ignore_permissions=True)

	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()

	def _create_plan_with_fixed_period(self, **kwargs):
		"""Helper to create subscription plan and return the document"""
		plan_name = kwargs.get("plan_name", f"_Test Fixed Period Plan {frappe.generate_hash(length=5)}")
		
		# Use create_plan from ERPNext (doesn't return doc)
		create_plan(
			plan_name=plan_name,
			interval=kwargs.get("interval", "Day"),
			interval_count=kwargs.get("interval_count", 1),
		)
		
		# Get and update the plan
		plan = frappe.get_doc("Subscription Plan", plan_name)
		plan.use_fixed_period = kwargs.get("use_fixed_period", 1)
		plan.save()
		
		return plan

	def test_fixed_period_subscription_invoice_end_date(self):
		"""
		Test that fixed period subscription uses end_date as current_invoice_end
		instead of calculating from billing interval
		"""
		# Create a subscription plan with use_fixed_period enabled
		plan = self._create_plan_with_fixed_period(use_fixed_period=1)
		
		# Create subscription with specific start and end dates
		start_date = "2025-12-01"
		end_date = "2025-12-25"
		
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": start_date,
				"end_date": end_date,
				"generate_invoice_at": "End of the current subscription period",
				"plans": [{"plan": plan.name, "qty": 1}],
			}
		)
		subscription.insert()
		
		# Verify that current_invoice_end is the subscription end_date
		# Not calculated from billing interval (which would be start_date + 0 days = start_date)
		self.assertEqual(
			getdate(subscription.current_invoice_start),
			getdate(start_date),
			"Invoice start should be subscription start date",
		)
		self.assertEqual(
			getdate(subscription.current_invoice_end),
			getdate(end_date),
			"Invoice end should be subscription end date (fixed period)",
		)

	def test_fixed_period_requires_end_date(self):
		"""
		Test that fixed period subscription requires end_date to be set
		"""
		# Create a subscription plan with use_fixed_period enabled
		plan = self._create_plan_with_fixed_period(use_fixed_period=1)
		
		# Create subscription without end_date
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": nowdate(),
				# No end_date
				"generate_invoice_at": "End of the current subscription period",
				"plans": [{"plan": plan.name, "qty": 1}],
			}
		)
		
		# Should raise validation error
		self.assertRaises(frappe.ValidationError, subscription.insert)

	def test_fixed_period_end_date_after_start(self):
		"""
		Test that fixed period subscription end_date must be after start_date
		"""
		# Create a subscription plan with use_fixed_period enabled
		plan = self._create_plan_with_fixed_period(use_fixed_period=1)
		
		# Create subscription with end_date before start_date
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": "2025-12-25",
				"end_date": "2025-12-01",  # Before start date
				"generate_invoice_at": "End of the current subscription period",
				"plans": [{"plan": plan.name, "qty": 1}],
			}
		)
		
		# Should raise validation error
		self.assertRaises(frappe.ValidationError, subscription.insert)

	def test_regular_subscription_still_works(self):
		"""
		Test that regular subscriptions (without fixed period) still work as expected
		"""
		# Create a regular subscription plan (use_fixed_period = 0)
		plan = self._create_plan_with_fixed_period(
			interval="Month",
			interval_count=1,
			use_fixed_period=0
		)
		
		# Create subscription
		start_date = "2025-12-01"
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": start_date,
				"generate_invoice_at": "End of the current subscription period",
				"plans": [{"plan": plan.name, "qty": 1}],
			}
		)
		subscription.insert()
		
		# Verify that current_invoice_end is calculated from billing interval
		# (1 month from start = 2025-12-31)
		self.assertEqual(
			getdate(subscription.current_invoice_start), getdate("2025-12-01")
		)
		self.assertEqual(
			getdate(subscription.current_invoice_end), getdate("2025-12-31")
		)

	def test_fixed_period_backdate_subscription(self):
		"""
		Test creating a backdate fixed period subscription (the original use case)
		"""
		# Create a subscription plan with use_fixed_period enabled
		plan = self._create_plan_with_fixed_period(use_fixed_period=1)
		
		# Create backdate subscription (1-25 Dec when today is 30 Dec)
		start_date = "2025-12-01"
		end_date = "2025-12-25"
		
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": start_date,
				"end_date": end_date,
				"generate_invoice_at": "End of the current subscription period",
				"plans": [{"plan": plan.name, "qty": 1}],
			}
		)
		subscription.insert()
		
		# Verify invoice dates
		self.assertEqual(getdate(subscription.current_invoice_start), getdate(start_date))
		self.assertEqual(getdate(subscription.current_invoice_end), getdate(end_date))
		
		# Verify that we can process and generate invoice
		subscription.process(posting_date=end_date)
		
		# Check that invoice was created with correct dates
		invoice = subscription.get_current_invoice()
		self.assertIsNotNone(invoice, "Invoice should be created")
		self.assertEqual(getdate(invoice.from_date), getdate(start_date))
		self.assertEqual(getdate(invoice.to_date), getdate(end_date))

	def test_mixed_plans_uses_fixed_period(self):
		"""
		Test that if any plan in subscription uses fixed period, the feature is enabled
		"""
		# Create one fixed period plan and one regular plan
		fixed_plan = self._create_plan_with_fixed_period(
			plan_name=f"_Test Fixed Plan {frappe.generate_hash(length=5)}",
			use_fixed_period=1
		)
		
		regular_plan = self._create_plan_with_fixed_period(
			plan_name=f"_Test Regular Plan {frappe.generate_hash(length=5)}",
			interval="Day",
			interval_count=30,
			use_fixed_period=0
		)
		
		# Create subscription with both plans
		start_date = "2025-12-01"
		end_date = "2025-12-25"
		
		subscription = frappe.get_doc(
			{
				"doctype": "Subscription",
				"party_type": "Customer",
				"party": "_Test Customer Fixed Period",
				"start_date": start_date,
				"end_date": end_date,
				"generate_invoice_at": "End of the current subscription period",
				"plans": [
					{"plan": fixed_plan.name, "qty": 1},
					{"plan": regular_plan.name, "qty": 1},
				],
			}
		)
		subscription.insert()
		
		# Should use fixed period behavior (because one plan has it enabled)
		self.assertEqual(getdate(subscription.current_invoice_end), getdate(end_date))
