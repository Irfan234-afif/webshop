# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Subscriptions API Endpoints

Provides API endpoints for managing subscriptions (NOT subscription requests)
"""

import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import get_party


@frappe.whitelist()
def get_subscriptions(student=None, start=0, page_length=20):
	"""
	Get all subscriptions and subscription requests for the currently logged-in customer
	
	Args:
		student (str, optional): Filter by student name.
		start (int, optional): Start index for pagination. Defaults to 0.
		page_length (int, optional): Number of records to return. Defaults to 20.
	
	Returns:
		dict: Dictionary containing list of subscriptions (includes both Subscription and Subscription Request)
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))
	
	try:
		subscriptions = []
		
		# Fetch Subscription Requests (Draft status - pending approval)
		request_filters = {"customer": party.name, "docstatus": 0}  # Draft
		if student:
			request_filters["student"] = student
		
		subscription_requests = frappe.get_all(
			"Subscription Request",
			fields=[
				"name",
				"customer",
				"subscription_plan",
				"item",
				"start_date",
				"end_date",
				"notes",
				"creation",
				"modified",
				"docstatus"
			],
			filters=request_filters,
			order_by="creation desc"
		)
		
		# Process Subscription Requests
		if subscription_requests:
			# Get unique plan and item codes
			plan_names = list(set([sr.subscription_plan for sr in subscription_requests if sr.subscription_plan]))
			item_codes = list(set([sr.item for sr in subscription_requests if sr.item]))
			
			# Fetch plan details
			plans_data = {}
			if plan_names:
				plans = frappe.get_all(
					"Subscription Plan",
					fields=["name", "plan_name", "cost", "billing_interval", "item"],
					filters={"name": ["in", plan_names]}
				)
				plans_data = {p.name: p for p in plans}
			
			# Fetch item details
			items_data = {}
			if item_codes:
				items = frappe.get_all(
					"Item",
					fields=["name", "item_name", "image"],
					filters={"name": ["in", item_codes]}
				)
				items_data = {i.name: i for i in items}
			
			# Add subscription requests to the list
			for sr in subscription_requests:
				plan = plans_data.get(sr.subscription_plan, {})
				item = items_data.get(sr.item, {})
				
				subscriptions.append({
					"name": sr.name,
					"type": "request",  # Mark as subscription request
					"customer": sr.customer,
					"subscription_plan": sr.subscription_plan,
					"plan_name": plan.get("plan_name"),
					"item": sr.item,
					"item_name": item.get("item_name"),
					"start_date": sr.start_date,
					"end_date": sr.end_date,
					"status": "Draft",
					"image": item.get("image"),
					"cost": plan.get("cost"),
					"billing_interval": plan.get("billing_interval"),
					"creation": sr.creation,
					"modified": sr.modified,
					"notes": sr.notes
				})
		
		# Fetch actual Subscriptions
		subscription_filters = {"party": party.name, "party_type": "Customer"}
		if student:
			subscription_filters["student"] = student
		
		actual_subscriptions = frappe.get_all(
			"Subscription",
			fields=[
				"name",
				"party",
				"start_date",
				"end_date",
				"status",
				"current_invoice_start",
				"current_invoice_end",
				"creation",
				"modified"
			],
			filters=subscription_filters,
			order_by="creation desc"
		)
		
		# Get plan details from child table
		if actual_subscriptions:
			subscription_names = [s.name for s in actual_subscriptions]
			
			# Get subscription plan details (child table)
			plan_details = frappe.get_all(
				"Subscription Plan Detail",
				fields=["parent", "plan", "qty"],
				filters={"parent": ["in", subscription_names]}
			)
			
			# Group plans by subscription
			plans_by_subscription = {}
			for pd in plan_details:
				if pd.parent not in plans_by_subscription:
					plans_by_subscription[pd.parent] = []
				plans_by_subscription[pd.parent].append(pd.plan)
			
			# Get unique plan names
			all_plan_names = list(set([pd.plan for pd in plan_details if pd.plan]))
			
			# Fetch plan details
			plans_data = {}
			if all_plan_names:
				plans = frappe.get_all(
					"Subscription Plan",
					fields=["name", "plan_name", "cost", "billing_interval", "item"],
					filters={"name": ["in", all_plan_names]}
				)
				plans_data = {p.name: p for p in plans}
			
			# Get item details from plans
			item_codes = list(set([p.get("item") for p in plans_data.values() if p.get("item")]))
			items_data = {}
			if item_codes:
				items = frappe.get_all(
					"Item",
					fields=["name", "item_name", "image"],
					filters={"name": ["in", item_codes]}
				)
				items_data = {i.name: i for i in items}
			
			# Process subscriptions
			for sub in actual_subscriptions:
				# Get first plan for this subscription
				sub_plans = plans_by_subscription.get(sub.name, [])
				first_plan_name = sub_plans[0] if sub_plans else None
				plan = plans_data.get(first_plan_name, {}) if first_plan_name else {}
				item_code = plan.get("item")
				item = items_data.get(item_code, {}) if item_code else {}
				
				subscriptions.append({
					"name": sub.name,
					"type": "subscription",  # Mark as actual subscription
					"customer": sub.party,
					"subscription_plan": first_plan_name,
					"plan_name": plan.get("plan_name"),
					"item": item_code,
					"item_name": item.get("item_name"),
					"start_date": sub.start_date,
					"end_date": sub.end_date,
					"status": sub.status,
					"image": item.get("image"),
					"cost": plan.get("cost"),
					"billing_interval": plan.get("billing_interval"),
					"creation": sub.creation,
					"modified": sub.modified
				})
		
		# Sort all subscriptions by creation date (newest first)
		subscriptions.sort(key=lambda x: x.get("creation", ""), reverse=True)
		
		# Apply pagination
		total_count = len(subscriptions)
		start_idx = int(start)
		end_idx = start_idx + int(page_length)
		paginated_subscriptions = subscriptions[start_idx:end_idx]
		
		return {
			"subscriptions": paginated_subscriptions,
			"total": total_count
		}
	
	except Exception as e:
		frappe.log_error(f"Error fetching subscriptions: {str(e)}")
		frappe.throw(_("Error fetching subscriptions"), title=_("Error"))
