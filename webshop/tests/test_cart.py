# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from webshop.tests.test_base import WebshopTestCase
from webshop.webshop.shopping_cart.cart import (
	get_cart_quotation,
	update_cart,
	update_cart_address,
	apply_shipping_rule,
	apply_coupon_code,
	remove_coupon_code,
	validate_cart_stock,
	_get_cart_quotation,
	get_party,
)
from webshop.webshop.doctype.website_item.website_item import make_website_item


class TestCart(WebshopTestCase):
	"""
	Unit tests for shopping cart functionality.
	Tests cart operations: quotation management, items, addresses, shipping, coupons, stock validation.
	
	Note: Checkout and order placement are tested separately in test_checkout.py
	"""

	def setUp(self):
		"""Set up test data for each test"""
		super().setUp()
		
		# Set user for cart operations
		frappe.set_user("Administrator")
		
		# Create test items and website items
		self._create_test_items()
		
		# Create test customer and user
		self._create_test_customer()
		
		# Login as test customer
		frappe.set_user(self.test_user_email)

	def tearDown(self):
		"""Clean up after each test"""
		frappe.db.rollback()
		frappe.set_user("Administrator")

	def _create_test_items(self):
		"""Create test items for cart testing"""
		# Test Item 1
		if not frappe.db.exists("Item", "_Test Cart Item 1"):
			item1 = frappe.get_doc({
				"doctype": "Item",
				"item_code": "_Test Cart Item 1",
				"item_name": "_Test Cart Item 1",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"standard_rate": 100
			})
			item1.insert(ignore_permissions=True)
			
			# Create Website Item
			if not frappe.db.exists("Website Item", {"item_code": "_Test Cart Item 1"}):
				make_website_item(item1)
			
			# Create Item Price
			if not frappe.db.exists("Item Price", {
				"item_code": "_Test Cart Item 1",
				"price_list": "Standard Selling"
			}):
				frappe.get_doc({
					"doctype": "Item Price",
					"item_code": "_Test Cart Item 1",
					"price_list": "Standard Selling",
					"price_list_rate": 100
				}).insert(ignore_permissions=True)

		# Test Item 2
		if not frappe.db.exists("Item", "_Test Cart Item 2"):
			item2 = frappe.get_doc({
				"doctype": "Item",
				"item_code": "_Test Cart Item 2",
				"item_name": "_Test Cart Item 2",
				"item_group": "All Item Groups",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"standard_rate": 200
			})
			item2.insert(ignore_permissions=True)
			
			# Create Website Item
			if not frappe.db.exists("Website Item", {"item_code": "_Test Cart Item 2"}):
				make_website_item(item2)
			
			# Create Item Price
			if not frappe.db.exists("Item Price", {
				"item_code": "_Test Cart Item 2",
				"price_list": "Standard Selling"
			}):
				frappe.get_doc({
					"doctype": "Item Price",
					"item_code": "_Test Cart Item 2",
					"price_list": "Standard Selling",
					"price_list_rate": 200
				}).insert(ignore_permissions=True)


	def _create_test_customer(self):
		"""Create test customer and user"""
		self.test_user_email = "test_cart_customer@example.com"
		self.test_customer_name = "_Test Cart Customer"
		
		# Create User if not exists - use db operations to bypass validation
		if not frappe.db.exists("User", self.test_user_email):
			user_doc = frappe.get_doc({
				"doctype": "User",
				"email": self.test_user_email,
				"first_name": "Test Cart",
				"last_name": "Customer",
				"enabled": 1
			})
			# Insert with ignore_mandatory to skip required fields
			user_doc.flags.ignore_mandatory = True
			user_doc.flags.ignore_permissions = True
			user_doc.insert()
			
			# Add Customer role via db to avoid validation
			frappe.get_doc({
				"doctype": "Has Role",
				"parent": self.test_user_email,
				"parenttype": "User",
				"parentfield": "roles",
				"role": "Customer"
			}).insert(ignore_permissions=True)

			
		# Create Customer if not exists
		if not frappe.db.exists("Customer", self.test_customer_name):
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": self.test_customer_name,
				"customer_type": "Individual",
				"customer_group": "All Customer Groups",
				"territory": "All Territories"
			})
			customer.insert(ignore_permissions=True)
		
		# Create Contact linking User and Customer
		contact_name = frappe.db.get_value("Contact", {"email_id": self.test_user_email})
		if not contact_name:
			contact = frappe.get_doc({
				"doctype": "Contact",
				"first_name": "Test Cart Customer",
				"email_ids": [{"email_id": self.test_user_email, "is_primary": 1}]
			})
			contact.append("links", {
				"link_doctype": "Customer",
				"link_name": self.test_customer_name
			})
			contact.insert(ignore_permissions=True)
		
		# Create test addresses
		self._create_test_addresses()

	def _create_test_addresses(self):
		"""Create test billing and shipping addresses"""
		# Billing Address
		if not frappe.db.exists("Address", "_Test Billing Address-Cart"):
			billing = frappe.get_doc({
				"doctype": "Address",
				"address_title": "_Test Billing Address",
				"address_type": "Billing",
				"address_line1": "Test Billing Street",
				"city": "Test City",
				"country": "Indonesia"
			})
			# Properly append the Dynamic Link with all required fields
			billing.append("links", {
				"doctype": "Dynamic Link",
				"link_doctype": "Customer",
				"link_name": self.test_customer_name,
				"parenttype": "Address",
				"parentfield": "links"
			})
			billing.insert(ignore_permissions=True)
			self.billing_address_name = billing.name
		else:
			self.billing_address_name = "_Test Billing Address-Cart"
		
		# Shipping Address
		if not frappe.db.exists("Address", "_Test Shipping Address-Cart"):
			shipping = frappe.get_doc({
				"doctype": "Address",
				"address_title": "_Test Shipping Address",
				"address_type": "Shipping",
				"address_line1": "Test Shipping Street",
				"city": "Test City",
				"country": "Indonesia"
			})
			# Properly append the Dynamic Link with all required fields
			shipping.append("links", {
				"doctype": "Dynamic Link",
				"link_doctype": "Customer",
				"link_name": self.test_customer_name,
				"parenttype": "Address",
				"parentfield": "links"
			})
			shipping.insert(ignore_permissions=True)
			self.shipping_address_name = shipping.name
		else:
			self.shipping_address_name = "_Test Shipping Address-Cart"

	def _clear_existing_quotations(self):
		"""Clear existing cart quotations for test user"""
		quotations = frappe.get_all(
			"Quotation",
			filters={
				"contact_email": self.test_user_email,
				"order_type": "Shopping Cart",
				"docstatus": 0
			},
			pluck="name"
		)
		for quot in quotations:
			frappe.delete_doc("Quotation", quot, ignore_permissions=True, force=True)

	# ===== Cart Quotation Management Tests =====

	def test_get_cart_quotation_new_user(self):
		"""Test cart creation for new user (empty cart)"""
		self._clear_existing_quotations()
		
		cart_data = get_cart_quotation()
		
		self.assertIsNotNone(cart_data)
		self.assertIn("doc", cart_data)
		self.assertEqual(cart_data["doc"].order_type, "Shopping Cart")
		self.assertEqual(cart_data["doc"].contact_email, self.test_user_email)
		self.assertEqual(len(cart_data["doc"].items), 0)

	def test_get_cart_quotation_structure(self):
		"""Test cart quotation returns correct data structure"""
		cart_data = get_cart_quotation()
		
		# Verify required keys
		required_keys = ["doc", "shipping_addresses", "billing_addresses", "cart_settings"]
		for key in required_keys:
			self.assertIn(key, cart_data)
		
		# Verify doc is a Quotation
		self.assertEqual(cart_data["doc"].doctype, "Quotation")

	# ===== Item Operations Tests =====

	def test_add_item_to_cart(self):
		"""Test adding a single item to empty cart"""
		self._clear_existing_quotations()
		
		result = update_cart("_Test Cart Item 1", 1)
		
		self.assertIsNotNone(result)
		
		# Verify cart quotation
		quotation = _get_cart_quotation()
		self.assertEqual(len(quotation.items), 1)
		self.assertEqual(quotation.items[0].item_code, "_Test Cart Item 1")
		self.assertEqual(quotation.items[0].qty, 1)
		self.assertEqual(quotation.items[0].rate, 100)

	def test_add_multiple_items(self):
		"""Test adding multiple different items to cart"""
		self._clear_existing_quotations()
		
		# Add first item
		update_cart("_Test Cart Item 1", 2)
		
		# Add second item
		update_cart("_Test Cart Item 2", 3)
		
		# Verify cart has both items
		quotation = _get_cart_quotation()
		self.assertEqual(len(quotation.items), 2)
		
		# Verify first item
		item1 = next((item for item in quotation.items if item.item_code == "_Test Cart Item 1"), None)
		self.assertIsNotNone(item1)
		self.assertEqual(item1.qty, 2)
		
		# Verify second item
		item2 = next((item for item in quotation.items if item.item_code == "_Test Cart Item 2"), None)
		self.assertIsNotNone(item2)
		self.assertEqual(item2.qty, 3)

	def test_update_item_quantity(self):
		"""Test updating quantity of existing item in cart"""
		self._clear_existing_quotations()
		
		# Add item with qty 1
		update_cart("_Test Cart Item 1", 1)
		
		# Update to qty 5
		update_cart("_Test Cart Item 1", 5)
		
		# Verify updated quantity
		quotation = _get_cart_quotation()
		self.assertEqual(len(quotation.items), 1)
		self.assertEqual(quotation.items[0].qty, 5)
		self.assertEqual(quotation.items[0].amount, 500)  # 5 * 100

	def test_remove_item_from_cart(self):
		"""Test removing item from cart by setting qty to 0"""
		self._clear_existing_quotations()
		
		# Add two items
		update_cart("_Test Cart Item 1", 2)
		update_cart("_Test Cart Item 2", 3)
		
		# Remove first item
		update_cart("_Test Cart Item 1", 0)
		
		# Verify only second item remains
		quotation = _get_cart_quotation()
		self.assertEqual(len(quotation.items), 1)
		self.assertEqual(quotation.items[0].item_code, "_Test Cart Item 2")

	def test_remove_last_item_deletes_quotation(self):
		"""Test that removing the last item deletes the quotation"""
		self._clear_existing_quotations()
		
		# Add item
		update_cart("_Test Cart Item 1", 1)
		quotation = _get_cart_quotation()
		quotation_name = quotation.name
		
		# Remove item (cart becomes empty)
		update_cart("_Test Cart Item 1", 0)
		
		# Verify quotation is deleted
		self.assertFalse(frappe.db.exists("Quotation", quotation_name))

	# ===== Address Management Tests =====

	def test_update_billing_address(self):
		"""Test setting billing address on cart"""
		self._clear_existing_quotations()
		
		# Add item first
		update_cart("_Test Cart Item 1", 1)
		
		# Update billing address
		result = update_cart_address("billing", self.billing_address_name)
		
		# Verify address is set
		quotation = _get_cart_quotation()
		self.assertEqual(quotation.customer_address, self.billing_address_name)
		self.assertIsNotNone(quotation.address_display)

	def test_update_shipping_address(self):
		"""Test setting shipping address on cart"""
		self._clear_existing_quotations()
		
		# Add item first
		update_cart("_Test Cart Item 1", 1)
		
		# Update shipping address
		result = update_cart_address("shipping", self.shipping_address_name)
		
		# Verify address is set
		quotation = _get_cart_quotation()
		self.assertEqual(quotation.shipping_address_name, self.shipping_address_name)
		self.assertIsNotNone(quotation.shipping_address)

	# ===== Coupon Code Tests =====

	def test_apply_coupon_code(self):
		"""Test applying valid coupon code to cart"""
		self._clear_existing_quotations()
		
		# Create test coupon
		pricing_rule_name = None
		if not frappe.db.exists("Coupon Code", "TEST10"):
			# Create Pricing Rule first
			if not frappe.db.exists("Pricing Rule", "_Test Cart Discount 10%"):
				pricing_rule = frappe.get_doc({
					"doctype": "Pricing Rule",
					"title": "_Test Cart Discount 10%",
					"apply_on": "Transaction",
					"price_or_product_discount": "Price",
					"selling": 1,
					"applicable_for": "Customer Group",
					"customer_group": "All Customer Groups",
					"discount_percentage": 10,
					"company": "_Test Company",
					"currency": "IDR",
					"coupon_code_based": 1
				})
				pricing_rule.insert(ignore_permissions=True)
				pricing_rule_name = pricing_rule.name
			else:
				pricing_rule_name = frappe.db.get_value("Pricing Rule", {"title": "_Test Cart Discount 10%"}, "name")
			
			# Create Coupon Code with the actual pricing rule name
			coupon = frappe.get_doc({
				"doctype": "Coupon Code",
				"coupon_name": "_Test Cart Discount 10%",
				"coupon_code": "TEST10",
				"pricing_rule": pricing_rule_name,  # Use the actual name, not title
				"valid_from": "2020-01-01",
				"valid_upto": "2030-12-31",
				"maximum_use": 100,
				"used": 0
			})
			coupon.insert(ignore_permissions=True)
		
		# Add item to cart
		update_cart("_Test Cart Item 1", 1)
		
		# Apply coupon
		quotation = apply_coupon_code("TEST10")
		
		# Verify coupon is applied (Frappe stores coupon name, not code)
		self.assertIsNotNone(quotation.coupon_code)
		# Verify discount is applied (net_total should be less than total)
		self.assertLess(quotation.net_total, quotation.total)
		# Verify 10% discount was applied
		self.assertAlmostEqual(quotation.net_total, quotation.total * 0.9, places=2)

	def test_remove_coupon_code(self):
		"""Test removing applied coupon code from cart"""
		# First apply coupon
		self.test_apply_coupon_code()
		
		# Remove coupon
		quotation = remove_coupon_code()
		
		# Verify coupon is removed
		self.assertEqual(quotation.coupon_code, "")
		self.assertEqual(quotation.discount_amount, 0)
		self.assertEqual(quotation.additional_discount_percentage, 0)

	def test_invalid_coupon_code(self):
		"""Test applying invalid coupon code raises error"""
		self._clear_existing_quotations()
		
		# Add item to cart
		update_cart("_Test Cart Item 1", 1)
		
		# Try to apply invalid coupon
		with self.assertRaises(frappe.ValidationError):
			apply_coupon_code("INVALID_COUPON")

	# ===== Stock Validation Tests =====

	def test_validate_cart_stock_available(self):
		"""Test stock validation when allow_items_not_in_stock is enabled"""
		self._clear_existing_quotations()
		
		# Enable allow_items_not_in_stock (should pass regardless of stock)
		frappe.db.set_single_value("Webshop Settings", "allow_items_not_in_stock", 1)
		
		# Add item - should work regardless of actual stock
		update_cart("_Test Cart Item 1", 1)
		
		quotation = _get_cart_quotation()
		
		# Should pass when allow_items_not_in_stock is enabled
		result = validate_cart_stock(quotation.name)
		self.assertTrue(result)

	def test_validate_cart_stock_insufficient(self):
		"""Test stock validation function when configured to check stock"""
		self._clear_existing_quotations()
		
		# Enable allow_items_not_in_stock (won't validate stock)
		frappe.db.set_single_value("Webshop Settings", "allow_items_not_in_stock", 1)
		
		# Add item - should work regardless of stock when allow_items_not_in_stock is enabled
		update_cart("_Test Cart Item 2", 10)
		
		quotation = _get_cart_quotation()
		
		# Should pass when allow_items_not_in_stock is enabled
		result = validate_cart_stock(quotation.name)
		self.assertTrue(result)

