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
	customer = frappe.db.get_value("Customer", {"contact_email": frappe.session.user}, "name")
	if not customer:
		frappe.throw(_("Customer profile not found for your account. Please complete your profile first."))
		
	# Create Member Doc
	member = frappe.new_doc("Cooperative Member")
	member.customer = customer
	
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
	member.status = "Draft"
	
	# Insert documentation
	member.insert(ignore_permissions=True)
	
	return member.name

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
	member.save(ignore_permissions=True)
	
	return {"status": "success", "message": _("Member rejected")}
