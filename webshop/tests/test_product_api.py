
import frappe
from webshop.tests.test_base import WebshopTestCase
from webshop.webshop.api.products import get_items_home, get_products

class TestProductAPI(WebshopTestCase):
	def setUp(self):
		super().setUp()
		self.create_test_items()

	def create_test_items(self):
		# Create Item Group if not exists
		if not frappe.db.exists("Item Group", "Test Group"):
			frappe.get_doc({
				"doctype": "Item Group",
				"item_group_name": "Test Group",
				"parent_item_group": "All Item Groups",
				"is_group": 0,
				"show_in_website": 1
			}).insert(ignore_permissions=True)

		# Create Test Item 1
		item_code = "TEST-ITEM-1"
		if not frappe.db.exists("Item", item_code):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": item_code,
				"item_name": "Test Item 1",
				"item_group": "Test Group",
				"stock_uom": "Nos",
				"is_stock_item": 1,
				"valuation_rate": 100,
				"opening_stock": 10,
				"description": "Test Item Description",
				"show_in_website": 1,
				"website_warehouse": "_Test Warehouse - _TC"
			}).insert(ignore_permissions=True)
			
			# Create Item Price
			frappe.get_doc({
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": "Standard Selling",
				"price_list_rate": 150
			}).insert(ignore_permissions=True)


			# Create Website Item manually if not created by hook
			if not frappe.db.exists("Website Item", {"item_code": item_code}):
				frappe.get_doc({
					"doctype": "Website Item",
					"web_item_name": "Test Item 1",
					"item_code": item_code,
					"item_group": "Test Group",
					"route": "test-item-1",
					"published": 1
				}).insert(ignore_permissions=True)

		# Create Test Item 2
		item_code_2 = "TEST-ITEM-2"
		if not frappe.db.exists("Item", item_code_2):
			item2 = frappe.get_doc({
				"doctype": "Item",
				"item_code": item_code_2,
				"item_name": "Test Item 2",
				"item_group": "Test Group",
				"stock_uom": "Nos", 
				"is_stock_item": 1,
				"valuation_rate": 200,
				"opening_stock": 20,
				"description": "Test Item 2 Description",
				"show_in_website": 1,
				"website_warehouse": "_Test Warehouse - _TC"
			}).insert(ignore_permissions=True)

			# Create Item Price
			frappe.get_doc({
				"doctype": "Item Price",
				"item_code": item_code_2,
				"price_list": "Standard Selling",
				"price_list_rate": 250
			}).insert(ignore_permissions=True)

			# Create Website Item manually
			if not frappe.db.exists("Website Item", {"item_code": item_code_2}):
				frappe.get_doc({
					"doctype": "Website Item",
					"web_item_name": "Test Item 2",
					"item_code": item_code_2,
					"item_group": "Test Group",
					"route": "test-item-2",
					"published": 1
				}).insert(ignore_permissions=True)


		

	def test_get_items_home(self):
		# Test basic home list retrieval
		result = get_items_home()
		
		# Check structure
		self.assertIn("items", result)
		self.assertIn("items_count", result)
		self.assertIn("discounts", result)
		
		# Check content
		items_map = result.get("items")
		self.assertIsInstance(items_map, dict)
		
		# Verify Test Group is present
		if "Test Group" in items_map:
			items = items_map["Test Group"]
			self.assertTrue(len(items) > 0)
			item_codes = [item.get("item_code") for item in items]
			self.assertIn("TEST-ITEM-1", item_codes)
			self.assertIn("TEST-ITEM-2", item_codes)

	def test_get_products(self):
		# Test fetching all products - TRY WITHOUT search first
		result = get_products(item_group="Test Group")

		self.assertIsInstance(result, dict)
		items = result.get("items", [])
		item_codes = [item.get("item_code") for item in items]
		
		# Ensure items are found
		self.assertIn("TEST-ITEM-1", item_codes)
		self.assertIn("TEST-ITEM-2", item_codes)

		# Test filtering by Price Min
		result_min = get_products(item_group="Test Group", price_min=200)
		items_min = result_min.get("items", [])
		# Should include TEST-ITEM-2 (price 250) but not TEST-ITEM-1 (price 150)
		self.assertTrue(any(i.get("item_code") == "TEST-ITEM-2" for i in items_min))
		self.assertFalse(any(i.get("item_code") == "TEST-ITEM-1" for i in items_min))
