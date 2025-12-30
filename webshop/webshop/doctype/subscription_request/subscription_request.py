# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, nowdate

class SubscriptionRequest(Document):
	def validate(self):
		self.calculate_end_date()
	
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
		# Create Subscription
		subscription = frappe.new_doc("Subscription")
		subscription.party_type = "Customer"
		subscription.party = self.customer
		subscription.append("plans", {
			"plan": self.subscription_plan,
			"qty": 1
		})
		subscription.start_date = self.start_date
		if self.end_date:
			subscription.end_date = self.end_date
		
		# Set post-paid settings (generate invoice at end of period)
		subscription.generate_invoice_at = "End of the current subscription period"
		
		# Submit to activate
		subscription.insert()
		subscription.submit()
		
		# Link back
		self.db_set("subscription_ref", subscription.name)
		
		# Link Subscription to this Request (if field exists on Subscription, optional)
		# subscription.db_set("subscription_request", self.name) 
		
		frappe.msgprint(_("Subscription {0} created and activated.").format(subscription.name))
