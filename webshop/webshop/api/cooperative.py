# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, get_url

@frappe.whitelist()
def register_member(data):
	"""
	Submit registration form to create Cooperative Member and Payment Request
	
	Args:
		data (str or dict): JSON string or dict of member data
	"""
	if isinstance(data, str):
		import json
		data = json.loads(data)
		
	# Verify user is logged in
	if frappe.session.user == "Guest":
		frappe.throw(_("Please login to register as a cooperative member"))
		
	# Check if already registered
	existing = frappe.get_all(
		"Cooperative Member", 
		filters={"email": frappe.session.user},
		fields=["name", "status"]
	)
	
	if existing:
		frappe.throw(_("You are already registered or have a pending registration"))
		
	# Get Cooperative Settings
	settings = frappe.get_doc("Cooperative Settings")
	if not settings.principal_saving_amount or not settings.mandatory_saving_amount:
		frappe.throw(_("Cooperative savings amounts are not configured completely."))
		
	# Get Customer
	from webshop.webshop.shopping_cart.cart import get_party
	customer_doc = get_party()
	if not customer_doc:
		frappe.throw(_("Customer profile not found for your account. Please complete your profile first."))
	customer_name = customer_doc.name
		
	# Create Member Doc
	member = frappe.new_doc("Cooperative Member")
	member.customer = customer_name
	
	# Mapping fields
	fields_to_map = [
		"nik", "full_name", "place_of_birth", "date_of_birth", "gender",
		"occupation", "marital_status", "email", "phone_number", "relationship_with_cooperative",
		"province", "city", "district", "sub_district", "postal_code", "full_address",
		"emergency_contact_name", "emergency_contact_phone", 
		"emergency_contact_relationship", "emergency_contact_address"
	]
	
	for field in fields_to_map:
		if data.get(field):
			member.set(field, data.get(field))
			
	if data.get("ktp_photo"):
		member.ktp_photo = data.get("ktp_photo")
		
	# Set registration amounts
	member.principal_saving_amount = settings.principal_saving_amount
	member.mandatory_saving_amount = settings.mandatory_saving_amount
	member.total_registration_amount = settings.principal_saving_amount + settings.mandatory_saving_amount
	member.status = "Pending Approval"
	member.workflow_state = "Pending Approval"
	
	# Insert documentation
	member.insert(ignore_permissions=True)
	
	return {"name": member.name, "status": "success"}

@frappe.whitelist()
def get_membership_status():
	"""
	Get current user's membership information
	"""
	if frappe.session.user == "Guest":
		return {"is_member": False}
		
	member = frappe.get_all(
		"Cooperative Member",
		filters={"email": frappe.session.user},
		fields=["name", "status", "total_registration_amount", "principal_saving_amount", "mandatory_saving_amount", "creation"]
	)
	
	if not member:
		return {"is_member": False, "status": "Not Registered"}
		
	member_info = member[0]
	
	# If pending payment, get the payment request details
	if member_info.status == "Pending Payment":
		pr = frappe.get_all(
			"Payment Request",
			filters={"reference_doctype": "Cooperative Member", "reference_name": member_info.name, "docstatus": 0},
			fields=["name"]
		)
		if pr:
			member_info["payment_request"] = pr[0].name
			
	member_info["is_member"] = True
	return member_info

@frappe.whitelist()
def approve_member(member_name):
	"""
	Admin function to approve a member manually (if not done via payment)
	"""
	member = frappe.get_doc("Cooperative Member", member_name)
	
	if member.status == "Active":
		frappe.throw(_("Member is already active"))
		
	if member.status == "Rejected":
		frappe.throw(_("Cannot approve a rejected member"))
		
	member.status = "Active"
	member.workflow_state = "Active"
	# Update approval information if fields existed
	
	member.save(ignore_permissions=True)
	
	# Generate Mandatory Saving record upon approval
	from webshop.webshop.api.cooperative_payment import create_mandatory_saving_for_year
	create_mandatory_saving_for_year(member.name, nowdate()[:4], is_registration=True)
	
	return {"status": "success", "message": _("Member approved successfully")}

@frappe.whitelist()
def reject_member(member_name, reason=None):
	"""
	Admin function to reject a member
	"""
	member = frappe.get_doc("Cooperative Member", member_name)
	
	if member.status == "Active":
		frappe.throw(_("Cannot reject an active member"))
		
	member.status = "Rejected"
	member.workflow_state = "Rejected"
	member.save(ignore_permissions=True)
	
	return {"status": "success", "message": _("Member rejected")}

@frappe.whitelist()
def get_registration_settings():
	"""
	Returns Cooperative Settings for registration fees.
	"""
	settings = frappe.get_doc("Cooperative Settings")
	return {
		"principal_saving_amount": settings.principal_saving_amount,
		"mandatory_saving_amount": settings.mandatory_saving_amount,
		"total_registration_amount": settings.principal_saving_amount + settings.mandatory_saving_amount
	}

@frappe.whitelist()
def get_cooperative_payment_details(member_name):
	"""
	Mock the `CheckoutPaymentDetails` shape so `BankTransferView` can be reused flawlessly.
	It fetches the Payment Request tied to this member registration.
	"""
	member = frappe.get_doc("Cooperative Member", member_name)
	
	pr_records = frappe.get_all(
		"Payment Request",
		filters={
			"reference_doctype": "Cooperative Member",
			"reference_name": member_name,
			"docstatus": ["!=", 2]
		},
		fields=["name", "docstatus", "payment_proof", "remarks", "payment_method_type", "payment_channel_code", "virtual_account_number", "virtual_account_bank", "payment_due_date"],
		limit=1
	)
	
	if not pr_records:
		frappe.throw(_("Payment Request is not found for this member."))
		
	pr = pr_records[0]
	
	# Fetch the payment method details
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
		
	# Approval mapping
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

	# Create a mock 'sales_order'
	sales_order_mock = {
		"name": member.name,
		"customer": member.full_name,
		"grand_total": member.total_registration_amount,
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
def upload_cooperative_payment_proof(member_name, file_url, notes=None):
	"""
	Uploads payment proof onto the Payment Request for the cooperative member.
	"""
	pr_records = frappe.get_all(
		"Payment Request",
		filters={
			"reference_doctype": "Cooperative Member",
			"reference_name": member_name,
			"docstatus": ["in", [0, 1]]
		},
		fields=["name", "docstatus", "remarks"],
		limit=1
	)
	
	if not pr_records:
		frappe.throw(_("Active Payment Request not found."))
		
	pr_name = pr_records[0].name
	pr_doc = frappe.get_doc("Payment Request", pr_name)
	
	if pr_doc.docstatus == 0:
		pr_doc.payment_proof = file_url
		if notes:
			current_remarks = pr_doc.remarks or ""
			pr_doc.remarks = (current_remarks + "\\n\\n" + notes) if current_remarks else notes
			
		pr_doc.save(ignore_permissions=True)
		frappe.db.commit()
		return {"status": "success", "message": "Bukti pembayaran berhasil diupload"}
	else:
		frappe.throw(_("Payment Request has already been submitted or processed."))
