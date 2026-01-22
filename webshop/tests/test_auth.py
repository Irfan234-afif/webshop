# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from webshop.tests.test_base import WebshopTestCase
from webshop.webshop.api.auth import register, login

class TestAuth(WebshopTestCase):
	def setUp(self):
		# Create a dummy School Unit for testing
		if not frappe.db.exists("School Unit", "Test School Unit"):
			frappe.get_doc({
				"doctype": "School Unit",
				"unit_name": "Test School Unit",
				"unit_code": "Test School Unit"
			}).insert(ignore_permissions=True)
			
		# Ensure a known customer group exists and is set in Webshop Settings
		if not frappe.db.exists("Customer Group", "Test Group"):
			frappe.get_doc({
				"doctype": "Customer Group",
				"customer_group_name": "Test Group",
				"is_group": 0
			}).insert(ignore_permissions=True)
			
		frappe.db.set_single_value("Webshop Settings", "default_customer_group", "Test Group")

	def tearDown(self):
		# Clean up created data to avoid loose ends (though FrappeTestCase usually handles rollback)
		frappe.db.rollback()

	def test_register_success(self):
		email = "test_user_unique@example.com"
		name = "Test User Unique"
		phone = "081234567890"
		password = "password123"
		
		address = {
			"address_line1": "Jalan Test No. 1",
			"city": "Jakarta",
			"country": "Indonesia",
			"postal_code": "12345"
		}
		
		students = [
			{
				"student_name": "Test Student 1",
				"school_unit": "Test School Unit"
			}
		]

		# Aggressive cleanup
		frappe.db.delete("User", {"email": email})
		frappe.db.delete("Customer", {"customer_name": name})
		contact_names = frappe.db.sql("""select parent from `tabContact Email` where email_id=%s""", email, pluck=True)
		for c in contact_names:
			frappe.delete_doc("Contact", c, force=True, ignore_permissions=True)
			
		# Clean up any students with this name
		frappe.db.delete("Student", {"student_name": "Test Student 1"})

		# Clean up User if it still exists (delete_doc vs db.delete)
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True, ignore_permissions=True)
		
		frappe.set_user("Guest")
		result = register(
			name=name,
			email=email,
			phone_number=phone,
			password=password,
			address=address,
			students=students
		)

		self.assertTrue(result["success"])
		self.assertEqual(result["user"]["email"], email)
		self.assertEqual(result["customer"]["customer_name"], name)
		
		# Verify User
		self.assertTrue(frappe.db.exists("User", email))
		user_doc = frappe.get_doc("User", email)
		
		# Verify Customer linkage
		customer_name = result["customer"]["name"]
		self.assertTrue(frappe.db.exists("Customer", customer_name))
		customer_doc = frappe.get_doc("Customer", customer_name)
		self.assertEqual(customer_doc.customer_group, "Test Group")
		
		# Verify Portal User Link
		self.assertTrue(any(u.user == user_doc.name for u in customer_doc.portal_users))

		# Verify Contact
		# Should be able to find contact via email
		contact_name = frappe.db.get_value("Contact", {"email_id": email}, "name")
		self.assertTrue(contact_name)
		contact_doc = frappe.get_doc("Contact", contact_name)
		
		# Verify Contact is linked to User
		self.assertEqual(contact_doc.user, user_doc.name)
		
		# Verify Contact-Customer Link
		links = [l for l in contact_doc.links if l.link_doctype == "Customer" and l.link_name == customer_name]
		self.assertTrue(links)
		
		# Verify Customer Primary Contact is set
		self.assertEqual(customer_doc.customer_primary_contact, contact_name)

		# Verify Address
		# Should be able to find address via customer link
		address_name = frappe.db.get_value("Dynamic Link", {"link_doctype": "Customer", "link_name": customer_name, "parenttype": "Address"}, "parent")
		self.assertTrue(address_name)
		address_doc = frappe.get_doc("Address", address_name)

		# Verify Address Deatils
		self.assertEqual(address_doc.address_line1, address["address_line1"])
		self.assertEqual(address_doc.city, address["city"])
		self.assertEqual(address_doc.country, address["country"])
		self.assertEqual(address_doc.pincode, address["postal_code"])
		
		# Verify Address Types
		self.assertEqual(address_doc.address_type, "Billing")
		self.assertEqual(address_doc.is_shipping_address, 1)
		
		# Verify Customer Primary Address is set
		self.assertEqual(customer_doc.customer_primary_address, address_name)

	def test_register_duplicate_email(self):
		email = "test_duplicate@example.com"
		name = "Test Duplicate"
		phone = "08123456789"
		password = "password123"
		
		address = {
			"address_line1": "Jalan Test",
			"city": "Jakarta",
			"country": "Indonesia"
		}
		
		students = [{"student_name": "S1", "school_unit": "Test School Unit"}]

		# Cleanup first
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True)

		# First registration
		frappe.set_user("Guest")
		register(name, email, phone, password, address, students)
		
		# Second registration should fail
		result = register(name, email, phone, password, address, students)
		self.assertFalse(result["success"])
		# The exact message might be from our custom check OR duplicate entry error
		# "User with email ... already exists"
		self.assertIn("already exists", result["message"])

	def test_register_missing_student(self):
		# Test registration without students
		frappe.set_user("Guest")
		result = register(
			name="No Student",
			email="nostudent@example.com",
			phone_number="123",
			password="pass",
			address={"address_line1": "A", "city": "B", "country": "C"},
			students=[]
		)
		self.assertFalse(result["success"])
		self.assertIn("At least one student is required", result["message"])
