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

@frappe.whitelist()
def get_member_savings():
	"""
	Fetch savings data for the currently logged in cooperative member.
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to view savings"))

	member_records = frappe.get_all(
		"Cooperative Member",
		filters={"email": frappe.session.user, "status": "Active"},
		fields=["name", "mandatory_saving_balance", "voluntary_saving_balance"],
		limit=1
	)

	if not member_records:
		frappe.throw(_("Active cooperative membership not found"))

	member = member_records[0]

	# Fetch Mandatory Savings
	mandatory_savings = frappe.get_all(
		"Mandatory Saving",
		filters={"cooperative_member": member.name},
		fields=["name", "year", "amount_per_month", "total_paid", "total_unpaid"],
		order_by="year desc"
	)

	for ms in mandatory_savings:
		ms["monthly_details"] = frappe.get_all(
			"Mandatory Saving Detail",
			filters={"parent": ms.name},
			fields=["name", "month", "month_name", "amount", "status", "payment_date", "payment_request"],
			order_by="month asc"
		)

	# Fetch Voluntary Savings
	voluntary_savings = frappe.get_all(
		"Voluntary Saving",
		filters={"cooperative_member": member.name},
		fields=["name", "transaction_type", "amount", "status", "payment_date", "creation", "payment_request"],
		order_by="creation desc"
	)

	return {
		"member_name": member.name,
		"mandatory_saving_balance": member.mandatory_saving_balance,
		"voluntary_saving_balance": member.voluntary_saving_balance,
		"mandatory_savings": mandatory_savings,
		"voluntary_savings": voluntary_savings
	}

@frappe.whitelist()
def get_savings_history(page=1, page_length=20, saving_type=None, transaction_kind=None):
	"""
	Fetch unified savings transaction history for the currently logged in cooperative member.
	Combines: registration, mandatory saving payments, voluntary saving deposits/withdrawals.

	Filters:
	  saving_type: "Simpanan Pokok" | "Simpanan Wajib" | "Simpanan Sukarela"
	  transaction_kind: "Pembayaran" | "Setoran" | "Pengambilan" | "Simpanan Pokok"
	"""
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to view savings history"))

	page = int(page)
	page_length = int(page_length)

	member_records = frappe.get_all(
		"Cooperative Member",
		filters={"email": frappe.session.user, "status": "Active"},
		fields=["name", "total_registration_amount", "creation"],
		limit=1
	)

	if not member_records:
		frappe.throw(_("Active cooperative membership not found"))

	member = member_records[0]
	items = []

	def get_payment_method_label(pr_name):
		if not pr_name:
			return "-"
		pm_type = frappe.db.get_value("Payment Request", pr_name, "payment_method_type")
		if not pm_type:
			return "-"
		pm = frappe.db.get_value("Webshop Payment Method", pm_type, ["title", "payment_type"], as_dict=True)
		if not pm:
			return "-"
		return pm.title or pm.payment_type or "-"

	month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
				   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

	# A. Registration transaction (Simpanan Pokok)
	include_registration = (
		(not saving_type or saving_type == "Simpanan Pokok") and
		(not transaction_kind or transaction_kind == "Simpanan Pokok")
	)
	if include_registration:
		reg_date = getdate(member.creation)
		reg_pr = frappe.db.get_value(
			"Payment Request",
			{"reference_doctype": "Cooperative Member", "reference_name": member.name, "docstatus": 1},
			"name"
		)
		items.append({
			"date": str(reg_date),
			"type": "registration",
			"period": f"{month_names[reg_date.month - 1]} {reg_date.year}",
			"amount": flt(member.total_registration_amount),
			"due_date": None,
			"saving_type": "Simpanan Pokok",
			"transaction_kind": "Simpanan Pokok",
			"payment_date": str(reg_date),
			"payment_method": get_payment_method_label(reg_pr),
			"status": "Paid",
			"reference_doctype": "Cooperative Member",
			"reference_name": member.name,
			"payment_request": reg_pr
		})

	# B. Mandatory Saving Detail rows (Paid or Pending Payment)
	include_mandatory = (
		(not saving_type or saving_type == "Simpanan Wajib") and
		(not transaction_kind or transaction_kind == "Pembayaran")
	)
	if include_mandatory:
		mandatory_rows = frappe.db.sql("""
			SELECT msd.payment_date, msd.month, msd.month_name, msd.amount,
				   msd.status, msd.payment_request, msd.name,
				   ms.name as saving_name, ms.year
			FROM `tabMandatory Saving Detail` msd
			JOIN `tabMandatory Saving` ms ON msd.parent = ms.name
			WHERE ms.cooperative_member = %s AND msd.status IN ('Paid', 'Pending Payment')
			ORDER BY ms.year DESC, msd.month DESC
		""", (member.name,), as_dict=True)

		for row in mandatory_rows:
			date = str(row.payment_date) if row.payment_date else f"{row.year}-{int(row.month):02d}-01"
			# Due date is last day of the month
			import calendar
			last_day = calendar.monthrange(int(row.year), int(row.month))[1]
			due_date_str = f"{row.year}-{int(row.month):02d}-{last_day:02d}"
			items.append({
				"date": date,
				"type": "mandatory",
				"period": f"{row.month_name} {row.year}",
				"amount": flt(row.amount),
				"due_date": due_date_str,
				"saving_type": "Simpanan Wajib",
				"transaction_kind": "Pembayaran",
				"payment_date": str(row.payment_date) if row.payment_date else None,
				"payment_method": get_payment_method_label(row.payment_request),
				"status": row.status,
				"reference_doctype": "Mandatory Saving",
				"reference_name": row.saving_name,
				"payment_request": row.payment_request
			})

	# C. Voluntary Saving records (exclude Draft docstatus)
	include_voluntary_deposit = (
		(not saving_type or saving_type == "Simpanan Sukarela") and
		(not transaction_kind or transaction_kind == "Setoran")
	)
	include_voluntary_withdrawal = (
		(not saving_type or saving_type == "Simpanan Sukarela") and
		(not transaction_kind or transaction_kind == "Pengambilan")
	)
	if include_voluntary_deposit or include_voluntary_withdrawal:
		vs_filters = {"cooperative_member": member.name, "docstatus": ["!=", 0]}
		if include_voluntary_deposit and not include_voluntary_withdrawal:
			vs_filters["transaction_type"] = "Deposit"
		elif include_voluntary_withdrawal and not include_voluntary_deposit:
			vs_filters["transaction_type"] = "Withdrawal"

		voluntary_rows = frappe.get_all(
			"Voluntary Saving",
			filters=vs_filters,
			fields=["name", "transaction_type", "amount", "status", "payment_date", "creation", "payment_request"],
			order_by="creation desc"
		)

		for row in voluntary_rows:
			is_deposit = row.transaction_type == "Deposit"
			p_date = row.payment_date or getdate(row.creation)
			items.append({
				"date": str(p_date),
				"type": "voluntary_deposit" if is_deposit else "voluntary_withdrawal",
				"period": None,
				"amount": flt(row.amount),
				"due_date": None,
				"saving_type": "Simpanan Sukarela",
				"transaction_kind": "Setoran" if is_deposit else "Pengambilan",
				"payment_date": str(p_date),
				"payment_method": get_payment_method_label(row.payment_request),
				"status": row.status,
				"reference_doctype": "Voluntary Saving",
				"reference_name": row.name,
				"payment_request": row.payment_request
			})

	# Sort by date descending
	items.sort(key=lambda x: x["date"], reverse=True)

	total_count = len(items)
	start = (page - 1) * page_length
	end = start + page_length
	paginated = items[start:end]

	return {
		"items": paginated,
		"total_count": total_count,
		"page": page,
		"page_length": page_length,
		"has_more": end < total_count
	}


@frappe.whitelist()
def create_mandatory_saving_payment_request(saving_name, row_names, payment_method_type, payment_channel=None):
	"""
	Create Payment Request for Mandatory Savings 
	saving_name: ID of the Mandatory Saving document
	row_names: List of Mandatory Saving Detail row names to be paid
	"""
	import json
	if isinstance(row_names, str):
		row_names = json.loads(row_names)

	if not row_names:
		frappe.throw(_("No months selected for payment"))

	ms = frappe.get_doc("Mandatory Saving", saving_name)
	member = frappe.get_doc("Cooperative Member", ms.cooperative_member)
	settings = frappe.get_doc("Cooperative Settings")
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)

	total_amount = 0
	rows_to_update = []
	for row in ms.get("monthly_details"):
		if row.name in row_names:
			if row.status not in ["Unpaid", "Pending Payment"]:
				frappe.throw(_("Row {0} for month {1} is already {2}").format(row.name, row.month_name, row.status))
			total_amount += row.amount
			rows_to_update.append(row)

	if total_amount <= 0:
		frappe.throw(_("Invalid total amount for payment"))

	# Create Payment Request
	pr = frappe.new_doc("Payment Request")
	pr.payment_request_type = "Inward"
	pr.reference_doctype = "Mandatory Saving"
	pr.reference_name = ms.name
	pr.party_type = "Customer"
	pr.party = member.customer
	pr.party_name = member.full_name
	pr.grand_total = total_amount
	pr.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
	pr.company = settings.company

	if hasattr(pr, 'payment_method_type'):
		pr.payment_method_type = payment_method.name

	if payment_method.payment_type == "Payment Gateway" and payment_channel:
		if hasattr(pr, 'payment_channel_code'):
			pr.payment_channel_code = payment_channel

	if hasattr(pr, 'mode_of_payment') and payment_method.mode_of_payment:
		pr.mode_of_payment = payment_method.mode_of_payment

	if hasattr(pr, 'payment_gateway_account') and payment_method.payment_gateway_account:
		pr.payment_gateway_account = payment_method.payment_gateway_account

	pr.mute_email = 1
	pr.email_to = member.email or frappe.session.user
	pr.subject = f"Payment for Mandatory Savings - {member.name}"

	pr.insert(ignore_permissions=True)

	# Update rows
	for row in rows_to_update:
		row.status = "Pending Payment"
		row.payment_request = pr.name
		# Save child doc directly
		frappe.db.set_value("Mandatory Saving Detail", row.name, {
			"status": "Pending Payment",
			"payment_request": pr.name
		}, update_modified=False)

	return {"payment_request": pr.name}


@frappe.whitelist()
def get_saving_payment_details(pr_name):
	"""
	Fetch payment request details and format as CheckoutPaymentDetails
	"""
	if not frappe.db.exists("Payment Request", pr_name):
		frappe.throw(_("Payment Request not found"))

	pr = frappe.get_doc("Payment Request", pr_name)
	payment_method = frappe.get_doc("Webshop Payment Method", pr.payment_method_type)

	bank_details = None
	if payment_method.payment_type == "Transfer Manual" and payment_method.bank_account:
		bank_account = frappe.get_doc("Bank Account", payment_method.bank_account)
		bank_details = {
			"account_number": bank_account.bank_account_no or "",
			"bank_name": bank_account.bank or "",
			"account_holder": payment_method.account_holder_name or "",
			"branch_code": bank_account.branch_code or ""
		}

	status_map = {
		0: "Pending",
		1: "Approved",
		2: "Rejected"
	}

	approval = {
		"name": pr.name,
		"status": status_map.get(pr.docstatus, "Pending"),
		"payment_proof": pr.payment_proof,
		"remarks": pr.remarks
	}

	# Create a mock 'sales_order' to reuse UI component
	sales_order_mock = {
		"name": pr.name,
		"customer": pr.party_name,
		"grand_total": pr.grand_total,
		"delivery_date": None,
		"student_name": None,
		"pickup_type": None,
		"unit": None
	}

	return {
		"sales_order": sales_order_mock,
		"payment_method": {
			"name": payment_method.name,
			"title": payment_method.title,
			"payment_type": payment_method.payment_type,
			"need_admin_approval": payment_method.need_admin_approval,
			"payment_duration": payment_method.payment_duration
		},
		"bank_account_details": bank_details,
		"payment_approval": approval,
		"virtual_account": {
			"number": pr.virtual_account_number,
			"bank": pr.virtual_account_bank,
			"expiry": pr.payment_due_date
		}
	}


@frappe.whitelist()
def upload_saving_payment_proof(pr_name, file_url, notes=None):
	"""
	Uploads payment proof onto the Payment Request for Savings
	"""
	if not frappe.db.exists("Payment Request", pr_name):
		frappe.throw(_("Payment Request not found"))

	pr_doc = frappe.get_doc("Payment Request", pr_name)

	if pr_doc.docstatus == 0:
		pr_doc.payment_proof = file_url
		if notes:
			current_remarks = pr_doc.remarks or ""
			pr_doc.remarks = (current_remarks + "\n\n" + notes) if current_remarks else notes

		pr_doc.save(ignore_permissions=True)
		frappe.db.commit()
		return {"status": "success", "message": "Bukti pembayaran berhasil diupload"}
	else:
		frappe.throw(_("Payment Request has already been submitted or processed."))

@frappe.whitelist()
def create_voluntary_saving_deposit_payment(amount, payment_method_type, payment_channel=None):
	"""
	Create a Voluntary Saving (Deposit) document and its Payment Request
	amount: Amount to deposit
	payment_method_type: Selected payment method
	"""
	amount = float(amount)
	if amount <= 0:
		frappe.throw(_("Minal Setoran tidak valid"))

	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to proceed"))

	member_records = frappe.get_all(
		"Cooperative Member",
		filters={"email": frappe.session.user, "status": "Active"},
		fields=["name", "customer"],
		limit=1
	)

	if not member_records:
		frappe.throw(_("Active cooperative membership not found"))

	member = member_records[0]

	# Create Voluntary Saving Document
	vs = frappe.new_doc("Voluntary Saving")
	vs.cooperative_member = member.name
	vs.customer = member.customer
	vs.transaction_type = "Deposit"
	vs.amount = amount
	vs.status = "Pending Payment"
	
	vs.flags.ignore_permissions = True
	vs.insert()
	vs.submit()

	# Create Payment Request
	settings = frappe.get_doc("Cooperative Settings")
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)

	pr = frappe.new_doc("Payment Request")
	pr.payment_request_type = "Inward"
	pr.reference_doctype = "Voluntary Saving"
	pr.reference_name = vs.name
	pr.party_type = "Customer"
	pr.party = member.customer
	pr.party_name = member.name
	pr.grand_total = amount
	pr.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
	pr.company = settings.company

	if hasattr(pr, 'payment_method_type'):
		pr.payment_method_type = payment_method.name

	if payment_method.payment_type == "Payment Gateway" and payment_channel:
		if hasattr(pr, 'payment_channel_code'):
			pr.payment_channel_code = payment_channel

	if hasattr(pr, 'mode_of_payment') and payment_method.mode_of_payment:
		pr.mode_of_payment = payment_method.mode_of_payment

	if hasattr(pr, 'payment_gateway_account') and payment_method.payment_gateway_account:
		pr.payment_gateway_account = payment_method.payment_gateway_account

	pr.mute_email = 1
	pr.email_to = frappe.session.user
	pr.subject = f"Payment for Voluntary Saving Deposit - {member.name}"

	pr.insert(ignore_permissions=True)

	# Link the PR back to Voluntary Saving
	frappe.db.set_value("Voluntary Saving", vs.name, {
		"payment_request": pr.name
	}, update_modified=False)

	return {"payment_request": pr.name}

@frappe.whitelist()
def create_voluntary_saving_withdrawal(amount, payment_method, bank_details=None):
	"""
	Create a Voluntary Saving (Withdrawal) request
	amount: Amount to withdraw
	payment_method: Preferred method (Cash or Transfer Manual)
	bank_details: JSON string containing bank name, account number, etc (if Transfer Manual)
	"""
	import json
	
	amount = float(amount)
	if amount <= 0:
		frappe.throw(_("Nominal penarikan tidak valid"))

	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to proceed"))

	member_records = frappe.get_all(
		"Cooperative Member",
		filters={"email": frappe.session.user, "status": "Active"},
		fields=["name", "customer", "voluntary_saving_balance"],
		limit=1
	)

	if not member_records:
		frappe.throw(_("Active cooperative membership not found"))

	member = member_records[0]

	if amount > member.voluntary_saving_balance:
		frappe.throw(_("Saldo tidak mencukupi. Saldo maksimal yang dapat ditarik: {0}").format(member.voluntary_saving_balance))

	# Format bank details for admin notes
	notes_text = ""
	bank_name = ""
	account_number = ""
	account_holder_name = ""
	if payment_method == "Transfer Manual" and bank_details:
		try:
			details = json.loads(bank_details) if isinstance(bank_details, str) else bank_details
			bank_name = details.get('bank_name', '')
			account_number = details.get('account_number', '')
			account_holder_name = details.get('account_holder_name', '')
			notes_text = f"**Instruksi Pencairan (Transfer):**\n"
			notes_text += f"Bank: {bank_name}\n"
			notes_text += f"No. Rekening: {account_number}\n"
			notes_text += f"Atas Nama: {account_holder_name}"
		except Exception:
			pass
	else:
		notes_text = f"**Instruksi Pencairan:** Pengambilan Tunai"

	# Create Voluntary Saving Document
	vs = frappe.new_doc("Voluntary Saving")
	vs.cooperative_member = member.name
	vs.customer = member.customer
	vs.transaction_type = "Withdrawal"
	vs.amount = amount
	vs.notes = notes_text
	vs.status = "Pending Approval"
	
	if bank_name: vs.bank_name = bank_name
	if account_number: vs.account_number = account_number
	if account_holder_name: vs.account_holder_name = account_holder_name
	
	vs.flags.ignore_permissions = True
	vs.insert()


	return {"status": "success", "name": vs.name}

