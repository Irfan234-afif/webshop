# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestPaymentRequestWebshop(FrappeTestCase):
	"""Test cases for Webshop Payment Request approval workflow"""

	def setUp(self):
		"""Create test data"""
		# Create test customer
		self.customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": "Test Customer Webshop",
			"customer_group": "All Customer Groups",
			"territory": "All Territories"
		})
		if not frappe.db.exists("Customer", self.customer.customer_name):
			self.customer.insert()
		else:
			self.customer = frappe.get_doc("Customer", self.customer.customer_name)

		# Create test item
		self.item = frappe.get_doc({
			"doctype": "Item",
			"item_code": "Test Item Webshop PR",
			"item_name": "Test Item Webshop PR",
			"item_group": "All Item Groups",
			"is_stock_item": 0
		})
		if not frappe.db.exists("Item", self.item.item_code):
			self.item.insert()
		else:
			self.item = frappe.get_doc("Item", self.item.item_code)

		# Create test payment method
		self.payment_method = frappe.get_doc({
			"doctype": "Webshop Payment Method",
			"payment_method_name": "Test Manual Transfer PR",
			"title": "Test Manual Transfer PR",
			"payment_type": "Transfer Manual",
			"need_admin_approval": 1,
			"enabled": 1
		})
		if not frappe.db.exists("Webshop Payment Method", self.payment_method.payment_method_name):
			self.payment_method.insert()
		else:
			self.payment_method = frappe.get_doc("Webshop Payment Method", self.payment_method.payment_method_name)

		# Create test sales order
		self.sales_order = self._create_test_sales_order()

	def tearDown(self):
		"""Clean up test data"""
		# Delete created payment requests
		frappe.db.delete("Payment Request", {
			"reference_doctype": "Sales Order",
			"reference_name": self.sales_order.name
		})
		frappe.db.commit()

	def _create_test_sales_order(self):
		"""Helper to create a test sales order"""
		so = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": self.customer.name,
			"order_type": "Shopping Cart",
			"payment_method_type": self.payment_method.name,
			"delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),
			"items": [{
				"item_code": self.item.item_code,
				"qty": 1,
				"rate": 100
			}]
		})
		so.insert()
		so.submit()
		return so

	def test_create_payment_request_draft(self):
		"""Test creating Payment Request in Draft status (Pending)"""
		pr = frappe.get_doc({
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"reference_doctype": "Sales Order",
			"reference_name": self.sales_order.name,
			"party_type": "Customer",
			"party": self.customer.name,
			"grand_total": 100,
			"currency": "IDR",
			"company": frappe.defaults.get_defaults().get("company"),
			"mute_email": 1
		})
		pr.insert()

		self.assertEqual(pr.docstatus, 0)  # Draft status
		self.assertTrue(pr.is_webshop_manual_payment())

		# Cleanup
		frappe.delete_doc("Payment Request", pr.name, force=True)

	def test_approve_payment_request_marks_as_paid(self):
		"""Test approving Payment Request (Submit) marks payment as paid"""
		pr = frappe.get_doc({
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"reference_doctype": "Sales Order",
			"reference_name": self.sales_order.name,
			"party_type": "Customer",
			"party": self.customer.name,
			"grand_total": 100,
			"currency": "IDR",
			"company": frappe.defaults.get_defaults().get("company"),
			"mute_email": 1,
			"payment_proof": "/files/test_proof.pdf"
		})
		pr.insert()

		# Approve (Submit)
		pr.submit()

		# Check docstatus
		self.assertEqual(pr.docstatus, 1)  # Submitted (Approved)

		# Check admin metadata
		self.assertEqual(pr.admin_approval_by, frappe.session.user)
		self.assertIsNotNone(pr.admin_approval_time)

		# Cleanup
		pr.cancel()
		frappe.delete_doc("Payment Request", pr.name, force=True)

	def test_reject_payment_request(self):
		"""Test rejecting Payment Request (Cancel)"""
		pr = frappe.get_doc({
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"reference_doctype": "Sales Order",
			"reference_name": self.sales_order.name,
			"party_type": "Customer",
			"party": self.customer.name,
			"grand_total": 100,
			"currency": "IDR",
			"company": frappe.defaults.get_defaults().get("company"),
			"mute_email": 1,
			"remarks": "Test rejection"
		})
		pr.insert()

		# Reject (Cancel)
		pr.cancel()

		# Check docstatus
		self.assertEqual(pr.docstatus, 2)  # Cancelled (Rejected)

		# Cleanup
		frappe.delete_doc("Payment Request", pr.name, force=True)

	def test_upload_payment_proof(self):
		"""Test uploading payment proof updates Payment Request"""
		from webshop.webshop.api.checkout import upload_payment_proof, create_payment_request_for_manual_approval

		# Create Payment Request
		pr = create_payment_request_for_manual_approval(self.sales_order, self.payment_method)

		# Upload proof (simulate user session)
		original_user = frappe.session.user
		frappe.set_user(self.sales_order.contact_email or "Administrator")

		result = upload_payment_proof(
			sales_order=self.sales_order.name,
			file_url="/files/proof.pdf",
			notes="Paid via BCA transfer"
		)

		# Restore user
		frappe.set_user(original_user)

		# Verify
		pr.reload()
		self.assertEqual(pr.payment_proof, "/files/proof.pdf")
		self.assertIn("Paid via BCA transfer", pr.remarks or "")
		self.assertEqual(result["status"], "success")

		# Cleanup
		frappe.delete_doc("Payment Request", pr.name, force=True)

	def test_prevent_duplicate_payment_request(self):
		"""Test that only one Payment Request exists per Sales Order"""
		from webshop.webshop.api.checkout import create_payment_request_for_manual_approval, upload_payment_proof

		# Create first PR
		pr1 = create_payment_request_for_manual_approval(self.sales_order, self.payment_method)

		# Try to upload proof (should update existing PR, not create new one)
		original_user = frappe.session.user
		frappe.set_user(self.sales_order.contact_email or "Administrator")

		result = upload_payment_proof(
			sales_order=self.sales_order.name,
			file_url="/files/proof2.pdf"
		)

		frappe.set_user(original_user)

		# Verify same PR is updated
		self.assertEqual(result["payment_request_id"], pr1.name)

		# Verify only one PR exists
		pr_list = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Order",
				"reference_name": self.sales_order.name
			}
		)
		self.assertEqual(len(pr_list), 1)

		# Cleanup
		frappe.delete_doc("Payment Request", pr1.name, force=True)

	def test_is_webshop_manual_payment(self):
		"""Test is_webshop_manual_payment correctly identifies webshop orders"""
		# Create webshop payment request
		pr = frappe.get_doc({
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"reference_doctype": "Sales Order",
			"reference_name": self.sales_order.name,
			"party_type": "Customer",
			"party": self.customer.name,
			"grand_total": 100,
			"currency": "IDR",
			"company": frappe.defaults.get_defaults().get("company"),
			"mute_email": 1
		})
		pr.insert()

		# Should return True for webshop manual payment
		self.assertTrue(pr.is_webshop_manual_payment())

		# Cleanup
		frappe.delete_doc("Payment Request", pr.name, force=True)

	def test_get_checkout_payment_details(self):
		"""Test get_checkout_payment_details returns correct status mapping"""
		from webshop.webshop.api.checkout import get_checkout_payment_details, create_payment_request_for_manual_approval

		# Create Payment Request
		pr = create_payment_request_for_manual_approval(self.sales_order, self.payment_method)
		pr.payment_proof = "/files/test.pdf"
		pr.save()

		# Get details
		original_user = frappe.session.user
		frappe.set_user(self.sales_order.contact_email or "Administrator")

		details = get_checkout_payment_details(self.sales_order.name)

		frappe.set_user(original_user)

		# Verify status mapping
		self.assertIsNotNone(details["payment_approval"])
		self.assertEqual(details["payment_approval"]["status"], "Pending")  # docstatus=0
		self.assertEqual(details["payment_approval"]["payment_proof"], "/files/test.pdf")

		# Cleanup
		frappe.delete_doc("Payment Request", pr.name, force=True)
