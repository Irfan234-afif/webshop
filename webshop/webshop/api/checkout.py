# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Checkout API endpoints for webshop
"""

import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import _get_cart_quotation
from frappe.utils import now_datetime, get_datetime
from datetime import timedelta


@frappe.whitelist()
def get_checkout_data(student_name=None):
	"""
	Get cart quotation data formatted for checkout

	Args:
		student_name (str, optional): Student name to fetch quotation for

	Returns:
		dict: Checkout data including quotation details, items, totals, and current checkout selections
	"""
	try:
		# If student_name provided, set as active student first
		if student_name:
			from webshop.webshop.shopping_cart.student_utils import set_active_student
			set_active_student(student_name)
			frappe.log_error(f"Set active student to: {student_name}", "Checkout Debug")

		quotation = _get_cart_quotation()

		frappe.log_error(
			f"get_checkout_data - Quotation: {quotation.name if quotation else 'None'}, Student: {quotation.student if quotation else 'N/A'}",
			"Checkout Debug"
		)

		if not quotation:
			frappe.throw(_("No active cart found. Please add items to cart first."))

		if not quotation.items:
			frappe.throw(_("Your cart is empty. Please add items to cart first."))

		# Get quotation details
		items = []
		for item in quotation.items:
			items.append({
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": item.qty,
				"rate": item.rate,
				"amount": item.amount,
				"image": frappe.db.get_value("Website Item", {"item_code": item.item_code}, "website_image") or ""
			})

		# Calculate discounts from quotation
		# Quotation already has total discount applied, we can use those fields
		voucher_discount = 0
		member_discount = 0

		# Use quotation's discount fields
		# If there's a coupon code, attribute discount to voucher
		if quotation.coupon_code and quotation.discount_amount:
			voucher_discount = abs(quotation.discount_amount or 0)
		elif quotation.discount_amount:
			# If no coupon code, consider it member discount
			member_discount = abs(quotation.discount_amount or 0)

		# Alternative: If additional_discount_percentage is used
		if quotation.additional_discount_percentage and not quotation.discount_amount:
			discount_value = (quotation.net_total * quotation.additional_discount_percentage) / 100
			if quotation.coupon_code:
				voucher_discount = abs(discount_value)
			else:
				member_discount = abs(discount_value)

		# Check if customer has address
		has_address = bool(quotation.shipping_address_name or quotation.customer_address)

		checkout_data = {
			"quotation_name": quotation.name,
			"items": items,
			"subtotal": quotation.net_total,
			"voucher_discount": voucher_discount,
			"member_discount": member_discount,
			"total": quotation.grand_total,
			"student": quotation.student if hasattr(quotation, 'student') else None,
			"pickup_type": quotation.pickup_type if hasattr(quotation, 'pickup_type') else None,
			"payment_method_type": quotation.payment_method_type if hasattr(quotation, 'payment_method_type') else None,
			"delivery_date": quotation.delivery_date if hasattr(quotation, 'delivery_date') else None,
			"delivery_time": quotation.delivery_time if hasattr(quotation, 'delivery_time') else None,
			"has_address": has_address,
			"shipping_address": quotation.shipping_address_name,
			"billing_address": quotation.customer_address
		}

		return checkout_data

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Get Checkout Data Error")
		frappe.throw(_("Failed to load checkout data: {0}").format(str(e)))


@frappe.whitelist()
def update_pickup_type(quotation_name, pickup_type, delivery_date=None, delivery_time=None):
	"""
	Update pickup type on cart quotation

	Args:
		quotation_name (str): Name of the quotation to update
		pickup_type (str): "Ambil di koperasi" or "Ambil secara online"
		delivery_date (str, optional): Date and time of delivery/pickup (required if pickup_type is koperasi)

	Returns:
		dict: Success message with updated quotation name
	"""
	try:
		# Validate quotation name provided
		if not quotation_name:
			frappe.throw(_("Quotation name is required"))

		# Validate pickup type
		valid_types = ["Ambil di koperasi", "Ambil secara online"]
		if pickup_type not in valid_types:
			frappe.throw(_("Invalid pickup type. Must be one of: {0}").format(", ".join(valid_types)))

		# Validate required fields for koperasi pickup
		if pickup_type == "Ambil di koperasi":
			if not delivery_date or not delivery_time:
				frappe.throw(_("Delivery date and time are required for koperasi pickup"))

		# Get quotation by name explicitly (not via session)
		if not frappe.db.exists("Quotation", quotation_name):
			frappe.throw(_("Quotation {0} not found").format(quotation_name))

		quotation = frappe.get_doc("Quotation", quotation_name)

		# Validate quotation is a shopping cart
		if quotation.order_type != "Shopping Cart":
			frappe.throw(_("Invalid quotation type"))

		# Validate quotation belongs to current user
		if quotation.contact_email != frappe.session.user:
			frappe.throw(_("You don't have permission to update this quotation"))

		frappe.log_error(
			f"Updating quotation: {quotation.name}, Student: {quotation.student}, Pickup: {pickup_type}",
			"Checkout Debug"
		)

		# Update pickup information using db_set to avoid validation errors
		# db_set updates the database directly without triggering validation
		# CRITICAL: db_set only works on saved documents (with name)
		quotation.db_set("pickup_type", pickup_type, update_modified=True)

		if pickup_type == "Ambil di koperasi":
			quotation.db_set("delivery_date", delivery_date, update_modified=False)
			quotation.db_set("delivery_time", delivery_time, update_modified=False)
		else:
			# Clear delivery date for online delivery
			quotation.db_set("delivery_date", None, update_modified=False)
			quotation.db_set("delivery_time", None, update_modified=False)

		frappe.db.commit()

		return {
			"success": True,
			"message": _("Pickup type updated successfully"),
			"quotation_name": quotation.name
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Update Pickup Type Error")
		frappe.throw(_("Failed to update pickup type: {0}").format(str(e)))


@frappe.whitelist()
def update_payment_method(quotation_name, payment_method_type):
	"""
	Update payment method on cart quotation

	Args:
		quotation_name (str): Name of the quotation to update
		payment_method_type (str): Payment method name from Webshop Payment Method doctype

	Returns:
		dict: Success message with updated quotation name
	"""
	try:
		# Validate quotation name provided
		if not quotation_name:
			frappe.throw(_("Quotation name is required"))

		# Validate payment method exists in the Webshop Payment Method doctype
		if not frappe.db.exists("Webshop Payment Method", payment_method_type):
			frappe.throw(_("Invalid payment method. Payment method does not exist."))

		# Get the payment method to check if it's enabled
		payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)
		if not payment_method.enabled:
			frappe.throw(_("This payment method is currently disabled."))

		# Get quotation by name explicitly
		if not frappe.db.exists("Quotation", quotation_name):
			frappe.throw(_("Quotation {0} not found").format(quotation_name))

		quotation = frappe.get_doc("Quotation", quotation_name)

		# Validate quotation is a shopping cart
		if quotation.order_type != "Shopping Cart":
			frappe.throw(_("Invalid quotation type"))

		# Validate quotation belongs to current user
		if quotation.contact_email != frappe.session.user:
			frappe.throw(_("You don't have permission to update this quotation"))

		frappe.log_error(
			f"Updating payment method for quotation: {quotation.name}, Method: {payment_method_type}",
			"Checkout Debug"
		)

		# Update payment method using db_set to avoid validation errors
		# db_set updates the database directly without triggering validation
		quotation.db_set("payment_method_type", payment_method_type, update_modified=True)

		frappe.db.commit()

		return {
			"success": True,
			"message": _("Payment method updated successfully"),
			"quotation_name": quotation.name
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Update Payment Method Error")
		frappe.throw(_("Failed to update payment method: {0}").format(str(e)))


@frappe.whitelist()
def get_payment_methods():
	"""
	Get available payment methods with metadata, including bank account details for Transfer Manual types

	Returns:
		list: List of payment methods with name, description, enabled status, icon, and bank account details
	"""
	payment_methods = frappe.get_all(
		"Webshop Payment Method",
		filters={"enabled": 1},
		fields=[
			"payment_method_name as name",
			"title as label",
			"description",
			"enabled",
			"icon",
			"need_admin_approval",
			"payment_type",
			"bank_account",
			"account_holder_name"
		],
		order_by="sort_order asc"
	)

	# Enhance payment methods with bank account details for Transfer Manual type
	result = []
	for method in payment_methods:
		method_data = {
			"name": method.name,
			"label": method.label,
			"description": method.description,
			"enabled": method.enabled,
			"icon": method.icon,
			"need_admin_approval": method.need_admin_approval,
			"payment_type": method.payment_type
		}

		# Add bank account details for Transfer Manual type
		if method.payment_type == "Transfer Manual" and method.bank_account:
			try:
				bank_account = frappe.get_doc("Bank Account", method.bank_account)
				method_data["bank_account_details"] = {
					"account_number": bank_account.bank_account_no or "",
					"bank_name": bank_account.bank or "",
					"account_holder": method.account_holder_name or "",
					"branch_code": bank_account.branch_code or ""
				}
			except Exception as e:
				frappe.log_error(f"Failed to fetch bank account details for {method.bank_account}: {str(e)}", "Get Payment Methods")
				# Continue without bank details if there's an error
				method_data["bank_account_details"] = None

			# Add Channels if Payment Gateway
		if method.payment_type == "Payment Gateway":
			channels = frappe.get_all(
				"Webshop Payment Channel",
				filters={"parent": method.name},
				fields=["channel_code", "channel_name", "description", "icon"],
				order_by="idx asc"
			)
			if channels:
				method_data["payment_channels"] = channels

		result.append(method_data)

	return result


@frappe.whitelist()
def get_checkout_payment_details(sales_order_name):
	"""
	Get complete payment details for checkout payment page
	Fetches sales order info, payment method details, bank account, and approval status

	Args:
		sales_order_name (str): Name of the Sales Order

	Returns:
		dict: Complete payment details including order info, payment method, bank details, and approval status
	"""
	try:
		# Get Sales Order
		if not frappe.db.exists("Sales Order", sales_order_name):
			frappe.throw(_("Sales Order {0} not found").format(sales_order_name))

		sales_order = frappe.get_doc("Sales Order", sales_order_name)

		# Validate user has permission to view this order
		if sales_order.contact_email != frappe.session.user:
			frappe.throw(_("You don't have permission to view this order"))

		# Get payment method
		if not sales_order.payment_method_type:
			frappe.throw(_("No payment method selected for this order"))

		payment_method = frappe.get_doc("Webshop Payment Method", sales_order.payment_method_type)

		# Get bank account details if Transfer Manual
		bank_details = None
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
				frappe.log_error(f"Failed to fetch bank account for payment details: {str(e)}", "Get Checkout Payment Details")

		# Get payment request if exists (replaces payment approval)
		approval = None
		if payment_method.need_admin_approval:
			pr_records = frappe.get_all(
				"Payment Request",
				filters={
					"reference_doctype": "Sales Order",
					"reference_name": sales_order_name,
					"docstatus": ["in", [0, 1, 2]]  # All statuses
				},
				fields=["name", "docstatus", "payment_proof", "remarks"],
				limit=1
			)

			if pr_records:
				pr = pr_records[0]
				# Map docstatus to frontend-friendly status
				status_map = {
					0: "Pending",   # Draft
					1: "Approved",  # Submitted
					2: "Rejected"   # Cancelled
				}

				approval = {
					"name": pr.name,
					"status": status_map.get(pr.docstatus, "Pending"),
					"payment_proof": pr.payment_proof,
					"remarks": pr.remarks
				}

		res = {
			"sales_order": {
				"name": sales_order.name,
				"customer": sales_order.customer_name,
				"grand_total": sales_order.grand_total,
				"delivery_date": sales_order.delivery_date if hasattr(sales_order, 'delivery_date') else None,
				"student_name": sales_order.student if hasattr(sales_order, 'student') else None,
				"pickup_type": sales_order.pickup_type if hasattr(sales_order, 'pickup_type') else None,
				"unit": sales_order.school_unit if hasattr(sales_order, 'school_unit') else None
			},
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
				"number": getattr(sales_order, 'virtual_account_number', None), # Fallback if stored on SO
				"bank": getattr(sales_order, 'virtual_account_bank', None),
				"expiry": getattr(sales_order, 'payment_due_date', None)
			}
		}

		# Get general payment status from Payment Request
		# specific logic for identifying if "Paid"
		pr_general = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Order",
				"reference_name": sales_order_name,
				"docstatus": ["!=", 2] # Not cancelled
			},
			fields=["status"],
			order_by="creation desc",
			limit=1
		)
		if pr_general:
			res["payment_status"] = pr_general[0].status
		else:
			res["payment_status"] = "Pending"

		# Check for Payment Request VA details (Primary Source)
		pr_va = frappe.db.get_value("Payment Request", {
			"reference_doctype": "Sales Order",
			"reference_name": sales_order_name,
			"status": ["in", ["Requested", "Pending", "Initiated"]]
		}, ["virtual_account_number", "virtual_account_bank", "payment_due_date"], as_dict=1)

		if pr_va:
			res["virtual_account"] = {
				"number": pr_va.virtual_account_number,
				"bank": pr_va.virtual_account_bank,
				"expiry": pr_va.payment_due_date
			}

		return res

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Get Payment Details Error")
		frappe.throw(_("Failed to load payment details: {0}").format(str(e)))


@frappe.whitelist()
def place_order_with_payment(quotation_name, payment_channel=None):
	"""
	Create Sales Order from cart and redirect to payment

	Args:
		quotation_name (str): Name of the quotation to convert to Sales Order

	Process:
	1. Validate checkout data (pickup_type, payment_method_type)
	2. Call existing place_order() to create Sales Order
	3. Copy custom fields from Quotation to Sales Order
	4. Create Payment Request
	5. Get payment gateway URL based on payment_method_type

	Returns:
		dict: {
			sales_order: Sales Order name,
			payment_url: URL to redirect for payment,
			redirect_type: "gateway" or "manual" or "cash"
		}
	"""
	try:
		from webshop.webshop.shopping_cart.cart import place_order

		# Validate quotation name provided
		if not quotation_name:
			frappe.throw(_("Quotation name is required"))

		# Get quotation by name explicitly
		if not frappe.db.exists("Quotation", quotation_name):
			frappe.throw(_("Quotation {0} not found").format(quotation_name))

		quotation = frappe.get_doc("Quotation", quotation_name)

		# Validate quotation is a shopping cart
		if quotation.order_type != "Shopping Cart":
			frappe.throw(_("Invalid quotation type"))

		# Validate quotation belongs to current user
		if quotation.contact_email != frappe.session.user:
			frappe.throw(_("You don't have permission to update this quotation"))

		# Validate checkout data
		if not quotation.pickup_type:
			frappe.throw(_("Please select a pickup type"))

		if not quotation.payment_method_type:
			frappe.throw(_("Please select a payment method"))

		if quotation.pickup_type == "Ambil di koperasi":
			if not quotation.delivery_date or not quotation.delivery_time:
				frappe.throw(_("Please select delivery date and time"))

		# Store checkout data temporarily
		pickup_type = quotation.pickup_type
		payment_method_type = quotation.payment_method_type
		delivery_date = quotation.delivery_date
		delivery_time = quotation.delivery_time

		# CRITICAL: Re-calculate totals before submitting
		# db_set() skips calculation, so we need to trigger it manually
		# This ensures grand_total, net_total, etc. are calculated
		quotation.flags.ignore_permissions = True
		quotation.run_method("calculate_taxes_and_totals")

		# Save to persist calculated values
		# Clear payment_schedule to avoid validation error
		quotation.payment_schedule = []
		quotation.save(ignore_permissions=True)

		frappe.log_error(
			f"Quotation totals recalculated: {quotation.name}, Grand Total: {quotation.grand_total}, Net Total: {quotation.net_total}",
			"Checkout Debug"
		)

		# Reload quotation from database to ensure we have saved values
		# Use force=True to reload from DB, bypassing cache
		quotation.reload()

		frappe.log_error(
			f"Quotation reloaded from DB: {quotation.name}, Grand Total: {quotation.grand_total}, Net Total: {quotation.net_total}",
			"Checkout Debug"
		)

		# CRITICAL: Set active student so place_order() gets the right quotation
		# place_order() internally calls _get_cart_quotation() which needs active student
		if quotation.student:
			from webshop.webshop.shopping_cart.student_utils import set_active_student
			set_active_student(quotation.student)
			frappe.log_error(f"Set active student for place_order: {quotation.student}", "Checkout Debug")

		# CRITICAL: Prevent auto-commit from submit() calls in place_order
		# This ensures the entire transaction (quotation submit + SO creation + payment setup) is atomic
		original_in_patch = frappe.flags.get("in_patch")
		frappe.flags.in_patch = True  # Prevents auto-commit on document submit
		
		try:
			# Create Sales Order using existing place_order function
			# This will call _get_cart_quotation() internally and should get our recalculated quotation
			sales_order_name = place_order(quotation_name=quotation_name)
		finally:
			# Restore original flag value
			frappe.flags.in_patch = original_in_patch

		# Get the created Sales Order
		sales_order = frappe.get_doc("Sales Order", sales_order_name)

		# Copy custom fields from Quotation to Sales Order
		sales_order.pickup_type = pickup_type
		sales_order.payment_method_type = payment_method_type

		# Set the delivery date using the default field in Sales Order
		if delivery_date:
			sales_order.delivery_date = delivery_date
		if delivery_time:
			sales_order.delivery_time = delivery_time

		sales_order.save(ignore_permissions=True)
		payment_data = get_payment_gateway_url(sales_order_name, payment_method_type, payment_channel)
		frappe.db.commit()

		return {
			"sales_order": sales_order_name,
			"payment_url": payment_data.get("payment_url"),
			"redirect_type": payment_data.get("redirect_type"),
			"virtual_account": payment_data.get("virtual_account")
		}

	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback(), "Checkout: Place Order Error")
		frappe.throw(_("Failed to create order: {0}").format(str(e)))


def get_payment_gateway_url(sales_order_name, payment_method_type, payment_channel=None):
	"""
	Get payment URL based on payment method

	Args:
		sales_order_name (str): Sales Order name
		payment_method_type (str): Payment method type

	Returns:
		dict: {payment_url: str, redirect_type: str}
	"""
	try:
		sales_order = frappe.get_doc("Sales Order", sales_order_name)

		# Get the payment method from the new doctype
		payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)

		# For Payment Gateway type, create payment request and get URL
		if payment_method.payment_type == "Payment Gateway":
			# Check if payment request already exists
			existing_pr = frappe.db.exists("Payment Request", {
				"reference_doctype": "Sales Order",
				"reference_name": sales_order_name,
				"status": ["!=", "Paid"]
			})

			if existing_pr:
				payment_request = frappe.get_doc("Payment Request", existing_pr)
			else:
				# Create new payment request
				payment_request = frappe.new_doc("Payment Request")
				payment_request.payment_gateway_account = payment_method.payment_gateway_account
				payment_request.payment_request_type = "Inward"
				payment_request.party_type = "Customer"
				payment_request.party = sales_order.customer
				payment_request.currency = sales_order.currency
				payment_request.grand_total = sales_order.grand_total
				payment_request.reference_doctype = "Sales Order"
				payment_request.reference_name = sales_order_name
				payment_request.email_to = frappe.session.user

				# Calculate payment due date based on duration
				payment_duration_seconds = payment_method.payment_duration or 86400  # Default 24h if 0 or None
				payment_request.payment_due_date = now_datetime() + timedelta(seconds=payment_duration_seconds)
				
				# Xendit Integration: Set Payment Channel
				if payment_channel:
					payment_request.payment_channel_code = payment_channel

				payment_request.insert(ignore_permissions=True)
				
				# IMPORTANT: Only submit Payment Request for Payment Gateways
				# Manual payments that need admin approval should stay in Draft (docstatus=0)
				# so admin can review payment proof before submitting (approving)
				# Payment gateways need submitted status for webhooks to work
				payment_request.submit()

				# Xendit VA Creation Trigger
				if payment_channel:
					# Check if this gateway is Xendit
					# We assume "payment_gateway_account" is linked to "Xendit" gateway or check settings
					# Better: Check if Xendit Settings is enabled and this PR targets it.
					# For now, if payment_channel is passed, we try to create VA.
					try:
						xendit_settings = frappe.get_doc("Xendit Settings")
						if xendit_settings.enabled:
							# Prepare data for Xendit create_request (following Stripe pattern)
							payment_data = {
								"order_id": payment_request.name,
								"reference_doctype": "Sales Order",
								"reference_docname": sales_order_name,
								"amount": payment_request.grand_total,
								"currency": payment_request.currency or "IDR",
								"bank_code": payment_channel,
								"payment_channel_code": payment_channel,
								"payer_name": sales_order.customer_name,
								"payer_email": payment_request.email_to,
								"redirect_to": f"/order/{sales_order_name}/checkout"
							}
							
							# Create virtual account using new API
							result = xendit_settings.create_request(payment_data)
							
							# Update payment request with VA details
							if xendit_settings.virtual_account_number:
								payment_request.db_set("virtual_account_number", xendit_settings.virtual_account_number)
							if xendit_settings.virtual_account_bank:
								payment_request.db_set("virtual_account_bank", xendit_settings.virtual_account_bank)
							
							return {
								"payment_url": result.get("redirect_to", f"/order/{sales_order_name}/checkout"),
								"redirect_type": "virtual_account",
								"virtual_account": {
									"account_number": xendit_settings.virtual_account_number,
									"bank_code": xendit_settings.virtual_account_bank
								}
							}
					except Exception as e:
						frappe.log_error(f"Xendit VA Creation Error: {str(e)}", "Checkout")
						# Fallback to standard flow or re-raise? 
						# If creation fails, we might want to tell basic checkout page
						pass

			# Get payment URL from payment request
			payment_url = payment_request.get_payment_url()

			return {
				"payment_url": payment_url,
				"redirect_type": "gateway"
			}

		# For Transfer Manual type, handle differently based on need_admin_approval
		elif payment_method.payment_type == "Transfer Manual":
			if payment_method.need_admin_approval:
				# Create a Payment Request for admin to approve
				create_payment_request_for_manual_approval(sales_order, payment_method)
				return {
					"payment_url": f"/order/{sales_order_name}/checkout",
					"redirect_type": "manual"
				}
			else:
				# If no admin approval needed, redirect to unified checkout page
				return {
					"payment_url": f"/order/{sales_order_name}/checkout",
					"redirect_type": "manual"
				}

		else:
			frappe.throw(_("Invalid payment method type"))

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Get Payment URL Error")
		frappe.throw(_("Failed to get payment URL: {0}").format(str(e)))


def create_payment_request_for_manual_approval(sales_order, payment_method):
	"""
	Create a Payment Request for manual payment methods that need admin approval

	Args:
		sales_order (Document): Sales Order document
		payment_method (Document): Webshop Payment Method document

	Returns:
		Document: Created Payment Request in Draft status (docstatus=0)
	"""
	# Create Payment Request instead of Payment Approval
	payment_request = frappe.new_doc("Payment Request")

	# Standard Payment Request fields
	payment_request.payment_request_type = "Inward"
	payment_request.reference_doctype = "Sales Order"
	payment_request.reference_name = sales_order.name
	payment_request.party_type = "Customer"
	payment_request.party = sales_order.customer
	payment_request.party_name = sales_order.customer_name
	payment_request.grand_total = sales_order.grand_total
	payment_request.currency = sales_order.currency
	payment_request.company = sales_order.company

	# Set email and subject
	payment_request.email_to = sales_order.contact_email or frappe.session.user
	payment_request.subject = f"Payment for Sales Order {sales_order.name}"

	# Mute email since this is manual approval workflow
	payment_request.mute_email = 1

	# Calculate payment due date based on duration
	payment_duration_seconds = payment_method.payment_duration or 86400  # Default 24h if 0 or None
	payment_request.payment_due_date = now_datetime() + timedelta(seconds=payment_duration_seconds)

	# Insert as Draft (docstatus=0) - this is the "Pending" state
	payment_request.insert(ignore_permissions=True)

	return payment_request


@frappe.whitelist()
def upload_payment_proof(sales_order, file_url, notes=None):
	"""
	Upload payment proof for manual bank transfer and update Payment Request

	Args:
		sales_order (str): Sales Order name
		file_url (str): URL of the uploaded file
		notes (str, optional): Additional notes about the payment

	Returns:
		dict: Status and payment request info
	"""
	# Validate inputs
	if not sales_order or not file_url:
		frappe.throw(_("Sales Order and File URL are required"))

	# Get the sales order
	sales_order_doc = frappe.get_doc("Sales Order", sales_order)

	# Validate user has permission to view this order
	if sales_order_doc.contact_email != frappe.session.user:
		frappe.throw(_("You don't have permission to update this order"))

	# Get the payment method to check if admin approval is needed
	payment_method = frappe.get_doc("Webshop Payment Method", sales_order_doc.payment_method_type)

	if not payment_method.need_admin_approval:
		frappe.throw(_("Admin approval is not required for this payment method"))

	# Check if a Payment Request already exists for this sales order
	payment_request = frappe.get_all(
		"Payment Request",
		filters={
			"reference_doctype": "Sales Order",
			"reference_name": sales_order,
			"docstatus": ["in", [0, 1]]  # Draft or Submitted (not Cancelled)
		},
		fields=["name", "docstatus"],
		limit=1
	)

	if payment_request:
		# Update existing Payment Request
		pr_doc = frappe.get_doc("Payment Request", payment_request[0].name)

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
		# Create new Payment Request
		pr_doc = create_payment_request_for_manual_approval(sales_order_doc, payment_method)
		pr_doc.payment_proof = file_url
		if notes:
			pr_doc.remarks = notes
		pr_doc.save(ignore_permissions=True)

	frappe.db.commit()

	return {
		"status": "success",
		"message": "Payment proof uploaded successfully",
		"payment_request_id": pr_doc.name
	}


def get_payment_gateway_account():
	"""
	Get payment gateway account from Webshop Settings

	Returns:
		str: Payment gateway account name
	"""
	webshop_settings = frappe.get_single("Webshop Settings")

	if not webshop_settings.payment_gateway_account:
		frappe.throw(_("Payment gateway not configured. Please contact administrator."))

	return webshop_settings.payment_gateway_account


@frappe.whitelist()
def create_customer_address(address_title, address_line1, city, phone, email_id=None, student_name=None):
	"""
	Create customer address for billing and shipping

	Args:
		address_title (str): Address title (e.g., "Home", "Office")
		address_line1 (str): Full address
		city (str): City name
		phone (str): Phone number
		email_id (str, optional): Email address
		student_name (str, optional): Student name for quotation context

	Returns:
		dict: Created address details
	"""
	try:
		from webshop.webshop.shopping_cart.cart import get_party

		# Set active student if provided
		if student_name:
			from webshop.webshop.shopping_cart.student_utils import set_active_student
			set_active_student(student_name)
			frappe.log_error(f"Set active student: {student_name}", "Checkout Debug")

		party = get_party()
		if not party:
			frappe.throw(_("No customer account found"))

		# Create address
		address = frappe.new_doc("Address")
		address.address_title = address_title
		address.address_line1 = address_line1
		address.city = city
		address.phone = phone
		address.email_id = email_id or frappe.session.user

		# Link to customer
		address.append("links", {
			"link_doctype": party.doctype,
			"link_name": party.name
		})

		# Set as both billing and shipping
		address.address_type = "Billing"
		address.is_primary_address = 1
		address.is_shipping_address = 1

		address.insert(ignore_permissions=True)
		frappe.db.commit()

		frappe.log_error(f"Address created: {address.name} for customer: {party.name}", "Checkout Debug")

		# Update cart quotation with the new address
		try:
			quotation = _get_cart_quotation()
			if quotation:
				frappe.log_error(f"Found quotation: {quotation.name} to update with address {address.name}", "Checkout Debug")

				# Use db_set to update address fields without triggering validation
				quotation.db_set("customer_address", address.name, update_modified=True)
				quotation.db_set("shipping_address_name", address.name, update_modified=False)
				frappe.db.commit()

				frappe.log_error(f"✅ Successfully updated quotation {quotation.name} with addresses - customer_address: {address.name}, shipping_address_name: {address.name}", "Checkout Debug")
			else:
				frappe.log_error(f"⚠️ No quotation found to update with address {address.name}", "Checkout Debug")
		except Exception as addr_update_error:
			# Log but don't fail - address is created successfully
			frappe.log_error(f"❌ Failed to update quotation with address: {str(addr_update_error)}\n{frappe.get_traceback()}", "Checkout Debug")

		return {
			"success": True,
			"address_name": address.name,
			"address_title": address.address_title,
			"display": address.get_display()
		}

	except frappe.exceptions.InvalidPhoneNumberError as e:
		# Pass through phone validation error with clear message
		frappe.throw(_(str(e)))
	except frappe.exceptions.ValidationError as e:
		# Pass through validation errors with clear message
		frappe.throw(_(str(e)))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Checkout: Create Address Error")
		frappe.throw(_("Gagal membuat alamat: {0}").format(str(e)))
  
# @frappe.whitelist()
# def make_payment_request(sales_order_name):
# 	"""
# 	Create a payment request for the given Sales Order

# 	Args:
# 		sales_order_name (str): Name of the Sales Order
#   	"""
# 	from erpnext.accounts.doctype.payment_request.payment_request import make_payment_request

   
