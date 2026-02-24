# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class CooperativeMember(Document):
	def before_insert(self):
		if not self.principal_saving_amount or not self.mandatory_saving_amount:
			settings = frappe.get_doc("Cooperative Settings")
			if not settings.principal_saving_amount or not settings.mandatory_saving_amount:
				frappe.throw(_("Cooperative savings amounts are not configured completely in settings."))
				
			self.principal_saving_amount = settings.principal_saving_amount
			self.mandatory_saving_amount = settings.mandatory_saving_amount
			self.total_registration_amount = settings.principal_saving_amount + settings.mandatory_saving_amount
			
		if not self.company:
			settings = frappe.get_doc("Cooperative Settings")
			self.company = settings.company

		if self.company and not self.company_currency:
			self.company_currency = frappe.get_cached_value('Company', self.company, 'default_currency')

		if not self.status:
			self.status = "Draft"

@frappe.whitelist()
def make_payment_request(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	import frappe
	
	def set_missing_values(source, target):
		target.payment_request_type = "Inward"
		target.party_type = "Customer"
		target.party = source.customer
		target.party_name = source.full_name
		target.grand_total = source.total_registration_amount
		target.reference_doctype = "Cooperative Member"
		target.reference_name = source.name
		
		settings = frappe.get_doc("Cooperative Settings")
		target.company = settings.company
		target.currency = frappe.get_cached_value("Company", settings.company, "default_currency")
		target.email_to = source.email or frappe.session.user
		target.mute_email = 1
		target.subject = f"Payment for Cooperative Registration - {source.name}"

	doclist = get_mapped_doc("Cooperative Member", source_name, {
		"Cooperative Member": {
			"doctype": "Payment Request",
			"field_map": {
			}
		}
	}, target_doc, set_missing_values)

	return doclist
