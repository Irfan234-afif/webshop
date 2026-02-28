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

	except Exception as e:
		raise e


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

		# Validate phone number format - must start with international code
		if not phone_number.startswith('+'):
			frappe.throw(_("Phone number must start with international country code (e.g., +62 for Indonesia)"))
		
		# Validate phone number format using Frappe's utility
		try:
			from frappe.utils import validate_phone_number
			if not validate_phone_number(phone_number):
				frappe.throw(_("Invalid phone number format"))
		except Exception:
			frappe.throw(_("Invalid phone number format. Please use international format (e.g., +628123456789)"))

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
		# Switch to Administrator to bypass permission checks for creating Contacts/Addresses via ERPNext hooks
		current_user = frappe.session.user
		frappe.set_user("Administrator")
		
		try:
			phone_number = phone_number.replace(" ", "")
			# Create User first
			user = frappe.get_doc({
				"doctype": "User",
				"email": email,
				"first_name": name.split()[0] if name else email.split("@")[0],
				"last_name": " ".join(name.split()[1:]) if len(name.split()) > 1 else "",
				"full_name": name,
				"user_type": "Website User",
				"language": "id",
				"send_welcome_email": 0,
				"enabled": 1,
			})
			user.insert(ignore_permissions=True)

			# Set password
			update_password(user.name, password)

			# Create Customer using standard ERPNext method (auto create contact and address)
			customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": name,
				"customer_type": "Individual",
				"customer_group": frappe.db.get_single_value("Webshop Settings", "default_customer_group") or "Individual",
				"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
				
				# Fields for auto-creation of Contact
				"email_id": email,
				"mobile_no": phone_number,
				
				# Fields for auto-creation of Address
				"address_line1": address.get("address_line1"),
				"address_line2": address.get("address_line2", ""),
				"city": address.get("city"),
				"state": address.get("state", ""),
				"country": address.get("country"),
				"pincode": address.get("postal_code", ""),
				
				# Directly add portal user
				"portal_users": [{
					"user": user.name
				}]
			})

			customer.insert(ignore_permissions=True)

			# Post-creation steps: Link User to Contact and Setup Address details
			
			# 1. Update the automatically created Contact to link to User
			if customer.customer_primary_contact:
				contact = frappe.get_doc("Contact", customer.customer_primary_contact)
				contact.user = user.name
				contact.save(ignore_permissions=True)
			else:
				# Fallback if no contact created (should not happen if fields are provided)
				contact = None

			# 2. Update the automatically created Address
			address_doc = None
			if customer.customer_primary_address:
				address_doc = frappe.get_doc("Address", customer.customer_primary_address)
				address_doc.address_type = "Billing"
				address_doc.is_shipping_address = 1
				# Address title is set to customer name by default in make_address
				address_doc.save(ignore_permissions=True)

			# frappe.db.commit()

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
					"name": address_doc.name if address_doc else None,
					"address_title": address_doc.address_title if address_doc else None,
					"city": address_doc.city if address_doc else None,
					"country": address_doc.country if address_doc else None,
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
		
		except Exception:
			raise
		finally:
			# Revert to original user
			frappe.set_user(current_user)


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
		# Perform standard Frappe logout
		frappe.local.login_manager.logout()
		
		# Clear all custom webshop cookies
		if hasattr(frappe.local, "cookie_manager"):
			# Clear active student cookie
			frappe.local.cookie_manager.delete_cookie("active_student")
			
			# Clear wishlist count cookie
			frappe.local.cookie_manager.delete_cookie("wish_count")
			
			# Clear cart count cookie
			frappe.local.cookie_manager.delete_cookie("cart_count")
		
		# Clear active student from session
		frappe.session.active_student = None
		
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

		# Get phone from Contact
		phone = frappe.db.get_value("Contact", customer.customer_primary_contact, "mobile_no")

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

		# Get cooperative member status
		is_member = False
		member_name = None
		member_status = None
		member_full_name = None
		member_category = None
		member_join_date = None
		member_docs = frappe.get_all(
			"Cooperative Member",
			filters={"email": frappe.session.user},
			fields=["name", "status", "full_name", "relationship_with_cooperative", "creation"]
		)
		if member_docs:
			is_member = True
			member_name = member_docs[0].name
			member_status = member_docs[0].status
			member_full_name = member_docs[0].full_name
			member_category = member_docs[0].relationship_with_cooperative
			member_join_date = member_docs[0].creation

		return {
			"success": True,
			"user": {
				"email": user.email,
				"full_name": user.full_name,
				"user_type": user.user_type,
				"phone": phone
			},
			"customer": {
				"name": customer.name if customer else None,
				"customer_name": customer.customer_name if customer else None,
			},
			"students": students,
			"is_member": is_member,
			"member_name": member_name,
			"member_status": member_status,
			"member_full_name": member_full_name,
			"member_category": member_category,
			"member_join_date": member_join_date,
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Current User Error")
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def update_profile(full_name, phone):
	"""
	Update user profile (full name, phone)
	"""
	try:
		if not full_name:
			frappe.throw(_("Full Name is required"))
		if not phone:
			frappe.throw(_("Phone number is required"))

		user = frappe.get_doc("User", frappe.session.user)
		phone = phone.replace(" ", "")
		
		# Update User
		name_parts = full_name.split()
		user.first_name = name_parts[0]
		user.last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
		user.full_name = full_name
		user.save(ignore_permissions=True)

		# Update Customer if exists
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		customer.customer_name = full_name
		customer.mobile_no = phone
		customer.save(ignore_permissions=True)

		# Update Contact
		contact = frappe.get_doc("Contact", customer.customer_primary_contact)
		contact.first_name = user.first_name
		contact.last_name = user.last_name
		contact.phone_nos[0].phone = phone
		contact.save(ignore_permissions=True)


		return {
			"success": True,
			"message": _("Profile updated successfully")
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Profile Error")
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


@frappe.whitelist()
def get_address():
	"""
	Get customer's primary address information
	
	Returns:
		dict: Address information with province, city, district, village, postal code, and full address
	"""
	try:
		if frappe.session.user == "Guest":
			frappe.throw("Not authenticated")

		# Get customer from the current user
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			return {
				"success": False,
				"message": _("Customer not found")
			}

		# Get primary address for the customer
		address_name = frappe.db.get_value(
			"Address",
			{
				"link_doctype": "Customer",
				"link_name": customer.name,
				"is_primary_address": 1
			},
			"name"
		)

		if not address_name:
			# Try to get any address if primary not found
			address_name = frappe.db.get_value(
				"Dynamic Link",
				{
					"link_doctype": "Customer",
					"link_name": customer.name,
					"parenttype": "Address"
				},
				"parent"
			)

		if not address_name:
			return {
				"success": True,
				"address": None,
				"message": _("No address found")
			}

		# Get the address document
		address = frappe.get_doc("Address", address_name)

		return {
			"success": True,
			"address": {
				"name": address.name,
				"province": address.state or "",
				"city": address.city or "",
				"district": address.get("county") or "",  # Using county field for district
				"village": address.get("address_line2") or "",  # Using address_line2 for village
				"postal_code": address.pincode or "",
				"full_address": address.address_line1 or ""
			}
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Address Error")
		frappe.throw("Error, please try again later")


@frappe.whitelist()
def update_address(province, city, district, village, postal_code, full_address):
	"""
	Update customer's address information
	
	Args:
		province (str): Province/State
		city (str): City
		district (str): District/County
		village (str): Village/Kelurahan
		postal_code (str): Postal code
		full_address (str): Full address line
		
	Returns:
		dict: Update status
	"""
	try:
		if frappe.session.user == "Guest":
			return {
				"success": False,
				"message": "Not authenticated"
			}

		# Validate required fields
		if not province or not city or not district or not village or not postal_code or not full_address:
			frappe.throw(_("All address fields are required"))

		# Get customer from the current user
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			frappe.throw(_("Customer not found"))

		# Get or create primary address
		address_name = frappe.db.get_value(
			"Address",
			{
				"link_doctype": "Customer",
				"link_name": customer.name,
				"is_primary_address": 1
			},
			"name"
		)

		if not address_name:
			# Try to get any address if primary not found
			address_name = frappe.db.get_value(
				"Dynamic Link",
				{
					"link_doctype": "Customer",
					"link_name": customer.name,
					"parenttype": "Address"
				},
				"parent"
			)

		if address_name:
			# Update existing address
			address = frappe.get_doc("Address", address_name)
			address.state = province
			address.city = city
			address.county = district
			address.address_line2 = village
			address.pincode = postal_code
			address.address_line1 = full_address
			address.is_primary_address = 1
			address.is_shipping_address = 1
			address.save(ignore_permissions=True)
		else:
			# Create new address
			user = frappe.get_doc("User", frappe.session.user)
			contact_name = frappe.db.get_value("Contact", {"email_id": user.email}, "name")
			contact = frappe.get_doc("Contact", contact_name) if contact_name else None
			phone = contact.phone_nos[0].phone if contact and contact.phone_nos else ""

			address = frappe.get_doc({
				"doctype": "Address",
				"address_title": customer.customer_name,
				"address_type": "Billing",
				"address_line1": full_address,
				"address_line2": village,
				"city": city,
				"state": province,
				"county": district,
				"country": "Indonesia",
				"pincode": postal_code,
				"email_id": user.email,
				"phone": phone,
				"is_primary_address": 1,
				"is_shipping_address": 1,
				"links": [{
					"link_doctype": "Customer",
					"link_name": customer.name
				}]
			})
			address.insert(ignore_permissions=True)

		frappe.db.commit()

		return {
			"success": True,
			"message": _("Address updated successfully")
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Address Error")
		frappe.db.rollback()
		return {
			"success": False,
			"message": str(e)
		}


@frappe.whitelist()
def get_students():
	"""
	Get all students associated with the current user's customer account
	
	Returns:
		dict: List of students with their details
	"""
	try:
		if frappe.session.user == "Guest":
			frappe.throw("Not authenticated")

		# Get customer from the current user
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			frappe.throw(_("Customer not found"))

		# Get students for the customer
		student_docs = frappe.get_all(
			"Student",
			filters={"customer": customer.name, "is_active": 1},
			fields=["name", "student_name", "isn", "school_unit", "grade_level", "is_active", "is_primary"],
			order_by="is_primary desc, creation asc"
		)

		students = []
		for s in student_docs:
			students.append({
				"student_id": s.name,
				"student_name": s.student_name,
				"nisn": s.isn or "",
				"school_unit": s.school_unit,
				"grade_level": s.grade_level or "",
				"is_active": s.is_active,
				"is_primary": s.is_primary
			})

		return {
			"success": True,
			"students": students
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Students Error")
		frappe.throw("Error, please try again later")


@frappe.whitelist()
def create_student(student_name, nisn, school_unit, grade_level, date_of_birth=None):
	"""
	Create a new student for the current user's customer account
	
	Args:
		student_name (str): Student name
		nisn (str): NIS/NISN
		school_unit (str): School unit
		grade_level (str): Grade level
		date_of_birth (str): Date of birth (optional)
		
	Returns:
		dict: Created student data
	"""
	try:
		if frappe.session.user == "Guest":
			frappe.throw("Not authenticated")

		# Validate required fields
		if not student_name or not school_unit:
			frappe.throw(_("Student name and school unit are required"))

		# Get customer from the current user
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			frappe.throw(_("Customer not found"))

		# Check if this is the first student (will be primary)
		existing_students = frappe.get_all(
			"Student",
			filters={"customer": customer.name, "is_active": 1},
			fields=["name"]
		)
		is_primary = 1 if len(existing_students) == 0 else 0

		# Create student
		student = frappe.get_doc({
			"doctype": "Student",
			"student_name": student_name,
			"isn": nisn or "",
			"customer": customer.name,
			"school_unit": school_unit,
			"grade_level": grade_level or "",
			"date_of_birth": date_of_birth,
			"is_active": 1,
			"is_primary": is_primary
		})
		student.insert(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Student created successfully"),
			"student": {
				"student_id": student.name,
				"student_name": student.student_name,
				"nisn": student.isn or "",
				"school_unit": student.school_unit,
				"grade_level": student.grade_level or "",
				"is_active": student.is_active,
				"is_primary": student.is_primary
			}
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Student Error")
		frappe.db.rollback()
		frappe.throw(str(e))


@frappe.whitelist()
def update_student(student_id, student_name, nisn, school_unit, grade_level, date_of_birth=None):
	"""
	Update an existing student
	
	Args:
		student_id (str): Student ID
		student_name (str): Student name
		nisn (str): NIS/NISN
		school_unit (str): School unit
		grade_level (str): Grade level
		date_of_birth (str): Date of birth (optional)
		
	Returns:
		dict: Updated student data
	"""
	try:
		if frappe.session.user == "Guest":
			frappe.throw("Not authenticated")

		# Validate required fields
		if not student_id or not student_name or not school_unit:
			frappe.throw(_("Student ID, student name and school unit are required"))

		# Get customer from the current user
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			frappe.throw(_("Customer not found"))

		# Check if student exists and belongs to customer
		student = frappe.get_doc("Student", student_id)
		if student.customer != customer.name:
			frappe.throw(_("Student not found"))

		# Update student
		if student.student_name != student_name:
			# If student_name changes, we must use rename_doc because it's the naming field
			new_name = frappe.rename_doc("Student", student_id, student_name, force=True)
			# Re-get the document with the new name to update other fields
			student = frappe.get_doc("Student", new_name)

		student.isn = nisn or ""
		student.school_unit = school_unit
		student.grade_level = grade_level or ""
		if date_of_birth:
			student.date_of_birth = date_of_birth
		student.save(ignore_permissions=True)
		frappe.db.commit()

		return {
			"success": True,
			"message": _("Student updated successfully"),
			"student": {
				"student_id": student.name,
				"student_name": student.student_name,
				"nisn": student.isn or "",
				"school_unit": student.school_unit,
				"grade_level": student.grade_level or "",
				"is_active": student.is_active,
				"is_primary": student.is_primary
			}
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Update Student Error")
		frappe.db.rollback()
		frappe.throw(str(e))


@frappe.whitelist()
def get_school_units():
	"""
	Get all school units
	
	Returns:
		dict: List of school units
	"""
	try:
		school_units = frappe.get_all(
			"School Unit",
			fields=["name", "unit_name"],
			order_by="name asc"
		)

		return {
			"success": True,
			"school_units": [{"value": s.name, "label": s.unit_name or s.name} for s in school_units]
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get School Units Error")
		frappe.throw("Error, please try again later")


@frappe.whitelist()
def get_grades(school_unit=None):
	"""
	Get all grade levels, optionally filtered by school unit
	
	Args:
		school_unit (str, optional): Filter grades by school unit
	
	Returns:
		dict: List of grades
	"""
	try:
		filters = {"enabled": 1}
		if school_unit:
			filters["school_unit"] = school_unit

		grades = frappe.get_all(
			"Grade",
			filters=filters,
			fields=["name", "grade_name"],
			order_by="sort_order asc, name asc"
		)

		return {
			"success": True,
			"grades": [{"value": g.name, "label": g.grade_name or g.name} for g in grades]
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Grades Error")
		frappe.throw("Error, please try again later")

@frappe.whitelist(allow_guest=True)
def reset_password(email):
	"""
	Send password reset email to user
	
	Args:
		email (str): User email
		
	Returns:
		dict: Success status
	"""
	try:
		if not email:
			frappe.throw(_("Email is required"))
			
		# Check if user exists
		if not frappe.db.exists("User", email):
			frappe.throw(_("User with email {0} does not exist").format(email))
			
		user = frappe.get_doc("User", email)
		user.reset_password(send_email=True)
		
		return {
			"success": True,
			"message": _("Password reset instructions have been sent to your email")
		}
		
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Reset Password Error")
		return {
			"success": False,
			"message": str(e)
		}
