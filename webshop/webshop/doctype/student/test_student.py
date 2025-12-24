# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestStudent(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Create a test school unit if it doesn't exist
		if not frappe.db.exists("School Unit", "Test School"):
			frappe.get_doc({
				"doctype": "School Unit",
				"unit_name": "Test School",
				"unit_code": "TEST",
				"is_active": 1
			}).insert(ignore_permissions=True)

	def test_create_student(self):
		"""Test creating a student"""
		student = frappe.get_doc({
			"doctype": "Student",
			"student_name": "Test Student",
			"school_unit": "Test School",
			"grade_level": "5",
			"is_active": 1
		})
		student.insert()

		# Verify student was created
		self.assertTrue(frappe.db.exists("Student", student.name))

		# Clean up
		student.delete()

	def test_duplicate_student_name(self):
		"""Test that duplicate student names are not allowed"""
		# Create first student
		student1 = frappe.get_doc({
			"doctype": "Student",
			"student_name": "Duplicate Test",
			"school_unit": "Test School",
			"is_active": 1
		})
		student1.insert()

		# Try to create duplicate
		student2 = frappe.get_doc({
			"doctype": "Student",
			"student_name": "Duplicate Test",
			"school_unit": "Test School",
			"is_active": 1
		})

		# Should raise an error
		with self.assertRaises(frappe.exceptions.UniqueValidationError):
			student2.insert()

		# Clean up
		student1.delete()

	def test_inactive_school_unit(self):
		"""Test that inactive school unit cannot be used"""
		# Create inactive school unit
		if not frappe.db.exists("School Unit", "Inactive School"):
			inactive_unit = frappe.get_doc({
				"doctype": "School Unit",
				"unit_name": "Inactive School",
				"unit_code": "INACTIVE",
				"is_active": 0
			})
			inactive_unit.insert(ignore_permissions=True)

		# Try to create student with inactive school unit
		student = frappe.get_doc({
			"doctype": "Student",
			"student_name": "Test Inactive",
			"school_unit": "Inactive School",
			"is_active": 1
		})

		# Should raise an error
		with self.assertRaises(frappe.exceptions.ValidationError):
			student.insert()

	def test_future_date_of_birth(self):
		"""Test that future date of birth is not allowed"""
		from frappe.utils import add_days, today

		student = frappe.get_doc({
			"doctype": "Student",
			"student_name": "Future Birth Test",
			"school_unit": "Test School",
			"date_of_birth": add_days(today(), 1),  # Tomorrow
			"is_active": 1
		})

		# Should raise an error
		with self.assertRaises(frappe.exceptions.ValidationError):
			student.insert()

	def tearDown(self):
		"""Clean up test data"""
		frappe.db.rollback()
