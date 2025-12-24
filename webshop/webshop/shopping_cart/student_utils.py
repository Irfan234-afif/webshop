# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Student session management utilities for per-student shopping carts
"""

import frappe
from frappe import _

from webshop.webshop.shopping_cart.cart import get_party
from webshop.webshop.doctype.student.student import get_students_for_customer


def get_active_student():
	"""
	Get the currently active student from session

	Returns:
		Student object if active student exists and is valid, None otherwise
	"""
	student_name = frappe.session.get("active_student")

	if not student_name:
		return None

	# Validate student belongs to current user's customer
	party = get_party()
	if not party:
		return None

	try:
		students = get_students_for_customer(party.name)

		# Find student in customer's students list
		for student in students:
			if student.get("name") == student_name and student.get("is_active"):
				return frappe.get_doc("Student", student_name)

		# Student not found or not active - clear from session
		frappe.session.active_student = None
		return None

	except Exception as e:
		frappe.log_error(f"Error getting active student: {str(e)}")
		return None


@frappe.whitelist()
def set_active_student(student_name):
	"""
	Set the active student for the shopping session

	Args:
		student_name (str): Student name to set as active

	Returns:
		dict: Success status and student info
	"""
	# Validate student belongs to current user
	party = get_party()
	if not party:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		students = get_students_for_customer(party.name)

		student_found = False
		student_obj = None

		# Check if student exists and is active
		for student in students:
			if student.get("name") == student_name:
				if not student.get("is_active"):
					frappe.throw(
						_("Student '{0}' is not active").format(student.get("student_name")),
						title=_("Inactive Student")
					)
				student_found = True
				student_obj = student
				break

		if not student_found:
			frappe.throw(
				_("Student not found or does not belong to your account"),
				title=_("Invalid Student")
			)

		# Set in session
		frappe.session.active_student = student_name

		# Set in cookie for persistence
		if hasattr(frappe.local, "cookie_manager"):
			from datetime import datetime, timedelta
			expiry_time = datetime.now() + timedelta(days=30)
			frappe.local.cookie_manager.set_cookie(
				"active_student",
				student_name,
				expires=expiry_time,
				httponly=False,  # Allow access from JavaScript if needed
				secure=frappe.local.request and frappe.local.request.scheme == "https"  # Secure only on HTTPS
			)

		return {
			"success": True,
			"student_name": student_name,
			"student_display_name": student_obj.get("student_name"),
			"school_unit": student_obj.get("school_unit")
		}

	except Exception as e:
		frappe.log_error(f"Error setting active student: {str(e)}")
		raise


@frappe.whitelist()
def get_customer_students():
	"""
	Get all students for the current customer

	Returns:
		list: Array of student objects
	"""
	party = get_party()
	if not party:
		return []

	try:
		customer_doc = frappe.get_doc("Customer", party.name)
		students = []

		for student in customer_doc.students:
			students.append({
				"student_id": student.student_id,
				"student_name": student.student_name,
				"school_unit": student.school_unit,
				"grade_level": student.grade_level,
				"is_active": student.is_active,
				"date_of_birth": student.date_of_birth
			})

		return students

	except Exception as e:
		frappe.log_error(f"Error getting customer students: {str(e)}")
		return []


@frappe.whitelist()
def clear_active_student():
	"""
	Clear the active student from session

	Returns:
		dict: Success status
	"""
	# Clear from session
	frappe.session.active_student = None

	# Delete cookie
	if hasattr(frappe.local, "cookie_manager"):
		frappe.local.cookie_manager.delete_cookie("active_student")

	return {"success": True}


@frappe.whitelist()
def get_active_student_name():
	"""
	Get just the active student name from session

	Returns:
		dict: Contains success status and student name
	"""
	student_name = frappe.session.get("active_student")
	return {
		"success": True,
		"student_name": student_name
	}


def restore_active_student_from_cookie():
	"""
	Restore active student from cookie if exists (called on session creation)

	This function should be called in session hooks to restore student selection
	"""
	if hasattr(frappe.local, "cookie_manager"):
		student_name = frappe.request.cookies.get("active_student")

		if student_name and not frappe.session.get("active_student"):
			# Validate student still exists and is valid
			party = get_party()
			if party:
				try:
					students = get_students_for_customer(party.name)
					for student in students:
						if student.get("name") == student_name and student.get("is_active"):
							frappe.session.active_student = student_name
							break
				except Exception:
					# Silently fail - cookie might be stale
					pass
