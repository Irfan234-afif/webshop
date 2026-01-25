
import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import get_party

@frappe.whitelist()
def get_bills(tab="bills"):
	"""
	Fetch Sales Invoices linked to Subscriptions for the current user.
	
	Args:
		tab (str): Filter tab - 'bills' for unpaid invoices, 'history' for paid invoices
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No link to a Customer found for this user."), title=_("Authentication Required"))

	# Base filters
	filters = {
		"customer": party.name,
		"docstatus": 1,
		"subscription": ["is", "set"] # Only subscription-generated invoices
	}
	
	# Add outstanding_amount filter based on tab
	if tab == "bills":
		# Unpaid invoices
		filters["outstanding_amount"] = [">", 0]
		order_by = "due_date asc"
	else:
		# Paid invoices (history)
		filters["outstanding_amount"] = ["=", 0]
		order_by = "posting_date desc"

	invoices = frappe.get_all(
		"Sales Invoice",
		filters=filters,
		fields=[
			"name",
			"posting_date",
			"due_date",
			"grand_total",
			"outstanding_amount",
			"currency",
			"subscription",
			"status"
		],
		order_by=order_by
	)

	# Check for existing Payment Request for each invoice
	for invoice in invoices:
		pr_exists = frappe.db.exists("Payment Request", {
			"reference_doctype": "Sales Invoice",
			"reference_name": invoice["name"],
			"docstatus": ["in", [0, 1]],  # Draft or Submitted
			"status": ["!=", "Paid"]
		})
		invoice["has_payment_request"] = bool(pr_exists)

	return {
		"bills": invoices
	}

@frappe.whitelist()
def get_unpaid_bills_count():
	"""
	Get the count of unpaid bills for the current user.
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No link to a Customer found for this user."), title=_("Authentication Required"))
	
	# Base filters
	filters = {
		"customer": party.name,
		"docstatus": 1,
		"subscription": ["is", "set"],
		"outstanding_amount": [">", 0]
	}
	order_by = "due_date asc"
	return frappe.db.count("Sales Invoice", filters=filters)

@frappe.whitelist()
def get_bill_payment_details(sales_invoice_name):
	"""
	Get complete payment details for bill payment page
	Fetches sales invoice info, payment method details, bank account, and payment request status
	
	Args:
		sales_invoice_name (str): Name of the Sales Invoice
	
	Returns:
		dict: Complete payment details including invoice info, payment method, bank details, and payment request
	"""
	try:
		# Get Sales Invoice
		if not frappe.db.exists("Sales Invoice", sales_invoice_name):
			frappe.throw(_("Sales Invoice {0} not found").format(sales_invoice_name))
		
		sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
		subscription = frappe.get_doc("Subscription", sales_invoice.subscription)
		
		# Validate user has permission to view this invoice
		party = get_party()
		if not party or sales_invoice.customer != party.name:
			frappe.throw(_("You don't have permission to view this invoice"), frappe.PermissionError)

		
		# Get Payment Request if exists
		pr_records = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Invoice",
				"reference_name": sales_invoice_name,
				"docstatus": ["in", [0, 1, 2]]  # All statuses
			},
			fields=["name", "docstatus", "payment_proof", "remarks", "payment_method_type"],
			order_by="creation desc",
			limit=1
		)
		
		payment_request_data = None
		payment_method_data = None
		bank_details = None
		virtual_account_data = None
		
		if pr_records:
			pr = pr_records[0]
			
			# Map docstatus to frontend-friendly status
			status_map = {
				0: "Pending",   # Draft
				1: "Approved",  # Submitted
				2: "Rejected"   # Cancelled
			}
			
			payment_request_data = {
				"name": pr.name,
				"status": status_map.get(pr.docstatus, "Pending"),
				"payment_proof": pr.payment_proof,
				"remarks": pr.remarks
			}
			
			# Get payment method details from Payment Request
			if pr.payment_method_type:
				payment_method = frappe.get_doc("Webshop Payment Method", pr.payment_method_type)
				
				payment_method_data = {
					"name": payment_method.name,
					"title": payment_method.title,
					"payment_type": payment_method.payment_type,
					"need_admin_approval": payment_method.need_admin_approval,
					"payment_duration": payment_method.payment_duration
				}
				
				# Get bank account details if Transfer Manual
				if payment_method.payment_type == "Transfer Manual" and payment_method.bank_account:
					try:
						bank_account = frappe.get_doc("Bank Account", payment_method.bank_account)
						bank_details = {
							"account_number": bank_account.bank_account_no or "",
							"bank_name": bank_account.bank or "",
							"account_holder": payment_method.account_holder_name or "",
							"branch_code": bank_account.branch_code or ""
						}
					except Exception as e:
						frappe.log_error(f"Failed to fetch bank account for bill payment: {str(e)}", "Get Bill Payment Details")
			
			# Get Virtual Account details if exists
			pr_doc = frappe.get_doc("Payment Request", pr.name)
			if hasattr(pr_doc, 'virtual_account_number') and pr_doc.virtual_account_number:
				virtual_account_data = {
					"number": pr_doc.virtual_account_number,
					"bank": pr_doc.virtual_account_bank or "",
					"expiry": pr_doc.payment_due_date
				}
		
		return {
			"sales_invoice": {
				"name": sales_invoice.name,
				"customer": sales_invoice.customer_name,
				"grand_total": sales_invoice.grand_total,
				"outstanding_amount": sales_invoice.outstanding_amount,
				"due_date": sales_invoice.due_date,
				"posting_date": sales_invoice.posting_date,
				"subscription": sales_invoice.subscription,
				"student_name": subscription.student
			},
			"payment_method": payment_method_data,
			"bank_account_details": bank_details,
			"payment_request": payment_request_data,
			"virtual_account": virtual_account_data
		}
	
	except frappe.exceptions.PermissionError:
		# Re-raise permission errors as-is
		raise
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bills: Get Payment Details Error")
		frappe.throw(_("Failed to load payment details: {0}").format(str(e)))

