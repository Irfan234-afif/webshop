# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Student Management API Endpoints

Provides API endpoints for managing students and their shopping carts
"""

import frappe
from frappe import _

from webshop.webshop.shopping_cart.cart import get_party
from webshop.webshop.doctype.student.student import get_students_for_customer


@frappe.whitelist()
def get_students():
	"""
	Get all students for the currently logged-in customer

	Returns:
		list: Array of student objects
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		students = get_students_for_customer(party.name)
		return students

	except Exception as e:
		frappe.log_error(f"Error fetching students: {str(e)}")
		frappe.throw(_("Error fetching students"), title=_("Error"))


@frappe.whitelist()
def add_student(student_name, school_unit, grade_level=None, date_of_birth=None, is_primary=0):
	"""
	Add a new student to the current customer account

	Args:
		student_name (str): Student's full name
		school_unit (str): Link to School Unit (e.g., "High School")
		grade_level (str, optional): Student's grade level
		date_of_birth (str, optional): Student's date of birth
		is_primary (int, optional): Mark as primary student (0 or 1)

	Returns:
		dict: Success status and student name
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	# Validate required fields
	if not student_name or not school_unit:
		frappe.throw(_("Student name and school unit are required"), title=_("Missing Required Fields"))

	# Verify school unit exists
	if not frappe.db.exists("School Unit", school_unit):
		frappe.throw(_("School Unit '{0}' does not exist").format(school_unit), title=_("Invalid School Unit"))

	try:
		# Create Student document with customer link
		student = frappe.get_doc({
			"doctype": "Student",
			"student_name": student_name,
			"customer": party.name,
			"school_unit": school_unit,
			"grade_level": grade_level,
			"date_of_birth": date_of_birth,
			"is_active": 1,
			"is_primary": int(is_primary)
		})
		student.insert(ignore_permissions=True)

		return {
			"success": True,
			"student_name": student.name,
			"message": _("Student added successfully")
		}

	except Exception as e:
		frappe.log_error(f"Error adding student: {str(e)}")
		frappe.throw(_("Error adding student: {0}").format(str(e)), title=_("Error"))


@frappe.whitelist()
def get_cart_by_student(student_name):
	"""
	Get cart (quotation) for a specific student

	Args:
		student_name (str): Student name to get cart for

	Returns:
		dict: Cart quotation summary or None
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	# Validate student belongs to current customer
	try:
		students = get_students_for_customer(party.name)
		student_found = False

		for student in students:
			if student.get("name") == student_name:
				student_found = True
				break

		if not student_found:
			frappe.throw(_("Student not found or does not belong to your account"), title=_("Invalid Student"))

	except Exception as e:
		frappe.log_error(f"Error validating student: {str(e)}")
		frappe.throw(_("Error validating student"), title=_("Error"))

	# Get cart for student
	quotation = frappe.get_all(
		"Quotation",
		fields=["name", "grand_total", "total_qty", "currency"],
		filters={
			"party_name": party.name,
			"student": student_name,
			"order_type": "Shopping Cart",
			"docstatus": 0
		},
		order_by="modified desc",
		limit_page_length=1
	)

	if quotation:
		return quotation[0]
	else:
		return None


@frappe.whitelist()
def get_all_student_carts():
	"""
	Get cart summaries for all students of the current customer

	Returns:
		list: Array of student cart summaries
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		students = get_students_for_customer(party.name)
		carts = []

		for student in students:
			# Get cart for this student
			cart = None
			quotation = frappe.get_all(
				"Quotation",
				fields=["name", "grand_total", "total_qty", "currency", "rounded_total"],
				filters={
					"party_name": party.name,
					"student": student.get("name"),
					"order_type": "Shopping Cart",
					"docstatus": 0
				},
				order_by="modified desc",
				limit_page_length=1
			)

			if quotation:
				cart = quotation[0]

			carts.append({
				"student_name": student.get("name"),
				"student_display_name": student.get("student_name"),
				"school_unit": student.get("school_unit"),
				"is_active": student.get("is_active"),
				"is_primary": student.get("is_primary"),
				"cart": cart
			})

		return carts

	except Exception as e:
		frappe.log_error(f"Error fetching student carts: {str(e)}")
		frappe.throw(_("Error fetching student carts"), title=_("Error"))


@frappe.whitelist()
def update_student(student_name, new_student_name=None, school_unit=None, grade_level=None, date_of_birth=None, is_active=None):
	"""
	Update an existing student

	Args:
		student_name (str): Student name to update
		new_student_name (str, optional): New student name
		school_unit (str, optional): New school unit
		grade_level (str, optional): New grade level
		date_of_birth (str, optional): New date of birth
		is_active (int, optional): Active status (0 or 1)

	Returns:
		dict: Success status
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		# Validate student belongs to current customer
		students = get_students_for_customer(party.name)
		student_found = False

		for student in students:
			if student.get("name") == student_name:
				student_found = True
				break

		if not student_found:
			frappe.throw(_("Student not found or does not belong to your account"), title=_("Invalid Student"))

		# Update the Student document
		student_doc = frappe.get_doc("Student", student_name)

		# Update fields if provided
		if new_student_name is not None:
			student_doc.student_name = new_student_name
		if school_unit is not None:
			# Verify school unit exists
			if not frappe.db.exists("School Unit", school_unit):
				frappe.throw(_("School Unit '{0}' does not exist").format(school_unit))
			student_doc.school_unit = school_unit
		if grade_level is not None:
			student_doc.grade_level = grade_level
		if date_of_birth is not None:
			student_doc.date_of_birth = date_of_birth
		if is_active is not None:
			student_doc.is_active = int(is_active)

		student_doc.save(ignore_permissions=True)

		return {
			"success": True,
			"message": _("Student updated successfully")
		}

	except Exception as e:
		frappe.log_error(f"Error updating student: {str(e)}")
		frappe.throw(_("Error updating student: {0}").format(str(e)), title=_("Error"))


@frappe.whitelist()
def delete_student(student_name):
	"""
	Delete a student from the customer account

	Args:
		student_name (str): Student name to delete

	Returns:
		dict: Success status
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		# Validate student belongs to current customer
		students = get_students_for_customer(party.name)
		student_found = False

		for student in students:
			if student.get("name") == student_name:
				student_found = True
				break

		if not student_found:
			frappe.throw(_("Student not found or does not belong to your account"), title=_("Invalid Student"))

		# Delete the Student document
		frappe.delete_doc("Student", student_name, ignore_permissions=True)

		return {
			"success": True,
			"message": _("Student deleted successfully")
		}

	except Exception as e:
		frappe.log_error(f"Error deleting student: {str(e)}")
		frappe.throw(_("Error deleting student: {0}").format(str(e)), title=_("Error"))
