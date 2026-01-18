# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Unit tests for individual bill payment API endpoints
Tests each API function separately with mocked dependencies
"""

import frappe
import unittest
from unittest.mock import patch, MagicMock
from webshop.webshop.api.pay_bill_request import (
	initiate_bill_payment,
	create_payment_request_for_invoice,
	get_payment_url_for_invoice,
	upload_payment_proof
)
from webshop.webshop.api.billing import get_bill_payment_details, get_unpaid_bills


class TestBillPaymentAPIs(unittest.TestCase):
	"""Unit tests for bill payment API endpoints"""
	
	@patch("webshop.webshop.api.pay_bill_request.get_party")
	@patch("frappe.get_doc")
	@patch("frappe.db.exists")
	def test_initiate_bill_payment_validates_input(self, mock_exists, mock_get_doc, mock_get_party):
		"""Test input validation in initiate_bill_payment"""
		
		# Test missing invoice name
		with self.assertRaises(frappe.exceptions.ValidationError):
			initiate_bill_payment(
				sales_invoice_name="",
				payment_method_type="Test Method"
			)
		
		# Test missing payment method
		with self.assertRaises(frappe.exceptions.ValidationError):
			initiate_bill_payment(
				sales_invoice_name="INV-001",
				payment_method_type=""
			)
	
	@patch("webshop.webshop.api.pay_bill_request.get_party")
	@patch("frappe.get_doc")
	@patch("frappe.db.exists")
	def test_initiate_bill_payment_checks_invoice_exists(self, mock_exists, mock_get_doc, mock_get_party):
		"""Test that initiate_bill_payment checks if invoice exists"""
		
		# Mock invoice doesn't exist
		mock_exists.return_value = False
		
		with self.assertRaises(frappe.exceptions.ValidationError):
			initiate_bill_payment(
				sales_invoice_name="NON-EXISTENT",
				payment_method_type="Test Method"
			)
		
		mock_exists.assert_called_with("Sales Invoice", "NON-EXISTENT")
	
	@patch("webshop.webshop.api.pay_bill_request.get_party")
	@patch("frappe.get_doc")
	@patch("frappe.db.exists")
	def test_create_payment_request_sets_payment_method_type(self, mock_exists, mock_get_doc, mock_get_party):
		"""Test that create_payment_request_for_invoice sets payment_method_type field"""
		
		# Mock Sales Invoice
		mock_invoice = MagicMock()
		mock_invoice.name = "INV-001"
		mock_invoice.customer = "Test Customer"
		mock_invoice.customer_name = "Test Customer Name"
		mock_invoice.outstanding_amount = 100000
		mock_invoice.currency = "IDR"
		mock_invoice.company = "_Test Company"
		mock_invoice.contact_email = "test@example.com"
		
		# Mock Payment Method
		mock_payment_method = MagicMock()
		mock_payment_method.name = "Test Manual Transfer"
		mock_payment_method.payment_type = "Transfer Manual"
		mock_payment_method.payment_duration = 86400
		
		# Mock new doc creation
		mock_pr = MagicMock()
		mock_pr.insert = MagicMock()
		
		def mock_new_doc(doctype):
			if doctype == "Payment Request":
				return mock_pr
			return MagicMock()
		
		with patch("frappe.new_doc", side_effect=mock_new_doc):
			result = create_payment_request_for_invoice(
				mock_invoice,
				mock_payment_method
			)
			
			# Verify payment_method_type was set
			self.assertTrue(hasattr(mock_pr, 'payment_method_type'))
			self.assertEqual(mock_pr.payment_method_type, "Test Manual Transfer")
	
	@patch("webshop.webshop.api.billing.get_party")
	@patch("frappe.get_doc")
	@patch("frappe.db.exists")
	def test_get_bill_payment_details_validates_permission(self, mock_exists, mock_get_doc, mock_get_party):
		"""Test that get_bill_payment_details validates user permission"""
		
		# Mock invoice exists
		mock_exists.return_value = True
		
		# Mock invoice with different customer
		mock_invoice = MagicMock()
		mock_invoice.customer = "Other Customer"
		mock_get_doc.return_value = mock_invoice
		
		# Mock party (current user's customer)
		mock_party = MagicMock()
		mock_party.name = "My Customer"
		mock_get_party.return_value = mock_party
		
		# Should throw permission error
		with self.assertRaises(frappe.exceptions.PermissionError):
			get_bill_payment_details("INV-001")
	
	@patch("webshop.webshop.api.billing.get_party")
	@patch("frappe.get_all")
	def test_get_unpaid_bills_filters_by_customer(self, mock_get_all, mock_get_party):
		"""Test that get_unpaid_bills filters by current customer"""
		
		# Mock party
		mock_party = MagicMock()
		mock_party.name = "Test Customer"
		mock_get_party.return_value = mock_party
		
		# Mock invoice data
		mock_get_all.return_value = [
			{
				"name": "INV-001",
				"grand_total": 100000,
				"outstanding_amount": 100000
			}
		]
		
		result = get_unpaid_bills()
		
		# Verify get_all was called with correct customer filter
		call_args = mock_get_all.call_args
		filters = call_args[1]["filters"]
		
		self.assertEqual(filters["customer"], "Test Customer")
		self.assertEqual(filters["docstatus"], 1)
		self.assertEqual(filters["outstanding_amount"], [">", 0])
		self.assertEqual(filters["subscription"], ["is", "set"])
	
	@patch("webshop.webshop.api.pay_bill_request.get_party")
	@patch("frappe.get_doc")
	@patch("frappe.get_all")
	def test_upload_payment_proof_only_updates_draft_pr(self, mock_get_all, mock_get_doc, mock_get_party):
		"""Test that upload_payment_proof only updates Draft Payment Requests"""
		
		# Mock party
		mock_party = MagicMock()
		mock_party.name = "Test Customer"
		mock_get_party.return_value = mock_party
		
		# Mock invoice
		mock_invoice = MagicMock()
		mock_invoice.customer = "Test Customer"
		
		# Mock submitted Payment Request (docstatus=1)
		mock_pr = MagicMock()
		mock_pr.docstatus = 1  # Submitted
		
		def mock_get_doc_side_effect(doctype, name):
			if doctype == "Sales Invoice":
				return mock_invoice
			elif doctype == "Payment Request":
				return mock_pr
			return MagicMock()
		
		mock_get_doc.side_effect = mock_get_doc_side_effect
		
		# Mock get_all to return existing PR
		mock_get_all.return_value = [{"name": "PR-001", "docstatus": 1}]
		
		# Try to upload proof - should not update because PR is submitted
		upload_payment_proof(
			sales_invoice="INV-001",
			file_url="/files/proof.jpg"
		)
		
		# Verify save was NOT called (because docstatus=1)
		mock_pr.save.assert_not_called()
	
	@patch("webshop.webshop.api.pay_bill_request.frappe.get_doc")
	def test_get_payment_url_for_invoice_manual_transfer(self, mock_get_doc):
		"""Test get_payment_url_for_invoice for manual transfer"""
		
		# Mock payment method
		mock_payment_method = MagicMock()
		mock_payment_method.payment_type = "Transfer Manual"
		
		# Mock payment request
		mock_pr = MagicMock()
		mock_pr.docstatus = 0
		
		result = get_payment_url_for_invoice(
			"INV-001",
			mock_payment_method,
			mock_pr
		)
		
		# Verify returns manual redirect type
		self.assertEqual(result["redirect_type"], "manual")
		self.assertEqual(result["payment_url"], "/bills/INV-001/payment")
	
	@patch("frappe.get_doc")
	def test_get_payment_url_for_invoice_gateway(self, mock_get_doc):
		"""Test get_payment_url_for_invoice for payment gateway"""
		
		# Mock payment method
		mock_payment_method = MagicMock()
		mock_payment_method.payment_type = "Payment Gateway"
		
		# Mock payment request
		mock_pr = MagicMock()
		mock_pr.docstatus = 0
		mock_pr.get_payment_url = MagicMock(return_value="https://gateway.com/pay")
		mock_pr.submit = MagicMock()
		
		result = get_payment_url_for_invoice(
			"INV-001",
			mock_payment_method,
			mock_pr
		)
		
		# Verify PR was submitted for gateway
		mock_pr.submit.assert_called_once()
		
		# Verify returns gateway redirect type
		self.assertEqual(result["redirect_type"], "gateway")
		self.assertEqual(result["payment_url"], "https://gateway.com/pay")


class TestPaymentRequestWebshopOverride(unittest.TestCase):
	"""Test Payment Request webshop override for is_webshop_manual_payment"""
	
	def test_is_webshop_manual_payment_checks_payment_method_type_field(self):
		"""Test that is_webshop_manual_payment checks payment_method_type field"""
		
		# We need to test the actual override
		from webshop.webshop.doctype.override_doctype.payment_request import PaymentRequest
		
		# Create mock Payment Request with payment_method_type
		pr = frappe.new_doc("Payment Request")
		pr.__class__ = PaymentRequest  # Use override class
		pr.payment_method_type = "Test Manual Transfer"
		pr.reference_doctype = "Sales Invoice"  # Not Sales Order
		
		# Mock frappe.get_cached_value to return need_admin_approval=1
		with patch("frappe.get_cached_value", return_value=1):
			result = pr.is_webshop_manual_payment()
			
			# Should return True because payment_method_type is set
			self.assertTrue(result)
	
	def test_is_webshop_manual_payment_supports_sales_invoice(self):
		"""Test that is_webshop_manual_payment now supports Sales Invoice"""
		
		from webshop.webshop.doctype.override_doctype.payment_request import PaymentRequest
		
		pr = frappe.new_doc("Payment Request")
		pr.__class__ = PaymentRequest  # Use override class
		pr.payment_method_type = "Test Method"
		pr.reference_doctype = "Sales Invoice"
		pr.reference_name = "INV-001"
		
		with patch("frappe.get_cached_value", return_value=True):
			result = pr.is_webshop_manual_payment()
			
			# Should return True even though reference is Sales Invoice
			self.assertTrue(result)



def run_tests():
	"""Run all API unit tests"""
	unittest.main(module="webshop.tests.test_bill_payment_apis", verbosity=2)


if __name__ == "__main__":
	run_tests()
