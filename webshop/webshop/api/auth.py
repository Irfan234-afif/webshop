# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Authentication API endpoints for Webshop
Provides login and registration functionality
"""

import frappe
from frappe import _
from frappe.utils import validate_email_address, cint
from frappe.utils.password import update_password


@frappe.whitelist(allow_guest=True)
def login(email, password):
	"""
	Login API endpoint

	Args:
		email (str): User email
		password (str): User password

	Returns:
		dict: Login status with user info
	"""
	try:
		# Validate inputs
		if not email or not password:
			frappe.throw(_("Email and password are required"))

		# Validate email format
		# try:
		# 	validate_email_address(email, throw=True)
		# except Exception:
		# 	frappe.throw(_("Invalid email format"))

		# Check if user exists
		if not frappe.db.exists("User", email):
			frappe.throw(_("Invalid email or password"))

		# Attempt login using Frappe's authentication
		try:
			frappe.local.login_manager.authenticate(email, password)
			frappe.local.login_manager.post_login()
		except frappe.exceptions.AuthenticationError:
			frappe.throw(_("Invalid email or password"))

		# Get user info
		user = frappe.get_doc("User", email)

		# Get associated customer
		customer = None
		customer_name = frappe.db.get_value("Contact", {"email_id": email}, "name")
		if customer_name:
			customer_link = frappe.db.get_value(
				"Dynamic Link",
				{"link_doctype": "Customer", "parent": customer_name},
				"link_name"
			)
			if customer_link:
				customer = frappe.get_doc("Customer", customer_link)

		# Get students if customer exists
		students = []
		if customer:
			student_docs = frappe.get_all(
				"Student",
				filters={"customer": customer.name, "is_active": 1},
				fields=["name", "student_name", "school_unit", "grade_level", "is_active"]
			)
			students = [
				{
					"student_id": s.name,
					"student_name": s.student_name,
					"school_unit": s.school_unit,
					"grade_level": s.grade_level,
					"is_active": s.is_active
				}
				for s in student_docs
			]

		return {
			"success": True,
			"message": "Login successful",
			"user": {
				"email": user.email,
				"full_name": user.full_name,
				"user_type": user.user_type,
			},
			"customer": {
				"name": customer.name if customer else None,
				"customer_name": customer.customer_name if customer else None,
			},
			"students": students,
		}

	except frappe.exceptions.AuthenticationError:
		frappe.local.response["http_status_code"] = 401
		return {
			"success": False,
			"message": _("Invalid email or password")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Webshop Login Error")
		frappe.local.response["http_status_code"] = 500
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def register(name, email, phone_number, password, address=None, students=None):
	"""
	Registration API endpoint
	Creates Customer, Contact, User, Address, and Students

	Args:
		name (str): Customer full name
		email (str): Customer email
		phone_number (str): Customer phone number
		password (str): Account password
		address (dict): Customer address with fields:
			- address_line1 (str, required): Primary address line
			- address_line2 (str, optional): Secondary address line
			- city (str, required): City/town
			- state (str, optional): State/province
			- country (str, required): Country
			- postal_code (str, optional): Postal/ZIP code
		students (list): List of student objects to create (at least one required)
			Each student object: {"student_name": str, "school_unit": str, "grade_level": str (optional)}

	Returns:
		dict: Registration status with customer, user, and address info
	"""
	try:
		# Validate inputs
		if not name or not email or not password:
			frappe.throw(_("Name, email, and password are required"))

		if not phone_number:
			frappe.throw(_("Phone number is required"))

		# Parse address if provided as JSON string
		if address and isinstance(address, str):
			import json
			address = json.loads(address)

		# Validate address
		if not address or not isinstance(address, dict):
			frappe.throw(_("Address is required"))

		if not address.get("address_line1") or not address.get("city") or not address.get("country"):
			frappe.throw(_("Address must include address_line1, city, and country"))

		# Validate email format
		try:
			validate_email_address(email, throw=True)
		except Exception:
			frappe.throw(_("Invalid email format"))

		# Check if user already exists
		if frappe.db.exists("User", email):
			frappe.throw(_("User with email {0} already exists").format(email))

		# Parse students if provided as JSON string
		if students and isinstance(students, str):
			import json
			students = json.loads(students)

		# Validate that at least one student is provided
		if not students:
			frappe.throw(_("At least one student is required for registration"))

		if not isinstance(students, list):
			frappe.throw(_("Students must be a list"))

		if len(students) == 0:
			frappe.throw(_("At least one student is required for registration"))

		# Validate students data
		validated_students = []
		if students and isinstance(students, list):
			for student in students:
				if not isinstance(student, dict):
					frappe.throw(_("Each student must be an object with student_name and school_unit"))

				if not student.get("student_name") or not student.get("school_unit"):
					frappe.throw(_("Each student must have student_name and school_unit"))

				# Check if school unit exists
				if not frappe.db.exists("School Unit", student["school_unit"]):
					frappe.throw(_("School Unit {0} does not exist").format(student["school_unit"]))

				validated_students.append({
					"student_name": student["student_name"],
					"school_unit": student["school_unit"],
					"grade_level": student.get("grade_level", ""),
					"date_of_birth": student.get("date_of_birth"),
					"nisn": student.get("nisn", ""),
					"is_active": 1
				})

		# Start transaction
		frappe.flags.ignore_permissions = True

		# Create User first
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": name.split()[0] if name else email.split("@")[0],
			"last_name": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
			"full_name": name,
			"user_type": "Website User",
			"send_welcome_email": 0,
			"enabled": 1,
		})
		user.insert(ignore_permissions=True)

		# Set password
		update_password(user.name, password)

		# Create Contact
		contact = frappe.get_doc({
			"doctype": "Contact",
			"first_name": name.split()[0] if name else email.split("@")[0],
			"last_name": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
			"email_ids": [{"email_id": email, "is_primary": 1}],
			"phone_nos": [{"phone": phone_number, "is_primary_phone": 1}],
			"user": user.name,
		})
		contact.insert(ignore_permissions=True)

		# Create Customer
		customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": name,
			"customer_type": "Individual",
			"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "Individual",
			"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
		})


		customer.insert(ignore_permissions=True)

		# Link Contact to Customer
		contact.append("links", {
			"link_doctype": "Customer",
			"link_name": customer.name
		})
		contact.save(ignore_permissions=True)

		# Add user to Customer's portal users
		if not any(u.user == user.name for u in customer.portal_users if hasattr(customer, 'portal_users')):
			customer.append("portal_users", {
				"user": user.name
			})
			customer.save(ignore_permissions=True)

		frappe.db.commit()

		# Create Address for Customer
		address_doc = frappe.get_doc({
			"doctype": "Address",
			"address_title": name,
			"address_type": "Billing",
			"address_line1": address.get("address_line1"),
			"address_line2": address.get("address_line2", ""),
			"city": address.get("city"),
			"state": address.get("state", ""),
			"country": address.get("country"),
			"pincode": address.get("postal_code", ""),
			"email_id": email,
			"phone": phone_number,
			"is_primary_address": 1,  # Set as default billing address
			"is_shipping_address": 1,  # Set as default shipping address
			"links": [{
				"link_doctype": "Customer",
				"link_name": customer.name
			}]
		})
		address_doc.insert(ignore_permissions=True)

		frappe.db.commit()

		# Create standalone Student documents if provided
		created_students = []
		if validated_students:
			for idx, student_data in enumerate(validated_students):
				student = frappe.get_doc({
					"doctype": "Student",
					"student_name": student_data["student_name"],
					"customer": customer.name,
					"school_unit": student_data["school_unit"],
					"grade_level": student_data.get("grade_level", ""),
					"date_of_birth": student_data.get("date_of_birth"),
					"isn": student_data.get("nisn", ""),
					"is_active": 1,
					"is_primary": 1 if idx == 0 else 0  # First student is primary
				})
				student.insert(ignore_permissions=True)
				created_students.append(student)

			frappe.db.commit()

		# Return success response with created entities
		return {
			"success": True,
			"message": "Registration successful",
			"user": {
				"email": user.email,
				"full_name": user.full_name,
			},
			"customer": {
				"name": customer.name,
				"customer_name": customer.customer_name,
			},
			"address": {
				"name": address_doc.name,
				"address_title": address_doc.address_title,
				"city": address_doc.city,
				"country": address_doc.country,
			},
			"students": [
				{
					"student_id": s.name,
					"student_name": s.student_name,
					"school_unit": s.school_unit,
					"grade_level": s.grade_level,
					"is_active": s.is_active
				}
				for s in created_students
			] if created_students else []
		}

	except frappe.exceptions.DuplicateEntryError:
		frappe.local.response["http_status_code"] = 409
		frappe.db.rollback()
		return {
			"success": False,
			"message": _("User with this email already exists")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Webshop Registration Error")
		frappe.db.rollback()
		frappe.local.response["http_status_code"] = 500
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def logout():
	"""
	Logout API endpoint

	Returns:
		dict: Logout status
	"""
	try:
		frappe.local.login_manager.logout()
		frappe.db.commit()

		return {
			"success": True,
			"message": "Logout successful"
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Webshop Logout Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def get_current_user():
	"""
	Get current logged-in user info

	Returns:
		dict: User information with associated customer and students
	"""
	from webshop.webshop.shopping_cart.cart import get_party
	try:
		if frappe.session.user == "Guest":
			return {
				"success": False,
				"message": "Not authenticated",
				"user": None
			}

		user = frappe.get_doc("User", frappe.session.user)

		# Get associated customer
		customer = get_party()

		# Get students if customer exists
		students = []
		if customer:
			student_docs = frappe.get_all(
				"Student",
				filters={"customer": customer.name, "is_active": 1},
				fields=["name", "student_name", "school_unit", "grade_level", "is_active"]
			)
			students = [
				{
					"student_id": s.name,
					"student_name": s.student_name,
					"school_unit": s.school_unit,
					"grade_level": s.grade_level,
					"is_active": s.is_active
				}
				for s in student_docs
			]

		return {
			"success": True,
			"user": {
				"email": user.email,
				"full_name": user.full_name,
				"user_type": user.user_type,
			},
			"customer": {
				"name": customer.name if customer else None,
				"customer_name": customer.customer_name if customer else None,
			},
			"students": students,
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Current User Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist(allow_guest=True)
def check_email_availability(email):
	"""
	Check if email is available for registration

	Args:
		email (str): Email to check

	Returns:
		dict: Availability status
	"""
	try:
		# Validate email format
		try:
			validate_email_address(email, throw=True)
		except Exception:
			return {
				"success": False,
				"available": False,
				"message": _("Invalid email format")
			}

		# Check if user exists
		exists = frappe.db.exists("User", email)

		return {
			"success": True,
			"available": not exists,
			"message": _("Email is available") if not exists else _("Email is already registered")
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Check Email Availability Error")
		return {
			"success": False,
			"message": str(e)
		}
