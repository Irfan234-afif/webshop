import frappe
from frappe.utils import add_days, add_months, add_years, getdate, nowdate

def validate_subscription_dates(doc, method=None):
	"""
	Auto-calculates service_start_date and service_end_date for Subscription Items.
	Triggered on Sales Order validate.
	"""
	for item in doc.items:
		if item.get("is_subscription_item") and item.get("subscription_plan"):
			# Default Start Date to Transaction Date (or Today)
			if not item.get("service_start_date"):
				item.service_start_date = doc.transaction_date or nowdate()

			# Calculate End Date based on Plan
			plan = frappe.get_doc("Subscription Plan", item.subscription_plan)
			
			if plan.billing_interval == "Day":
				item.service_end_date = add_days(item.service_start_date, plan.billing_interval_count)
			elif plan.billing_interval == "Week":
				item.service_end_date = add_days(item.service_start_date, plan.billing_interval_count * 7)
			elif plan.billing_interval == "Month":
				item.service_end_date = add_months(item.service_start_date, plan.billing_interval_count)
			elif plan.billing_interval == "Year":
				item.service_end_date = add_years(item.service_start_date, plan.billing_interval_count)
			
			# Adjust end date to be inclusive (e.g., 1st Jan to 31st Jan is 1 month)
			# Standard expectation: 1 Month from 1st Jan is 1st Feb. Coverage is until 31st Jan.
			# So we subtract 1 day from the calculated date.
			item.service_end_date = add_days(item.service_end_date, -1)

def process_subscription_order(doc, method=None):
	"""
	Creates Active Subscription(s) ONLY IF Sales Order is fully paid.
	Triggered on Sales Order on_submit (if already paid) 
	AND Payment Entry on_submit (if deferred payment).
	"""
	# Strict Payment Check
	# We considered "Paid" if advance_paid >= grand_total
	# Note: doc.status might not be 'Completed' yet if not delivered.
	# But advance_paid relies on Payment Entries.
	
	is_paid = (doc.advance_paid or 0) >= doc.grand_total
	if not is_paid:
		return

	# Group items by calculated start_date
	# Start Date depends on Plan.billing_timing:
	# Pre-Paid -> Service End Date + 1
	# Post-Paid -> Service Start Date (Immediate)
	items_by_start_date = {}
	
	for item in doc.items:
		if item.get("is_subscription_item") and item.get("subscription_plan"):
			if not item.get("service_end_date") or not item.get("service_start_date"):
				continue
				
			# Fetch Plan configuration
			# We use cached value for performance
			billing_timing = frappe.get_cached_value("Subscription Plan", item.subscription_plan, "billing_timing")
			
			if billing_timing == "Post-Paid":
				start_date = getdate(item.service_start_date)
			else:
				# Default / Pre-Paid
				start_date = add_days(getdate(item.service_end_date), 1)

			if start_date not in items_by_start_date:
				items_by_start_date[start_date] = []
			items_by_start_date[start_date].append(item)

	for start_date, items in items_by_start_date.items():
		# All items in this group share the same start_date logic
		# We can assume they share the same billing timing if we grouped strictly, 
		# but strictly speaking items could have different plans. 
		# However, our grouping logic above implicitly groups by timing too (Start Date vs End+1).
		# Let's peek at the first item's plan to determine the timing for the subscription doc.
		first_item = items[0]
		billing_timing = frappe.get_cached_value("Subscription Plan", first_item.subscription_plan, "billing_timing")
		
		create_subscription_for_group(doc, items, start_date, billing_timing)

def create_subscription_for_group(sales_order, items, start_date, billing_timing="Pre-Paid"):
	subscription_start_date = start_date

	if frappe.db.exists("Subscription", {
		"party": sales_order.customer,
		"sales_order_ref": sales_order.name,
		"start_date": subscription_start_date
	}):
		return

	subscription = frappe.new_doc("Subscription")
	subscription.party_type = "Customer"
	subscription.party = sales_order.customer
	subscription.sales_order_ref = sales_order.name
	subscription.start_date = subscription_start_date
	
	# Map Billing Timing to Invoice Generation
	if billing_timing == "Post-Paid":
		subscription.generate_invoice_at = "End of the current subscription period"
	else:
		subscription.generate_invoice_at = "Beginning of the current subscription period"
	
	for item in items:
		subscription.append("plans", {
			"plan": item.subscription_plan,
			"qty": item.qty
		})

	subscription.save(ignore_permissions=True)
	if subscription.docstatus == 0:
		subscription.submit()

def process_payment_entry(doc, method=None):
	"""
	Triggered on Payment Entry on_submit.
	Checks if the payment is linked to a Sales Order and if that SO is now fully paid.
	If so, triggers subscription creation.
	"""
	if doc.docstatus != 1:
		return

	if not doc.references:
		return

	for ref in doc.references:
		if ref.reference_doctype == "Sales Order" and ref.reference_name:
			# Fetch the fresh Sales Order to get updated advance_paid
			so = frappe.get_doc("Sales Order", ref.reference_name)
			
			# We must re-trigger the logic explicitly
			process_subscription_order(so)
