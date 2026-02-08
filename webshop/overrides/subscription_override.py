# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate

# Import original Subscription class
from erpnext.accounts.doctype.subscription.subscription import Subscription


class CustomSubscription(Subscription):
	"""
	Extended Subscription class to support fixed-period subscriptions.
	
	This override adds support for subscriptions with a fixed end date
	(e.g., catering service from 1-25 Dec) where the invoice end date
	should be the subscription's end_date, not calculated from billing interval.
	"""

	def get_current_invoice_end(self, date=None):
		"""
		Override to support fixed period subscriptions.
		
		If any plan in the subscription has 'use_fixed_period' enabled,
		and the subscription has an end_date, use that as the invoice end
		instead of calculating from billing interval.
		
		Args:
			date: The start date for calculating invoice end
			
		Returns:
			The invoice end date
		"""
		# Check if this subscription uses fixed period
		if self._uses_fixed_period() and self.end_date:
			# For fixed period, if the date is before or on end_date
			# return the subscription's end_date
			if not date or getdate(date) <= getdate(self.end_date):
				return self.end_date
		
		# Otherwise, use the original logic
		return super(CustomSubscription, self).get_current_invoice_end(date)

	def _uses_fixed_period(self):
		"""
		Check if any plan in this subscription uses fixed period mode.
		
		Returns:
			bool: True if any plan has use_fixed_period enabled
		"""
		for plan in self.plans:
			# Get the plan document (cached for performance)
			plan_doc = frappe.get_cached_doc("Subscription Plan", plan.plan)
			
			# Check if the custom field exists and is enabled
			if plan_doc.get("use_fixed_period"):
				return True
		
		return False

	def validate_end_date(self):
		"""
		Override validate_end_date to skip validation for fixed period subscriptions.
		
		ERPNext's default validation requires end_date to be after the calculated
		billing cycle end date. For fixed period subscriptions, we want to allow
		any end_date (even shorter than one billing interval).
		"""
		# Skip validation if using fixed period
		if self._uses_fixed_period():
			return
		
		# Otherwise, use the original validation
		super(CustomSubscription, self).validate_end_date()

	def validate(self):
		"""
		Extended validation for fixed period subscriptions.
		"""
		# Call original validate
		super(CustomSubscription, self).validate()
		
		# Auto-update qty from days child table
		self._update_qty_from_days()
		
		# Additional validation for fixed period
		if self._uses_fixed_period():
			if not self.end_date:
				frappe.throw(
					_("Subscription End Date is mandatory when using Fixed Period subscription plan")
				)
			
			if getdate(self.end_date) <= getdate(self.start_date):
				frappe.throw(_("Subscription End Date must be after Start Date"))
	
	def _update_qty_from_days(self):
		"""
		Auto-update subscription plan qty based on active days in child table.
		Only applies to Post-Paid Day-based plans.
		"""
		# Check if days child table exists and has data
		if not self.get("days"):
			return
		
		# Count active (non-excluded) days
		active_days = len([d for d in self.days if not d.is_excluded])
		
		if active_days <= 0:
			return
		
		# Update qty for Post-Paid Day-based plans
		for plan in self.plans:
			plan_doc = frappe.get_cached_doc("Subscription Plan", plan.plan)
			
			if plan_doc.billing_timing == "Post-Paid" and plan_doc.billing_interval == "Day":
				plan.qty = active_days

