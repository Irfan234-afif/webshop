# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class SubscriptionRequest(Document):
	def validate(self):
		self.calculate_end_date()
		self.update_holiday_list()
		self.update_effective_days()
	
	def update_holiday_list(self):
		if not self.holiday_list:
			self.holiday_list = frappe.db.get_value("Holiday List", {"from_date": ("<", self.start_date), "to_date": (">", self.end_date)}, "name")
	
	def update_effective_days(self):
		"""Update effective_days field based on start_date, end_date, and holiday_list"""
		if self.start_date and self.end_date:
			self.effective_days = self.calculate_effective_days()
	
	def calculate_effective_days(self):
		"""
		Calculate effective days between start_date and end_date, excluding holidays.
		Returns:
			int: Number of effective working days
		"""
		if not self.start_date or not self.end_date:
			return 0
		
		from frappe.utils import date_diff, getdate
		
		# Get total days between start and end date (inclusive)
		total_days = date_diff(self.end_date, self.start_date)
		
		# Get holidays if holiday_list is specified
		holiday_count = 0
		if self.holiday_list:
			# Query holidays from Holiday List within the date range
			holidays = frappe.db.sql("""
				SELECT COUNT(*) as count
				FROM `tabHoliday`
				WHERE parent = %s
				AND holiday_date BETWEEN %s AND %s
			""", (self.holiday_list, self.start_date, self.end_date), as_dict=True)
			
			if holidays:
				holiday_count = holidays[0].count or 0
		
		# Effective days = total days - holidays
		effective_days = total_days - holiday_count
		
		return max(effective_days, 0)  # Ensure non-negative

	
	def input_validate(self):
		if not self.subscription_plan:
			frappe.throw(_("Subscription Plan is required"))
		if not self.item:
			frappe.throw(_("Item is required"))
		if not self.start_date:
			frappe.throw(_("Start Date is required"))
	
	def calculate_end_date(self):
		"""Auto-calculate end_date based on subscription plan's billing interval"""
		if not self.subscription_plan or not self.start_date:
			return
		
		if self.end_date:
			return
		
		# Fetch plan details
		plan = frappe.get_doc("Subscription Plan", self.subscription_plan)
		
		# Get billing interval from plan
		billing_interval = plan.billing_interval
		billing_interval_count = plan.billing_interval_count or 1
		
		# Convert start_date to date object
		start = getdate(self.start_date)
		
		# Calculate end_date based on interval
		from dateutil.relativedelta import relativedelta
		
		if billing_interval == "Day":
			end = start + relativedelta(days=billing_interval_count)
		elif billing_interval == "Week":
			end = start + relativedelta(weeks=billing_interval_count)
		elif billing_interval == "Month":
			end = start + relativedelta(months=billing_interval_count)
		elif billing_interval == "Year":
			end = start + relativedelta(years=billing_interval_count)
		else:
			# Default to 1 month if interval not recognized
			end = start + relativedelta(months=1)
		
		self.end_date = end

	def on_submit(self):
		self.create_subscription_from_request()

	def create_subscription_from_request(self):
		# Get plan details to check billing timing and interval
		plan_details = frappe.db.get_value(
			"Subscription Plan", 
			self.subscription_plan, 
			["billing_timing", "billing_interval"], 
			as_dict=True
		)
		
		# Determine quantity based on billing timing and interval
		qty = 1  # Default quantity
		if plan_details.billing_timing == "Post-Paid" and plan_details.billing_interval == "Day":
			# For consumption-based (post-paid, day-based), use effective days as quantity
			qty = self.calculate_effective_days() or 1

		# Create Subscription
		subscription = frappe.new_doc("Subscription")
		subscription.party_type = "Customer"
		subscription.party = self.customer
		subscription.company = self.company if self.get("company") else frappe.defaults.get_user_default("Company")
		subscription.append("plans", {
			"plan": self.subscription_plan,
			"qty": qty
		})
		subscription.start_date = self.start_date
		if self.end_date:
			subscription.end_date = self.end_date
		
		billing_timing = frappe.db.get_value("Subscription Plan", self.subscription_plan, "billing_timing")
		if billing_timing == "Post-Paid":
			subscription.generate_invoice_at = "End of the current subscription period"
		else:
			subscription.generate_invoice_at = "Days before the current subscription period"
			# Calculate number_of_days dynamically as the difference from start_date to today
			# This ensures invoice can be generated immediately on today's date
			from frappe.utils import date_diff, nowdate
			days_difference = date_diff(self.start_date, nowdate())
			subscription.number_of_days = max(days_difference, 0)  # Ensure non-negative
		
		# Submit to activate
		subscription.insert()
		
		# Link back
		self.db_set("subscription_ref", subscription.name)
		
		# Link Subscription to this Request (if field exists on Subscription, optional)
		# subscription.db_set("subscription_request", self.name) 
		
		# Trigger process() to generate invoice immediately ONLY for Pre-Paid subscriptions
		# Post-Paid subscriptions should generate invoice at the end of period
		if billing_timing == "Pre-Paid":
			try:
				subscription.process(posting_date=nowdate())
				frappe.msgprint(_("Subscription {0} created and invoice generated successfully.").format(subscription.name))
			except Exception as e:
				frappe.log_error(f"Failed to process subscription {subscription.name}: {str(e)}")
				frappe.msgprint(_("Subscription {0} created, but invoice generation encountered an issue. Please check the subscription.").format(subscription.name))
		else:
			frappe.msgprint(_("Subscription {0} created and activated.").format(subscription.name))
