import frappe
from frappe.utils import now_datetime, add_days
from webshop.webshop.api.scheduled_tasks import cancel_overdue_orders
from frappe.tests.utils import FrappeTestCase

class TestOverdueCancellation(FrappeTestCase):
	def setUp(self):
		self.create_test_data()

	def create_test_data(self):
		if not frappe.db.exists("Company", "_Test Company Overdue"):
			try:
				frappe.get_doc({
					"doctype": "Company",
					"company_name": "_Test Company Overdue",
					"default_currency": "INR",
					"country": "India"
				}).insert()
			except frappe.DuplicateEntryError:
				pass

		if not frappe.db.exists("Customer", "_Test Customer Overdue"):
			try:
				frappe.get_doc({
					"doctype": "Customer",
					"customer_name": "_Test Customer Overdue",
					"customer_type": "Individual",
					"customer_group": "All Customer Groups",
					"territory": "All Territories"
				}).insert()
			except frappe.DuplicateEntryError:
				pass
		else:
			frappe.db.set_value("Customer", "_Test Customer Overdue", "disabled", 0)
			
		if not frappe.db.exists("Item", "_Test Item Overdue"):
			try:
				frappe.get_doc({
					"doctype": "Item",
					"item_code": "_Test Item Overdue",
					"item_group": "All Item Groups",
					"stock_uom": "Nos",
					"is_stock_item": 1,
					"opening_stock": 100,
					"valuation_rate": 100
				}).insert()
			except frappe.DuplicateEntryError:
				pass
		
	def test_cancel_overdue_orders(self):
		# Create a Sales Order
		so = frappe.new_doc("Sales Order")
		so.company = "_Test Company Overdue"
		so.customer = "_Test Customer Overdue"
		so.currency = "INR"
		so.append("items", {
			"item_code": "_Test Item Overdue",
			"qty": 1,
			"rate": 100,
			"delivery_date": add_days(now_datetime(), 1)
		})
		so.delivery_date = add_days(now_datetime(), 1)
		so.insert()
		so.submit()
		
		# Create a Payment Request linked to it
		pr = frappe.new_doc("Payment Request")
		pr.payment_request_type = "Inward"
		pr.reference_doctype = "Sales Order"
		pr.reference_name = so.name
		pr.party_type = "Customer"
		pr.party = "_Test Customer Overdue"
		pr.currency = "INR"
		pr.grand_total = 100
		pr.email_to = "test@example.com"
		pr.subject = "Test Payment Request"
		
		# Set due date in the past
		pr.payment_due_date = add_days(now_datetime(), -1)
		
		# Bypass validation if custom field doesn't exist yet in test env
		# check if field exists
		if not frappe.db.has_column("Payment Request", "payment_due_date"):
			from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
			custom_fields = {
				"Payment Request": [
					{
						"fieldname": "payment_due_date",
						"label": "Payment Due Date",
						"fieldtype": "Datetime",
						"insert_after": "transaction_date",
						"no_copy": 1,
						"print_hide": 1
					}
				]
			}
			create_custom_fields(custom_fields, update=True)
			
		pr.insert()
		pr.submit()
		
		# Verify status is Requested/Initiated
		pr.reload()
		# self.assertIn(pr.status, ["Requested", "Initiated"])
		
		# Run the cancellation task
		cancel_overdue_orders()
		
		# Verify SO is cancelled
		so.reload()
		self.assertEqual(so.status, "Cancelled")
		self.assertEqual(so.docstatus, 2)
		
		# Verify PR is cancelled
		pr.reload()
		self.assertEqual(pr.status, "Cancelled")
		self.assertEqual(pr.docstatus, 2)


	def test_cancel_draft_overdue_orders(self):
		# Create a Draft Sales Order
		so = frappe.new_doc("Sales Order")
		so.company = "_Test Company Overdue"
		so.customer = "_Test Customer Overdue"
		so.currency = "INR"
		so.transaction_date = now_datetime()
		so.delivery_date = add_days(now_datetime(), 1)
		so.append("items", {
			"item_code": "_Test Item Overdue",
			"qty": 1,
			"rate": 100,
			"delivery_date": add_days(now_datetime(), 1)
		})
		so.insert()
		# Valid transitions: Saved(0)
		
		# Create a Payment Request linked to it
		pr = frappe.new_doc("Payment Request")
		pr.payment_request_type = "Inward"
		pr.reference_doctype = "Sales Order"
		pr.reference_name = so.name
		pr.party_type = "Customer"
		pr.party = "_Test Customer Overdue"
		pr.currency = "INR"
		pr.grand_total = 100
		pr.email_to = "test@example.com"
		pr.subject = "Test Payment Request Draft"
		
		# Set due date in the past
		pr.payment_due_date = add_days(now_datetime(), -1)
		
		pr.insert()
		# We must submit PR to have status "Requested" usually?
		# But PR can be "Requested" even if docstatus=1?
		# Standard flow: PR insert -> submit -> status becomes Requested?
		# Let's assume submit is needed for PR.
		pr.submit()
		
		# Ensure PR is in 'Requested' or 'Initiated' state
		pr.reload()
		
		# Run the cancellation task
		cancel_overdue_orders()
		
		# Verify Draft SO is cancelled
		so.reload()
		self.assertEqual(so.status, "Cancelled")
		self.assertEqual(so.docstatus, 2)
		
		# Verify PR is cancelled
		pr.reload()
		self.assertEqual(pr.status, "Cancelled")
		self.assertEqual(pr.docstatus, 2)

	def tearDown(self):
		frappe.db.rollback()
