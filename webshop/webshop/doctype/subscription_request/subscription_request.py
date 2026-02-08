# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate, add_days

class SubscriptionRequest(Document):
	def validate(self):
		self.calculate_end_date()
		self.update_holiday_list()
		self.populate_days()
		self.update_effective_days()
	
	def update_holiday_list(self):
		if not self.holiday_list:
			self.holiday_list = frappe.db.get_value("Holiday List", {"from_date": ("<", self.start_date), "to_date": (">", self.end_date)}, "name")
	
	def update_effective_days(self):
		"""Update effective_days field based on active days in child table"""
		if self.days:
			# Count non-excluded days from child table
			self.effective_days = len([d for d in self.days if not d.is_excluded])
		elif self.start_date and self.end_date:
			# Fallback to calculation if child table not populated yet
			self.effective_days = self.calculate_effective_days()
		else:
			self.effective_days = 0
	
	def populate_days(self):
		"""
		Populate days child table with active days between start_date and end_date,
		excluding holidays from the selected holiday list.
		"""
		if not self.start_date or not self.end_date:
			return
		
		# Get holidays from holiday list
		holiday_dates = set()
		if self.holiday_list:
			holidays = frappe.db.get_all(
				"Holiday",
				filters={
					"parent": self.holiday_list,
					"holiday_date": ["between", [self.start_date, self.end_date]]
				},
				pluck="holiday_date"
			)
			holiday_dates = set(getdate(d) for d in holidays)
		
		# Clear existing days
		self.days = []
		
		# Add all dates except holidays
		current = getdate(self.start_date)
		end = getdate(self.end_date)
		while current <= end:
			if current not in holiday_dates:
				self.append("days", {
					"date": current,
					"description": "Hari Aktif",
					"is_excluded": 0
				})
			current = add_days(current, 1)
	
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
		"""Auto-calculate end_date as the last day of the start month"""
		if not self.subscription_plan or not self.start_date:
			return
		
		if self.end_date:
			return
		
		# Get the last day of the start month
		from frappe.utils import get_last_day
		self.end_date = get_last_day(self.start_date)

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
			# For consumption-based (post-paid, day-based), use count of active days from child table
			active_days = len([d for d in self.days if not d.is_excluded]) if self.days else 0
			qty = active_days or self.calculate_effective_days() or 1

		# Create Subscription
		subscription = frappe.new_doc("Subscription")
		subscription.party_type = "Customer"
		subscription.party = self.customer
		subscription.company = self.company if self.get("company") else frappe.defaults.get_user_default("Company")
		subscription.days_until_due = 1
		
		# Copy student if available
		if self.student:
			subscription.student = self.student
		
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
		
		# Copy days child table from Subscription Request to Subscription
		if self.days:
			for day in self.days:
				subscription.append("days", {
					"date": day.date,
					"description": day.description,
					"is_excluded": day.is_excluded
				})
			subscription.save()
		
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


@frappe.whitelist()
def get_estimate_cost(item_code, start_date):
	# Get the last day of the start month
	from frappe.utils import get_last_day
	end_date = get_last_day(start_date)

	plan = frappe.db.get_value("Item", item_code, "subscription_plan")
	if not plan:
		plan_name = frappe.db.get_value("Subscription Plan", {"item": item_code})
		if not plan_name:
			frappe.throw(_("This item is not configured as a Subscription Plan."))
	else:
		plan_name = plan
	
	plan_details = frappe.get_doc("Subscription Plan", plan_name)

	# Get holiday list
	holiday_list = frappe.db.get_value("Holiday List", {"from_date": ("<", start_date), "to_date": (">", end_date)}, "name")
	holidays = frappe.db.count("Holiday", {"parent": holiday_list, "holiday_date": ("between", (start_date, end_date))})

	# Calculate effective days
	from frappe.utils import date_diff
	effective_days = date_diff(end_date, start_date) - holidays

	# Calculate cost
	if plan_details.billing_timing == "Post-Paid" and plan_details.billing_interval == "Day":
		cost = plan_details.cost * effective_days
	else:
		effective_days = 0
		cost = plan_details.cost
	
	return {
		"cost": cost,
		"effective_days": effective_days,
		"end_date": end_date,
		"subscription_plan": plan_details,
	}