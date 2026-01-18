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
			"country": "Indonesia"
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
		frappe.db.delete("Contact", {"email_id": email}) # This might need a join properly but simple delete often works if not normalized
		# Actually Contact uses child table for emails, so better find it
		contact_names = frappe.db.sql("select parent from `tabContact Email` where email_id=%s", email, pluck=True)
		for c in contact_names:
			frappe.delete_doc("Contact", c, force=True)
			
		# Clean up any students with this name
		frappe.db.delete("Student", {"student_name": "Test Student 1"})

		# Clean up User if it still exists (delete_doc vs db.delete)
		if frappe.db.exists("User", email):
			frappe.delete_doc("User", email, force=True)
		
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
		
		# Verify Contact
		contact_name = frappe.db.get_value("Contact", {"email_id": email}, "name")
		self.assertTrue(contact_name)
		
		# Verify Customer linkage
		customer_name = result["customer"]["name"]
		self.assertTrue(frappe.db.exists("Customer", customer_name))
		
		# Verify Contact-Customer Link
		links = frappe.get_all("Dynamic Link", filters={
			"parent": contact_name,
			"link_doctype": "Customer",
			"link_name": customer_name
		})
		self.assertTrue(links)

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

		# First registration
		register(name, email, phone, password, address, students)
		
		# Second registration should fail
		result = register(name, email, phone, password, address, students)
		self.assertFalse(result["success"])
		self.assertIn(f"User with email {email} already exists", result["message"])

	def test_register_missing_student(self):
		# Test registration without students
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
