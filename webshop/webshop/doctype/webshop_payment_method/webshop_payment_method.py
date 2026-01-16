# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class WebshopPaymentMethod(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from webshop.webshop.doctype.webshop_payment_channel.webshop_payment_channel import (
			WebshopPaymentChannel,
		)
		from erpnext.accounts.doctype.sales_taxes_and_charges.sales_taxes_and_charges import (
			SalesTaxesandCharges,
		)

		account_holder_name: DF.Data | None
		allow_on_return: DF.Check
		bank_account: DF.Link | None
		description: DF.Text | None
		enabled: DF.Check
		icon: DF.Data | None
		mode_of_payment: DF.Link | None
		need_admin_approval: DF.Check
		payment_channels: DF.Table[WebshopPaymentChannel]
		payment_charges: DF.Table[SalesTaxesandCharges]
		payment_duration: DF.Duration | None
		payment_gateway_account: DF.Link | None
		payment_method_name: DF.Data
		payment_type: DF.Literal["", "Transfer Manual", "Payment Gateway", "Cash"]
		sort_order: DF.Int
		title: DF.Data
	# end: auto-generated types

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


@frappe.whitelist()
def get_payment_method_charges(payment_method_name):
	"""
	Get service charges configured for a payment method (READONLY)
	
	Args:
		payment_method_name: Name of payment method
		
	Returns:
		list: List of charge configurations (Sales Taxes and Charges structure)
	"""
	if not payment_method_name:
		return []
	
	if not frappe.db.exists("Webshop Payment Method", payment_method_name):
		return []
	
	payment_method = frappe.get_doc("Webshop Payment Method", payment_method_name)
	
	charges = []
	for charge in payment_method.payment_charges:
		charges.append({
			"charge_type": charge.charge_type,
			"description": charge.description,
			"rate": charge.rate if charge.charge_type == "On Net Total" else 0,
			"tax_amount": charge.tax_amount if charge.charge_type == "Actual" else 0,
			"account_head": charge.account_head,
			"cost_center": charge.cost_center
		})
	
	return charges