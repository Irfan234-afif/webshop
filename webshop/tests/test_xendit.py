import frappe
import unittest
from unittest.mock import patch, MagicMock
from frappe.utils import now_datetime
from webshop.webshop.api.checkout import place_order_with_payment
from webshop.webshop.doctype.xendit_settings.xendit_settings import XenditSettings

class TestXenditIntegration(unittest.TestCase):
	def setUp(self):
		# Patch commit to prevent data persistence
		self.mock_commit = patch("frappe.db.commit")
		self.mock_commit.start()
		
		# Create Company
		if not frappe.db.exists("Company", "_Test Company"):
			frappe.get_doc({
				"doctype": "Company",
				"company_name": "_Test Company",
				"default_currency": "IDR",
				"country": "Indonesia"
			}).insert(ignore_permissions=True)

		# Create User and Customer
		if not frappe.db.exists("User", "test_xendit@example.com"):
			frappe.get_doc({
				"doctype": "User",
				"email": "test_xendit@example.com",
				"first_name": "Test Xendit",
				"enabled": 1,
				"new_password": "password",
				"user_type": "Website User"
			}).insert(ignore_permissions=True)

		if not frappe.db.exists("Customer", "Test Xendit Customer"):
			frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "Test Xendit Customer",
				"customer_type": "Individual",
				"customer_group": "All Customer Groups",
				"territory": "All Territories"
			}).insert(ignore_permissions=True)
			
		# Create Test Item
		if not frappe.db.exists("Item", "Test Checkout Item"):
			frappe.get_doc({
				"doctype": "Item",
				"item_code": "Test Checkout Item",
				"item_name": "Test Checkout Item",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 0,
				"valuation_rate": 100
			}).insert(ignore_permissions=True)

		# Create Website Item
		if not frappe.db.exists("Website Item", {"item_code": "Test Checkout Item"}):
			frappe.get_doc({
				"doctype": "Website Item",
				"web_item_name": "Test Checkout Item",
				"item_code": "Test Checkout Item",
				"item_name": "Test Checkout Item",
				"item_group": "All Item Groups",
				"published": 1
			}).insert(ignore_permissions=True)

		# Create Test Address
		if not frappe.db.exists("Address", "Test Address"):
			address = frappe.get_doc({
				"doctype": "Address",
				"address_title": "Test Address",
				"address_type": "Billing",
				"address_line1": "Test Line 1",
				"city": "Test City",
				"country": "Indonesia",
				"links": [{"link_doctype": "Customer", "link_name": "Test Xendit Customer"}]
			})
			address.insert(ignore_permissions=True)

		# Ensure Payment Gateway Account exists (simplified)
		pga_name = frappe.db.get_value("Payment Gateway Account", {"payment_gateway": "Xendit"}, "name")
		if not pga_name:
			# Create Payment Gateway first
			if not frappe.db.exists("Payment Gateway", "Xendit"):
				frappe.get_doc({"doctype": "Payment Gateway", "gateway": "Xendit"}).insert(ignore_permissions=True)

			pga_doc = frappe.get_doc({
				"doctype": "Payment Gateway Account",
				"payment_gateway": "Xendit",
				"payment_account": "Cash - _TC", # Assuming standard test data
				"currency": "IDR"
			})
			pga_doc.insert(ignore_permissions=True)
			pga_name = pga_doc.name
		
		# Create Configured Payment Method
		if not frappe.db.exists("Webshop Payment Method", "Virtual Account"):
			self.payment_method = frappe.get_doc({
				"doctype": "Webshop Payment Method",
				"payment_method_name": "Virtual Account",
				"title": "Virtual Account",
				"payment_type": "Payment Gateway",
				"payment_gateway_account": pga_name,
				"enabled": 1,
				"payment_channels": [
					{
						"channel_code": "BCA",
						"channel_name": "BCA Virtual Account",
						"description": "Pay via BCA"
					}
				]
			})
			self.payment_method.insert(ignore_permissions=True)

		# Setup Xendit Settings
		if not frappe.db.exists("Xendit Settings", "Xendit Settings"):
			self.xendit_settings = frappe.get_doc({
				"doctype": "Xendit Settings",
				"enabled": 1,
				"test_mode": 1,
				"secret_api_key": "xnd_development_..."
			})
			self.xendit_settings.insert(ignore_permissions=True)
		else:
			self.xendit_settings = frappe.get_doc("Xendit Settings", "Xendit Settings")
			self.xendit_settings.enabled = 1
			self.xendit_settings.save()

		frappe.set_user("test_xendit@example.com")

	def tearDown(self):
		self.mock_commit.stop()
		frappe.set_user("Administrator")

	@patch('requests.post')
	@patch('webshop.webshop.doctype.xendit_settings.xendit_settings.XenditSettings.get_api_key')
	def test_checkout_with_xendit(self, mock_get_api_key, mock_post):
		"""
		Test placing an order with a selected channel (BCA) and triggering Xendit VA creation.
		"""
		mock_get_api_key.return_value = "xnd_development_test_key"
		
		# Mock API Response
		mock_response = MagicMock()
		mock_response.status_code = 200
		mock_response.json.return_value = {
			"external_id": "PR-TEST-1",
			"bank_code": "BCA",
			"account_number": "88000123456",
			"expiration_date": "2025-12-31T23:59:59.000Z",
			"status": "PENDING"
		}
		mock_post.return_value = mock_response

		# Get Address Name
		address_name = frappe.get_value("Address", {"address_title": "Test Address"}, "name")

		# Create Quotation
		quotation = frappe.get_doc({
			"doctype": "Quotation",
			"quotation_to": "Customer",
			"party_name": "Test Xendit Customer",
			"order_type": "Shopping Cart",
			"contact_email": "test_xendit@example.com",
			"items": [{"item_code": "Test Checkout Item", "qty": 1, "rate": 50000}], 
			"payment_method_type": "Virtual Account",
			"pickup_type": "Ambil secara online",
			"customer_address": address_name,
			"shipping_address_name": address_name
		})
		quotation.insert(ignore_permissions=True)

		# Place Order
		result = place_order_with_payment(quotation.name, payment_channel="BCA")

		# Assertions
		self.assertTrue(result.get("sales_order"))
		self.assertEqual(result.get("redirect_type"), "virtual_account")
		self.assertEqual(result.get("virtual_account")["account_number"], "88000123456")

		# Check Sales Order linkage
		so = frappe.get_doc("Sales Order", result.get("sales_order"))
		
		# Check Payment Request
		pr_name = frappe.db.get_value("Payment Request", {"reference_name": so.name}, "name")
		pr = frappe.get_doc("Payment Request", pr_name)
		
		self.assertEqual(pr.payment_channel_code, "BCA")
		self.assertEqual(pr.virtual_account_number, "88000123456")
		self.assertEqual(pr.virtual_account_bank, "BCA")
		self.assertEqual(pr.status, "Requested")
		
		# Verify Mock Call
		mock_post.assert_called_once()
		args, kwargs = mock_post.call_args
		self.assertEqual(kwargs['json']['bank_code'], "BCA")
		self.assertEqual(kwargs['json']['expected_amount'], 50000)

	def test_xendit_webhook(self):
		"""
		Test handling of Xendit webhook to mark Payment Request as Paid.
		"""
		# Create Dummy Sales Order for reference
		so = frappe.get_doc({
			"doctype": "Sales Order",
			"customer": "Test Xendit Customer",
			"company": "_Test Company", # Standard test company
			"transaction_date": now_datetime(),
			"items": [{"item_code": "Test Checkout Item", "qty": 1, "rate": 50000, "delivery_date": now_datetime()}]
		})
		so.insert(ignore_permissions=True)
		
		# Prepare Payment Request
		pr = frappe.get_doc({
			"doctype": "Payment Request",
			"payment_request_type": "Inward",
			"party_type": "Customer",
			"party": "Test Xendit Customer",
			"reference_doctype": "Sales Order", 
			"reference_name": so.name,
			"grand_total": 50000,
			"currency": "IDR",
			"status": "Requested",
			"payment_channel_code": "BCA"
		})
		pr.insert(ignore_permissions=True)
		
		# Create dummy Sales Order to link if needed for 'set_as_paid' logic
		# But 'set_as_paid' usually works if doc is there.
		
		payload = {
			"external_id": pr.name,
			"status": "COMPLETED",
			"id": "py_123456",
			"payment_id": "pay_123456",
			"amount": 50000
		}

		# Call Webhook logic directly
		frappe.request = MagicMock()
		frappe.request.get_json.return_value = payload
		frappe.request.headers = {} # No token for now or mock it if implemented

		# Check token logic in controller
		# If token is set in settings, we must provide it.
		# In setup we didn't set token, so it should pass.
		
		settings = frappe.get_doc("Xendit Settings")
		settings.webhook_token = "secret_token"
		settings.save(ignore_permissions=True)
		frappe.request.headers = {"x-callback-token": "secret_token"}

		# We need to mock 'set_as_paid' because we didn't create a full valid Sales Order structure for it to update
		# or we can trust it fails on 'set_as_paid' execution but verifies the path reaches there.
		# A better way is to check if 'run_method' is called.
		
		# Mocking 'run_method' on the document instance retrieved inside the controller is hard without patching 'get_doc'.
		
		with patch('frappe.get_doc', side_effect=lambda *args: pr if args[0] == 'Payment Request' and args[1] == pr.name else frappe.get_doc(*args)) as mock_get_doc:
			with patch.object(pr, 'run_method') as mock_run_method:
				settings.handle_webhook()
				mock_run_method.assert_called_with("set_as_paid")

