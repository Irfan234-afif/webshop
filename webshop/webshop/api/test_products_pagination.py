import frappe
from frappe.tests.utils import FrappeTestCase
from webshop.webshop.api.products import get_products
from webshop.webshop.doctype.website_item.test_website_item import create_regular_web_item

class TestProductsPagination(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		# Create dummy products
		cls.created_items = []
		for i in range(25):
			item_code = f"Test_Pagination_Item_{i}"
			if not frappe.db.exists("Item", item_code):
				create_regular_web_item(item_code)
				cls.created_items.append(item_code)

	@classmethod
	def tearDownClass(cls):
		for item_code in cls.created_items:
			if frappe.db.exists("Website Item", {"item_code": item_code}):
				frappe.get_doc("Website Item", {"item_code": item_code}).delete()
			if frappe.db.exists("Item", item_code):
				frappe.get_doc("Item", item_code).delete()
		super().tearDownClass()

	def test_get_products_pagination(self):
		# Fetch page 1 (10 items)
		result_page_1 = get_products(start=0, page_length=10, search_term="Test_Pagination_Item_")
		self.assertEqual(len(result_page_1["items"]), 10)
		self.assertTrue(result_page_1["pagination"]["has_more"])
		self.assertEqual(result_page_1["pagination"]["next_start"], 10)

		# Fetch page 2 (10 items)
		result_page_2 = get_products(start=10, page_length=10, search_term="Test_Pagination_Item_")
		self.assertEqual(len(result_page_2["items"]), 10)
		self.assertTrue(result_page_2["pagination"]["has_more"])
		self.assertEqual(result_page_2["pagination"]["next_start"], 20)

		# Verify items are different
		ids_page_1 = [item.item_code for item in result_page_1["items"]]
		ids_page_2 = [item.item_code for item in result_page_2["items"]]
		self.assertTrue(set(ids_page_1).isdisjoint(set(ids_page_2)))

		# Fetch page 3 (remaining 5 items)
		result_page_3 = get_products(start=20, page_length=10, search_term="Test_Pagination_Item_")
		self.assertEqual(len(result_page_3["items"]), 5)
		self.assertFalse(result_page_3["pagination"]["has_more"])
