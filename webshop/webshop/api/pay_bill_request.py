# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Bills Payment API endpoints for webshop
Handles payment initiation for Sales Invoices (bills)
"""

import frappe
from frappe import _
from frappe.utils import now_datetime
from datetime import timedelta
from webshop.webshop.shopping_cart.cart import get_party


@frappe.whitelist()
def initiate_bill_payment(sales_invoice_name, payment_method_type, payment_channel=None):
	"""
	Initiate payment for a Sales Invoice (bill)
	
	Args:
		sales_invoice_name (str): Name of the Sales Invoice to pay
		payment_method_type (str): Payment method from Webshop Payment Method (selected by user)
		payment_channel (str, optional): Payment channel code for gateway (e.g., bank code for VA)
	
	Returns:
		dict: {
			payment_request: Payment Request name,
			payment_url: URL to redirect,
			redirect_type: "gateway" | "manual" | "virtual_account",
			virtual_account: VA details if applicable
		}
	"""
	try:
		# Validate inputs
		if not sales_invoice_name:
			frappe.throw(_("Sales Invoice name is required"))
		
		if not payment_method_type:
			frappe.throw(_("Payment method is required"))
		
		# Get Sales Invoice
		if not frappe.db.exists("Sales Invoice", sales_invoice_name):
			frappe.throw(_("Sales Invoice {0} not found").format(sales_invoice_name))
		
		sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
		
		# Validate invoice is submitted
		if sales_invoice.docstatus != 1:
			frappe.throw(_("Sales Invoice must be submitted"))
		
		# Validate invoice has outstanding amount
		if sales_invoice.outstanding_amount <= 0:
			frappe.throw(_("This invoice has already been paid"))
		
		# Validate invoice belongs to current user
		party = get_party()
		if not party or sales_invoice.customer != party.name:
			frappe.throw(_("You don't have permission to pay this invoice"))
		
		# Get payment method
		if not frappe.db.exists("Webshop Payment Method", payment_method_type):
			frappe.throw(_("Invalid payment method"))
		
		payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)
		
		if not payment_method.enabled:
			frappe.throw(_("This payment method is currently disabled"))
		
		# Check for existing Payment Request (reuse per user requirement)
		existing_pr = frappe.db.exists("Payment Request", {
			"reference_doctype": "Sales Invoice",
			"reference_name": sales_invoice_name,
			"docstatus": ["in", [0, 1]],  # Draft or Submitted
			"status": ["!=", "Paid"]
		})
		
		if existing_pr:
			payment_request = frappe.get_doc("Payment Request", existing_pr)
			
			# Update payment_method_type if changed
			if hasattr(payment_request, 'payment_method_type'):
				if payment_request.payment_method_type != payment_method_type:
					payment_request.payment_method_type = payment_method_type
					payment_request.save(ignore_permissions=True)
		else:
			# Create new Payment Request with payment_method_type field
			payment_request = create_payment_request_for_invoice(
				sales_invoice, 
				payment_method,
				payment_channel
			)
		
		frappe.db.commit()
		
		# Get payment URL/details based on payment method type
		payment_data = get_payment_url_for_invoice(
			sales_invoice_name,
			payment_method,
			payment_request,
			payment_channel
		)
		
		return {
			"payment_request": payment_request.name,
			"payment_url": payment_data.get("payment_url"),
			"redirect_type": payment_data.get("redirect_type"),
			"virtual_account": payment_data.get("virtual_account")
		}
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bills: Initiate Payment Error")
		frappe.throw(_("Failed to initiate payment: {0}").format(str(e)))


def create_payment_request_for_invoice(sales_invoice, payment_method, payment_channel=None):
	"""
	Create a Payment Request for Sales Invoice
	
	Args:
		sales_invoice (Document): Sales Invoice document
		payment_method (Document): Webshop Payment Method document
		payment_channel (str, optional): Payment channel code
	
	Returns:
		Document: Created Payment Request
	"""
	payment_request = frappe.new_doc("Payment Request")
	
	# Standard Payment Request fields
	payment_request.payment_request_type = "Inward"
	payment_request.reference_doctype = "Sales Invoice"
	payment_request.reference_name = sales_invoice.name
	payment_request.party_type = "Customer"
	payment_request.party = sales_invoice.customer
	payment_request.party_name = sales_invoice.customer_name
	payment_request.grand_total = sales_invoice.outstanding_amount
	payment_request.currency = sales_invoice.currency
	payment_request.company = sales_invoice.company
	
	# Set email and subject
	payment_request.email_to = sales_invoice.contact_email or frappe.session.user
	payment_request.subject = f"Payment for Invoice {sales_invoice.name}"
	
	# Mute email since this is manual approval workflow
	payment_request.mute_email = 1
	
	# Calculate payment due date based on duration
	payment_duration_seconds = payment_method.payment_duration or 86400  # Default 24h
	payment_request.payment_due_date = now_datetime() + timedelta(seconds=payment_duration_seconds)
	
	# CRITICAL: Set payment_method_type custom field
	# This enables is_webshop_manual_payment() to work for Sales Invoice
	if hasattr(payment_request, 'payment_method_type'):
		payment_request.payment_method_type = payment_method.name
	
	# For Payment Gateway, set gateway account
	if payment_method.payment_type == "Payment Gateway":
		payment_request.payment_gateway_account = payment_method.payment_gateway_account
		
		# Set payment channel if provided
		if payment_channel:
			payment_request.payment_channel_code = payment_channel
	
	# Insert as Draft for manual payments, will be submitted for gateways
	payment_request.insert(ignore_permissions=True)
	
	return payment_request


def get_payment_url_for_invoice(sales_invoice_name, payment_method, payment_request, payment_channel=None):
	"""
	Get payment URL based on payment method type
	
	Args:
		sales_invoice_name (str): Sales Invoice name
		payment_method (Document): Webshop Payment Method document
		payment_request (Document): Payment Request document
		payment_channel (str, optional): Payment channel code
	
	Returns:
		dict: {payment_url: str, redirect_type: str, virtual_account: dict}
	"""
	try:
		# For Payment Gateway type
		if payment_method.payment_type == "Payment Gateway":
			# Submit Payment Request for gateway (needed for webhooks)
			if payment_request.docstatus == 0:
				# Mute email to prevent email account error
				payment_request.flags.mute_email = True
				payment_request.submit()
			
			# Handle Xendit Virtual Account
			if payment_channel:
				try:
					xendit_settings = frappe.get_doc("Xendit Settings")
					if xendit_settings.enabled:
						# Create virtual account
						payment_data = {
							"order_id": payment_request.name,
							"reference_doctype": "Sales Invoice",
							"reference_docname": sales_invoice_name,
							"amount": payment_request.grand_total,
							"currency": payment_request.currency or "IDR",
							"bank_code": payment_channel,
							"payment_channel_code": payment_channel,
							"payer_name": payment_request.party_name,
							"payer_email": payment_request.email_to,
							"redirect_to": f"/bills/{sales_invoice_name}/payment"
						}
						
						result = xendit_settings.create_request(payment_data)
						
						# Update payment request with VA details
						if xendit_settings.virtual_account_number:
							payment_request.db_set("virtual_account_number", xendit_settings.virtual_account_number)
						if xendit_settings.virtual_account_bank:
							payment_request.db_set("virtual_account_bank", xendit_settings.virtual_account_bank)
						
						return {
							"payment_url": f"/bills/{sales_invoice_name}/payment",
							"redirect_type": "virtual_account",
							"virtual_account": {
								"number": xendit_settings.virtual_account_number,
								"bank": xendit_settings.virtual_account_bank,
								"expiry": payment_request.payment_due_date
							}
						}
				except Exception as e:
					frappe.log_error(f"Xendit VA Creation Error: {str(e)}", "Bills Payment")
					# Fallback to standard gateway flow
					pass
			
			# Standard gateway flow
			payment_url = payment_request.get_payment_url()
			return {
				"payment_url": payment_url,
				"redirect_type": "gateway"
			}
		
		# For Transfer Manual type
		elif payment_method.payment_type == "Transfer Manual":
			# Payment Request already created in Draft status
			# Redirect to payment page where user can upload proof
			return {
				"payment_url": f"/bills/{sales_invoice_name}/payment",
				"redirect_type": "manual"
			}
		
		else:
			frappe.throw(_("Invalid payment method type"))
	
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bills: Get Payment URL Error")
		frappe.throw(_("Failed to get payment URL: {0}").format(str(e)))


@frappe.whitelist()
def upload_payment_proof(sales_invoice, file_url, notes=None):
	"""
	Upload payment proof for bill payment (Sales Invoice)
	Similar to checkout upload but for Sales Invoice Payment Requests
	
	Args:
		sales_invoice (str): Sales Invoice name
		file_url (str): URL of the uploaded file
		notes (str, optional): Additional notes about the payment
	
	Returns:
		dict: Status and payment request info
	"""
	# Validate inputs
	if not sales_invoice or not file_url:
		frappe.throw(_("Sales Invoice and File URL are required"))
	
	# Get the sales invoice
	sales_invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice)
	
	# Validate user has permission to view this invoice
	party = get_party()
	if not party or sales_invoice_doc.customer != party.name:
		frappe.throw(_("You don't have permission to update this invoice"))
	
	# Get the payment request for this invoice
	payment_request = frappe.get_all(
		"Payment Request",
		filters={
			"reference_doctype": "Sales Invoice",
			"reference_name": sales_invoice,
			"docstatus": ["in", [0, 1]]  # Draft or Submitted (not Cancelled)
		},
		fields=["name", "docstatus"],
		limit=1
	)
	
	if payment_request:
		# Update existing Payment Request
		pr_doc = frappe.get_doc("Payment Request", payment_request[0]["name"])
		
		# Only update if still in Draft status (not yet approved)
		if pr_doc.docstatus == 0:
			pr_doc.payment_proof = file_url
			if notes:
				current_remarks = pr_doc.remarks or ""
				pr_doc.remarks = (current_remarks + "\n\n" + notes) if current_remarks else notes
			pr_doc.save(ignore_permissions=True)
		else:
			frappe.msgprint(
				_("Payment Request has already been processed. Contact admin if you need to update payment proof."),
				indicator="orange"
			)
	else:
		frappe.throw(_("No Payment Request found for this invoice"))
	
	frappe.db.commit()
	
	return {
		"status": "success",
		"message": "Payment proof uploaded successfully",
		"payment_request_id": pr_doc.name
	}
