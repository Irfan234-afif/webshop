# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WebshopPaymentMethod(Document):
	def validate(self):
		# Validate that for Transfer Manual, bank account and account holder name are provided
		if self.payment_type == "Transfer Manual":
			if not self.bank_account:
				frappe.throw(_("Bank Account is required for Transfer Manual payment type"))
			if not self.account_holder_name:
				frappe.throw(_("Account Holder Name is required for Transfer Manual payment type"))
		
		# Validate that for Payment Gateway, payment gateway account is provided
		elif self.payment_type == "Payment Gateway":
			if not self.payment_gateway_account:
				frappe.throw(_("Payment Gateway Account is required for Payment Gateway payment type"))
		
		# Validate Mode of Payment - warning only for backward compatibility
		if self.enabled and not self.mode_of_payment:
			frappe.msgprint(
				_("Mode of Payment is not set. Payment Entry may not have correct GL Account mapping."),
				indicator="orange",
				alert=True
			)