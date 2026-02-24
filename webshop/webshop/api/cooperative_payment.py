# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, getdate, add_days, flt

@frappe.whitelist()
def create_registration_payment_request(member_name, payment_method_type, payment_channel=None):
	"""
	Create Payment Request for cooperative registration
	"""
	member = frappe.get_doc("Cooperative Member", member_name)
	
	if member.status != "Draft":
		frappe.throw(_("Registration is already processed"))
		
	settings = frappe.get_doc("Cooperative Settings")
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)
	
	# Calculate total
	total_amount = member.total_registration_amount
	
	# Create Payment Request
	pr = frappe.new_doc("Payment Request")
	pr.payment_request_type = "Inward"
	pr.reference_doctype = "Cooperative Member"
	pr.reference_name = member.name
	pr.party_type = "Customer"
	pr.party = member.customer
	pr.party_name = member.full_name
	pr.grand_total = total_amount
	pr.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
	pr.company = settings.company
	
	# Set payment method (needed for our override)
	if hasattr(pr, 'payment_method_type'):
		pr.payment_method_type = payment_method.name
		
	if payment_method.payment_type == "Payment Gateway" and payment_channel:
		if hasattr(pr, 'payment_channel_code'):
			pr.payment_channel_code = payment_channel
			
	if hasattr(pr, 'mode_of_payment') and payment_method.mode_of_payment:
		pr.mode_of_payment = payment_method.mode_of_payment
		
	if hasattr(pr, 'payment_gateway_account') and payment_method.payment_gateway_account:
		pr.payment_gateway_account = payment_method.payment_gateway_account
		
	# Mute email
	pr.mute_email = 1
	pr.email_to = member.email or frappe.session.user
	pr.subject = f"Payment for Cooperative Registration - {member.name}"
	
	# Insert as Draft
	pr.insert(ignore_permissions=True)
	
	# Update member status
	member.status = "Pending Payment"
	member.save(ignore_permissions=True)
	
	return {"payment_request": pr.name}

def on_payment_request_submit(doc, method=None):
	"""
	Hook for Payment Request on_submit
	Handles automatic approval of cooperative members if payment is successful
	"""
	if doc.reference_doctype == "Cooperative Member":
		# Payment is completed/approved, activate member
		member = frappe.get_doc("Cooperative Member", doc.reference_name)
		if member.status != "Active":
			new_balance = flt(member.mandatory_saving_balance) + flt(member.mandatory_saving_amount)

			# Use db.set_value to bypass the Workflow engine, which would revert
			# workflow_state back to "Pending Payment" if we used doc.save()
			frappe.db.set_value("Cooperative Member", member.name, {
				"status": "Active",
				"workflow_state": "Active",
				"mandatory_saving_balance": new_balance,
			}, update_modified=False)

			# Create Mandatory Saving for this year and mark registration month as Paid
			current_month = getdate(doc.get("transaction_date") or nowdate()).month
			create_mandatory_saving_for_year(member.name, getdate(doc.get("transaction_date") or nowdate()).year, is_registration=True, start_month=current_month)

	elif doc.reference_doctype == "Mandatory Saving":
		# Payment is completed for mandatory saving months
		ms = frappe.get_doc("Mandatory Saving", doc.reference_name)
		
		# Find rows linked to this Payment Request and mark them Paid
		paid_amount = 0
		for row in ms.get("monthly_details"):
			if row.payment_request == doc.name and row.status == "Pending Payment":
				row.status = "Paid"
				row.payment_date = nowdate()
				paid_amount += flt(row.amount)
				# Write child row directly to DB
				frappe.db.set_value("Mandatory Saving Detail", row.name, {
					"status": "Paid",
					"payment_date": nowdate()
				}, update_modified=False)
		
		# Recalculate and write totals directly to DB
		ms.calculate_totals()
		frappe.db.set_value("Mandatory Saving", ms.name, {
			"total_paid": ms.total_paid,
			"total_unpaid": ms.total_unpaid
		}, update_modified=False)
		
		# Update member's mandatory saving balance
		if paid_amount > 0:
			member = frappe.get_doc("Cooperative Member", ms.cooperative_member)
			member.mandatory_saving_balance = flt(member.mandatory_saving_balance) + paid_amount
			frappe.db.set_value("Cooperative Member", member.name,
				"mandatory_saving_balance", member.mandatory_saving_balance,
				update_modified=False)

	elif doc.reference_doctype == "Voluntary Saving":
		# Payment is completed for Voluntary Saving deposit
		vs = frappe.get_doc("Voluntary Saving", doc.reference_name)
		
		# Find the Journal Entry created by this Payment Request override
		je_name = frappe.db.get_value("Journal Entry", {"cheque_no": doc.name, "docstatus": 1}, "name")
		
		# Update Voluntary Saving status
		frappe.db.set_value("Voluntary Saving", vs.name, {
			"status": "Approved",
			"payment_date": nowdate(),
			"journal_entry": je_name
		}, update_modified=False)
		
		# Update member's voluntary saving balance
		member = frappe.get_doc("Cooperative Member", vs.cooperative_member)
		member.voluntary_saving_balance = flt(member.voluntary_saving_balance) + flt(vs.amount)
		frappe.db.set_value("Cooperative Member", member.name, 
			"voluntary_saving_balance", member.voluntary_saving_balance, 
			update_modified=False)



def before_payment_request_cancel(doc, method=None):
	"""
	Hook for Payment Request before_cancel.
	Clears back-link fields that would cause Frappe's link check to
	block the cancellation of the Payment Request.
	"""
	if doc.reference_doctype == "Mandatory Saving":
		# Clear payment_request link from any Mandatory Saving Detail rows
		detail_rows = frappe.get_all(
			"Mandatory Saving Detail",
			filters={"payment_request": doc.name},
			fields=["name", "status"],
		)
		for row in detail_rows:
			new_status = "Unpaid" if row.status == "Pending Payment" else row.status
			frappe.db.set_value(
				"Mandatory Saving Detail",
				row.name,
				{"payment_request": None, "status": new_status},
				update_modified=False,
			)

	elif doc.reference_doctype == "Voluntary Saving":
		# Clear payment_request link from the Voluntary Saving doc
		if frappe.db.exists("Voluntary Saving", doc.reference_name):
			frappe.db.set_value(
				"Voluntary Saving",
				doc.reference_name,
				"payment_request",
				None,
				update_modified=False,
			)

	elif doc.reference_doctype == "Cooperative Member":
		# Reset member status back to Draft if payment is being cancelled
		if frappe.db.exists("Cooperative Member", doc.reference_name):
			member_status = frappe.db.get_value("Cooperative Member", doc.reference_name, "status")
			if member_status == "Pending Payment":
				frappe.db.set_value(
					"Cooperative Member",
					doc.reference_name,
					"status",
					"Draft",
					update_modified=False,
				)


def create_mandatory_saving_for_year(member_name, year, is_registration=False, start_month=1):
	"""
	Create Mandatory Saving record for a member for a specific year
	"""
	# Check if exists
	existing = frappe.db.exists("Mandatory Saving", {"cooperative_member": member_name, "year": year})
	if existing:
		return existing
		
	settings = frappe.get_doc("Cooperative Settings")
	member = frappe.get_doc("Cooperative Member", member_name)
	
	ms = frappe.new_doc("Mandatory Saving")
	ms.cooperative_member = member.name
	ms.year = year
	ms.amount_per_month = settings.mandatory_saving_amount
	
	# Determine which month to mark as paid if registration
	current_month = getdate().month
	
	month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
				   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
				   
	for i in range(start_month, 13):
		status = "Unpaid"
		if is_registration and i == current_month:
			status = "Paid"
			
		ms.append("monthly_details", {
			"month": i,
			"month_name": month_names[i-1],
			"amount": settings.mandatory_saving_amount,
			"status": status,
			"payment_date": nowdate() if status == "Paid" else None
		})
		
	ms.flags.ignore_permissions = True
	ms.save()
	ms.submit()
	
	return ms.name


def create_annual_mandatory_savings():
	"""
	Scheduled job: Auto-create Mandatory Saving records for the current year
	for all active cooperative members who don't already have one.
	Runs yearly (configured in hooks.py as yearly cron).
	"""
	current_year = getdate().year
	
	active_members = frappe.get_all(
		"Cooperative Member",
		filters={"status": "Active"},
		fields=["name"]
	)
	
	created = 0
	for m in active_members:
		existing = frappe.db.exists("Mandatory Saving", {"cooperative_member": m.name, "year": current_year})
		if not existing:
			create_mandatory_saving_for_year(m.name, current_year)
			created += 1
	
	if created:
		frappe.logger().info(f"Created {created} Mandatory Saving records for year {current_year}")


@frappe.whitelist()
def create_next_year_saving(member_name):
	"""
	Manual button: Create Mandatory Saving record for the next year for a specific member.
	"""
	current_year = getdate().year
	next_year = current_year + 1
	
	# Also create current year if missing
	current_result = create_mandatory_saving_for_year(member_name, current_year)
	next_result = create_mandatory_saving_for_year(member_name, next_year)
	
	return {"current_year": current_result, "next_year": next_result}

