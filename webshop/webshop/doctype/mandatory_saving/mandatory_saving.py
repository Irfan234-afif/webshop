# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class MandatorySaving(Document):
	def validate(self):
		self.calculate_totals()
		
	def calculate_totals(self):
		total_paid = 0
		total_unpaid = 0
		
		for row in self.get("monthly_details"):
			if row.status == "Paid":
				total_paid += flt(row.amount)
			else:
				total_unpaid += flt(row.amount)
				
		self.total_paid = total_paid
		self.total_unpaid = total_unpaid


@frappe.whitelist()
def make_payment_request(doc_name, months, payment_method_type):
	"""
	Create a Payment Request for selected unpaid months
	"""
	doc = frappe.get_doc("Mandatory Saving", doc_name)
	settings = frappe.get_cached_doc("Cooperative Settings")
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)
	
	if isinstance(months, str):
		import json
		months = json.loads(months)
		
	months = [int(m) for m in months]
	
	total_amount = 0
	rows_to_update = []
	
	for row in doc.get("monthly_details"):
		if row.month in months:
			if row.status != "Unpaid":
				frappe.throw(_("Month {0} is already {1}").format(row.month_name, row.status))
			total_amount += flt(row.amount)
			rows_to_update.append(row)
			
	if total_amount == 0:
		frappe.throw(_("No valid unpaid months selected"))
		
	# Create Payment Request
	pr = frappe.new_doc("Payment Request")
	pr.payment_request_type = "Inward"
	pr.reference_doctype = "Mandatory Saving"
	pr.reference_name = doc.name
	pr.party_type = "Customer"
	pr.party = doc.customer
	
	# Fetch party name from Cooperative Member
	member = frappe.get_cached_value("Cooperative Member", doc.cooperative_member, "full_name")
	pr.party_name = member
	
	pr.grand_total = total_amount
	pr.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
	pr.company = settings.company
	
	if hasattr(pr, 'payment_method_type'):
		pr.payment_method_type = payment_method.name
		
	if hasattr(pr, 'mode_of_payment') and payment_method.mode_of_payment:
		pr.mode_of_payment = payment_method.mode_of_payment
		
	if hasattr(pr, 'payment_gateway_account') and payment_method.payment_gateway_account:
		pr.payment_gateway_account = payment_method.payment_gateway_account
		
	pr.mute_email = 1
	pr.subject = f"Payment for Mandatory Saving - {doc.name}"
	
	pr.insert(ignore_permissions=True)
	
	# Update rows
	for row in rows_to_update:
		row.status = "Pending Payment"
		row.payment_request = pr.name
		
	doc.save(ignore_permissions=True)
	
	return pr.name
