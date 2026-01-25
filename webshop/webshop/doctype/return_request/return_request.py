# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, add_days, nowdate


class ReturnRequest(Document):
	"""Return Request DocType for handling sales returns"""
	
	def validate(self):
		"""Validate return request before saving"""
		self.validate_refund_payment_mode()
		self.validate_bank_details()
		self.validate_other_reason()
		self.validate_sales_order_delivered()
		self.validate_return_window()
		self.validate_duplicate_return()
	
	def before_insert(self):
		"""Auto-populate fields before insert"""
		self.populate_customer_and_documents()
		self.populate_items_from_sales_order()
	
	def on_submit(self):
		"""Update status when submitted"""
		self.status = "Approved"
		self.save()
	
	def on_cancel(self):
		"""Update status when cancelled"""
		self.status = "Rejected"
		self.save()
	
	def validate_refund_payment_mode(self):
		"""Validate refund payment mode has allow_on_return enabled"""
		if self.refund_payment_mode:
			payment_method = frappe.get_doc("Webshop Payment Method", self.refund_payment_mode)
			if not payment_method.get("allow_on_return"):
				frappe.throw(_("Selected payment method {0} is not allowed for returns").format(
					frappe.bold(self.refund_payment_mode)
				))
	
	def validate_bank_details(self):
		"""Validate bank details if payment type is Transfer Manual"""
		if self.refund_payment_mode:
			payment_method = frappe.get_doc("Webshop Payment Method", self.refund_payment_mode)
			if payment_method.payment_type == "Transfer Manual":
				if not self.bank_name:
					frappe.throw(_("Bank Name is required for Transfer Manual payment method"))
				if not self.account_number:
					frappe.throw(_("Account Number is required for Transfer Manual payment method"))
				if not self.account_holder_name:
					frappe.throw(_("Account Holder Name is required for Transfer Manual payment method"))
	
	def validate_other_reason(self):
		"""Validate other_reason is provided if return_reason is 'Other'"""
		if self.return_reason == "Other" and not self.other_reason:
			frappe.throw(_("Please provide details in 'Other Reason' field"))
	
	def validate_sales_order_delivered(self):
		"""Validate that sales order has been delivered"""
		if self.sales_order:
			# Check if delivery note exists and is submitted
			delivery_notes = frappe.get_all("Delivery Note Item",
				filters={
					"against_sales_order": self.sales_order,
					"docstatus": 1
				},
				fields=["parent"]
			)
			
			if not delivery_notes:
				frappe.throw(_("Sales Order {0} has not been delivered yet").format(
					frappe.bold(self.sales_order)
				))
	
	def validate_return_window(self):
		"""Validate return is within eligibility window"""
		if not self.delivery_note:
			return
		
		# Get return eligibility days from settings
		settings = frappe.get_single("Webshop Settings")
		eligibility_days = settings.return_eligibility_days or 7
		
		# Get delivery date
		delivery_date = frappe.db.get_value("Delivery Note", self.delivery_note, "posting_date")
		
		if delivery_date:
			cutoff_date = add_days(delivery_date, eligibility_days)
			today = getdate(nowdate())
			
			if today > getdate(cutoff_date):
				frappe.throw(_("Return window has expired. Returns are allowed within {0} days of delivery").format(
					eligibility_days
				))
	
	def validate_duplicate_return(self):
		"""Validate no duplicate return request for same sales order"""
		if self.is_new():
			existing = frappe.db.exists("Return Request", {
				"sales_order": self.sales_order,
				"docstatus": ["!=", 2],  # Not cancelled
				"name": ["!=", self.name]
			})
			
			if existing:
				frappe.throw(_("Return Request already exists for Sales Order {0}").format(
					frappe.bold(self.sales_order)
				))
	
	def populate_customer_and_documents(self):
		"""Auto-populate customer, sales_invoice, and delivery_note from sales order"""
		if self.sales_order:
			so = frappe.get_doc("Sales Order", self.sales_order)
			self.customer = so.customer
			
			# Get Sales Invoice
			invoices = frappe.get_all("Sales Invoice Item",
				filters={
					"sales_order": self.sales_order,
					"docstatus": 1
				},
				fields=["parent"],
				limit=1
			)
			if invoices:
				self.sales_invoice = invoices[0].parent
			
			# Get Delivery Note
			delivery_notes = frappe.get_all("Delivery Note Item",
				filters={
					"against_sales_order": self.sales_order,
					"docstatus": 1
				},
				fields=["parent"],
				limit=1
			)
			if delivery_notes:
				self.delivery_note = delivery_notes[0].parent
	
	def populate_items_from_sales_order(self):
		"""Auto-populate all items from sales order"""
		self.items = []
		if self.sales_order:
			so = frappe.get_doc("Sales Order", self.sales_order)
			
			for item in so.items:
				self.append("items", {
					"sales_order_item": item.name,
					"item_code": item.item_code,
					"item_name": item.item_name,
					"qty": item.qty,
					"rate": item.rate,
					"amount": item.amount
				})

@frappe.whitelist()
def make_return_delivery_note(source_name, target_doc=None):
	from erpnext.stock.doctype.delivery_note.delivery_note import make_sales_return
	
	return_request = frappe.get_doc("Return Request", source_name)
	target_doc = make_sales_return(return_request.delivery_note, target_doc)
	
	# Set issue_credit_note to 1
	target_doc.issue_credit_note = 1
	
	# Set return_request field
	target_doc.return_request = return_request.name
	
	# Map items from Return Request
	doc = filter_return_items(return_request, target_doc)
	
	return doc

def filter_return_items(return_request, target_doc):
	"""Filter items in target_doc to match Return Request items and quantities"""
	items_to_return = {item.item_code: item.qty for item in return_request.items}
	final_items = []
	
	for item in target_doc.items:
		if item.item_code in items_to_return:
			# Set quantity to negative (as per ERPNext return convention)
			# standard make_sales_return sets it to negative available qty
			# we override it with our requested return qty
			return_qty = items_to_return[item.item_code]
			item.qty = -1 * abs(return_qty)
			
			# Recalculate amount if rate exists
			if item.rate:
				item.amount = item.qty * item.rate
				
			final_items.append(item)
	
	target_doc.items = final_items
	
	# Set other fields if needed
	return target_doc

def update_return_request_on_dn_submit(doc, method):
	"""Update Return Request when Return Delivery Note is submitted"""
	if doc.is_return and doc.get("return_request"):
		rr = frappe.get_doc("Return Request", doc.return_request)
		rr.return_delivery_note = doc.name
		
		# Check if Credit Note is also created (might be created later)
		if rr.credit_note:
			rr.status = "Completed"
		else:
			rr.status = "Processing"
			
		rr.save(ignore_permissions=True)

def update_return_request_on_si_submit(doc, method):
	"""Update Return Request when Return Sales Invoice (Credit Note) is submitted"""
	if doc.is_return and doc.get("return_request"):
		rr = frappe.get_doc("Return Request", doc.return_request)
		rr.credit_note = doc.name
		
		# Check if Return Delivery Note is also created
		if rr.return_delivery_note:
			rr.status = "Completed"
		else:
			# If only Credit Note created (some flows might skip DN?), allow completion?
			# Usually need both for full return if DN was involved. 
			# But for now assume "Processing" unless both present if DN expected.
			# If original sales order skipped DN (service item), maybe logic differs.
			# Stick to checking both for now as per requirement.
			rr.status = "Completed" if rr.return_delivery_note else "Processing"
			
		rr.save(ignore_permissions=True)
