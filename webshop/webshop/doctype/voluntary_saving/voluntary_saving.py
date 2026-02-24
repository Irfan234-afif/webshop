# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import nowdate

class VoluntarySaving(Document):
	def validate(self):
		if self.transaction_type == "Withdrawal":
			member = frappe.get_doc("Cooperative Member", self.cooperative_member)
			if self.amount > member.voluntary_saving_balance:
				frappe.throw(_("Withdrawal amount cannot exceed available balance ({0})").format(member.voluntary_saving_balance))
				
	def on_submit(self):
		if self.transaction_type == "Withdrawal":
			# Create JE directly for withdrawal
			settings = frappe.get_cached_doc("Cooperative Settings")
			member = frappe.get_doc("Cooperative Member", self.cooperative_member)
			company = member.company or settings.company
			
			je = frappe.new_doc("Journal Entry")
			je.voucher_type = "Bank Entry"
			je.company = company
			je.posting_date = nowdate()
			je.user_remark = f"Withdrawal for Voluntary Saving {self.name}"
			
			if not settings.default_bank_account:
				frappe.throw(_("Please set a Default Bank Account in Cooperative Settings"))
				
			# Row 1: Debit Voluntary Saving Account (liability decreases)
			je.append("accounts", {
				"account": settings.voluntary_saving_account,
				"debit_in_account_currency": self.amount,
				"credit_in_account_currency": 0,
			})
			
			# Row 2: Credit Bank Account (asset decreases)
			je.append("accounts", {
				"account": settings.default_bank_account,
				"debit_in_account_currency": 0,
				"credit_in_account_currency": self.amount,
			})
			
			je.insert(ignore_permissions=True)
			je.submit()
			
			# Update member balance
			member.voluntary_saving_balance -= self.amount
			member.save(ignore_permissions=True)
			
			self.db_set("status", "Approved", update_modified=False)
			self.db_set("payment_date", nowdate(), update_modified=False)
			self.db_set("journal_entry", je.name, update_modified=False)
			
		elif self.transaction_type == "Deposit":
			self.db_set("status", "Pending Payment", update_modified=False)

@frappe.whitelist()
def make_payment_request(doc_name, payment_method_type):
	"""
	Create a Payment Request for Voluntary Saving Deposit
	"""
	doc = frappe.get_doc("Voluntary Saving", doc_name)
	settings = frappe.get_cached_doc("Cooperative Settings")
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_type)
	
	if doc.transaction_type != "Deposit":
		frappe.throw(_("Payment Request can only be created for Deposits"))
		
	# Create Payment Request
	pr = frappe.new_doc("Payment Request")
	pr.payment_request_type = "Inward"
	pr.reference_doctype = "Voluntary Saving"
	pr.reference_name = doc.name
	pr.party_type = "Customer"
	pr.party = doc.customer
	
	# Fetch party name from Cooperative Member
	member = frappe.get_cached_value("Cooperative Member", doc.cooperative_member, "full_name")
	pr.party_name = member
	
	pr.grand_total = doc.amount
	pr.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
	pr.company = settings.company
	
	if hasattr(pr, 'payment_method_type'):
		pr.payment_method_type = payment_method.name
		
	if hasattr(pr, 'mode_of_payment') and payment_method.mode_of_payment:
		pr.mode_of_payment = payment_method.mode_of_payment
		
	if hasattr(pr, 'payment_gateway_account') and payment_method.payment_gateway_account:
		pr.payment_gateway_account = payment_method.payment_gateway_account
		
	pr.mute_email = 1
	pr.subject = f"Payment for Voluntary Saving Deposit - {doc.name}"
	
	pr.insert(ignore_permissions=True)
	
	doc.db_set("payment_request", pr.name, update_modified=False)
	
	return pr.name
