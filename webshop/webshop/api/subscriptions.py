# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Subscriptions API Endpoints

Provides API endpoints for managing subscriptions and subscription requests
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
		dict: Dictionary containing list of subscriptions and requests
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))
	
	try:
		subscriptions = []
		
		# Fetch Subscription Requests
		# Show all requests, but mark as "Active" when they have a subscription_ref (approved)
		request_filters = {"customer": party.name}
		if student:
			# For subscription requests, we need to check if the item relates to the student
			# This is a simplified approach - you may need to adjust based on your schema
			pass
		
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
				"docstatus",
				"subscription_ref",
				"creation",
				"modified"
			],
			filters=request_filters,
			order_by="creation desc",
			start=0,  # Get all for now, we'll combine and paginate later
			page_length=100
		)
		
		# Get plan details for requests
		if subscription_requests:
			plan_names = list(set([sr.subscription_plan for sr in subscription_requests if sr.subscription_plan]))
			item_codes = list(set([sr.item for sr in subscription_requests if sr.item]))
			
			# Fetch plan details
			plans_data = {}
			if plan_names:
				plans = frappe.get_all(
					"Subscription Plan",
					fields=["name", "plan_name", "cost", "billing_interval"],
					filters={"name": ["in", plan_names]}
				)
				plans_data = {p.name: p for p in plans}
			
			# Fetch item details (name and image)
			items_data = {}
			if item_codes:
				items = frappe.get_all(
					"Item",
					fields=["name", "item_name", "image"],
					filters={"name": ["in", item_codes]}
				)
				items_data = {i.name: i for i in items}
			
			# Process subscription requests
			for sr in subscription_requests:
				plan = plans_data.get(sr.subscription_plan, {})
				item = items_data.get(sr.item, {})
				
				# Determine status
				# If has subscription_ref, it means approved and should show as "Active"
				if sr.subscription_ref:
					status = "Active"
				elif sr.docstatus == 0:
					status = "Draft"
				elif sr.docstatus == 1:
					status = "Submitted"
				else:
					status = "Cancelled"
				
				subscriptions.append({
					"name": sr.name,
					"type": "request",
					"customer": sr.customer,
					"subscription_plan": sr.subscription_plan,
					"plan_name": plan.get("plan_name"),
					"item": sr.item,
					"item_name": item.get("item_name"),
					"start_date": sr.start_date,
					"end_date": sr.end_date,
					"notes": sr.notes,
					"status": status,
					"docstatus": sr.docstatus,
					"subscription_ref": sr.subscription_ref,
					"image": item.get("image"),
					"cost": plan.get("cost"),
					"billing_interval": plan.get("billing_interval"),
					"creation": sr.creation,
					"modified": sr.modified
				})
		
		# Sort by creation date (newest first)
		subscriptions.sort(key=lambda x: x.get("creation", ""), reverse=True)
		
		# Apply pagination
		start = int(start)
		page_length = int(page_length)
		paginated_subscriptions = subscriptions[start:start + page_length]
		
		return {
			"subscriptions": paginated_subscriptions,
			"total": len(subscriptions)
		}
	
	except Exception as e:
		frappe.log_error(f"Error fetching subscriptions: {str(e)}")
		frappe.throw(_("Error fetching subscriptions"), title=_("Error"))
