# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Student session management utilities for per-student shopping carts
"""

import frappe
from frappe import _

from webshop.webshop.doctype.student.student import get_students_for_customer


def get_all_customers_for_user(user=None):
	"""
	Get all customers linked to the user via Contact or Portal User.
	Handles cases where user has multiple contacts or multiple customer links.
	"""
	if not user:
		user = frappe.session.user

	customers = set()

	# 1. Get all Contacts with this email
	contacts = frappe.get_all("Contact Email", filters={"email_id": user}, fields=["parent"])
	contact_names = [c.parent for c in contacts]

	if contact_names:
		# 2. Get linked customers from these contacts
		links = frappe.get_all(
			"Dynamic Link", 
			filters={
				"parent": ["in", contact_names], 
				"parenttype": "Contact", 
				"link_doctype": "Customer"
			}, 
			fields=["link_name"]
		)
		for l in links:
			customers.add(l.link_name)

	# 3. Check Portal User links
	portal_links = frappe.get_all(
		"Portal User", 
		filters={"user": user, "parenttype": "Customer"}, 
		fields=["parent"]
	)
	for p in portal_links:
		customers.add(p.parent)

	return list(customers)



def get_active_student():
	"""
	Get the currently active student from session

	Returns:
		Student object if active student exists and is valid, None otherwise
	"""
	# Try to get from session first, then fallback to cookie
	student_name = frappe.session.get("active_student")
	if not student_name:
		try:
			# Try to get from cookie (may fail in test context)
			student_name = frappe.request.cookies.get("active_student")
		except (RuntimeError, AttributeError):
			# frappe.request is not bound (test context) or cookies not available
			student_name = None

	if not student_name:
		return None

	# Validate student belongs to current user's customer(s)
	customers = get_all_customers_for_user()
	if not customers:
		return None

	try:
		# Check all linked customers
		for customer in customers:
			students = get_students_for_customer(customer)
			for student in students:
				if student.get("name") == student_name and student.get("is_active"):
					return frappe.get_doc("Student", student_name)


		# Student not found or not active - clear from session and cookie
		frappe.session.active_student = None
		if hasattr(frappe.local, "cookie_manager"):
			frappe.local.cookie_manager.delete_cookie("active_student")
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
	customers = get_all_customers_for_user()
	if not customers:
		frappe.throw(_("No customer account found"), title=_("Authentication Required"))

	try:
		student_found = False
		student_obj = None

		# Check all linked customers
		for customer in customers:
			students = get_students_for_customer(customer)
			
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
			
			if student_found:
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
	customers = get_all_customers_for_user()
	if not customers:
		return []

	try:
		all_students = []
		
		# Aggregate students from all customers
		for customer in customers:
			customer_doc = frappe.get_doc("Customer", customer)
			
			# Check child table students
			if hasattr(customer_doc, 'students'):
				for student in customer_doc.students:
					all_students.append({
						"student_id": student.student_id,
						"student_name": student.student_name,
						"school_unit": student.school_unit,
						"grade_level": student.grade_level,
						"is_active": student.is_active,
						"date_of_birth": student.date_of_birth
					})
			
			# Also get students linked via 'customer' field (backwards compatibility/completeness)
			linked_students = get_students_for_customer(customer)
			for s in linked_students:
				# Avoid duplicates if they appear in both places
				if not any(exist['student_id'] == s.name for exist in all_students):
					all_students.append({
						"student_id": s.name,
						"student_name": s.student_name,
						"school_unit": s.school_unit,
						"grade_level": s.grade_level,
						"is_active": s.is_active,
						"date_of_birth": s.date_of_birth
					})

		return all_students

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
			try:
				party = get_party()
				if party:
					students = get_students_for_customer(party.name)
					for student in students:
						if student.get("name") == student_name and student.get("is_active"):
							frappe.session.active_student = student_name
							break
			except Exception:
				# Silently fail - cookie might be stale
				pass