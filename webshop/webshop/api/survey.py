import frappe
from frappe import _
from frappe.utils import getdate, get_time

@frappe.whitelist()
def get_last_survey_status(item_code):
	"""
	Get the status of the last survey request for a specific item and current user
	"""
	try:
		if frappe.session.user == "Guest":
			return {
				"success": False,
				"message": "Not authenticated"
			}

		user = frappe.session.user
		
		# Get customer link
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			return {
				"success": False,
				"message": "Customer not found"
			}

		# Find the latest survey request for this item and customer
		survey = frappe.db.get_value(
			"Survey Request",
			{
				"customer": customer.name,
				"item_code": item_code
			},
			["name", "status", "admin_notes", "creation"],
			order_by="creation desc",
			as_dict=True
		)

		if survey:
			return {
				"success": True,
				"has_survey": True,
				"status": survey.status,
				"admin_notes": survey.admin_notes,
				"request_date": survey.creation
			}
		
		return {
			"success": True,
			"has_survey": False
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Last Survey Status Error")
		return {
			"success": False,
			"message": str(e)
		}

@frappe.whitelist()
def create_survey_request(web_item_code, date, time, address, students):
	"""
	Create a new survey request
	"""
	try:
		if frappe.session.user == "Guest":
			frappe.throw(_("Please login to submit a survey request"))

		# Get customer
		from webshop.webshop.shopping_cart.cart import get_party
		customer = get_party()
		
		if not customer:
			frappe.throw(_("Customer profile not found"))

		# Validate inputs
		if not web_item_code:
			frappe.throw(_("Web Item code is required"))
		if not date:
			frappe.throw(_("Date is required"))
		if not time:
			frappe.throw(_("Time is required"))
		
		# Parse address and students if they come as JSON strings (common in some API calls)
		import json
		if isinstance(address, str):
			address = json.loads(address)
		if isinstance(students, str):
			students = json.loads(students)

		if not address:
			frappe.throw(_("Address details are required"))
			
		# Get Website Item based on Item Code
		# website_item = frappe.db.get_value("Website Item", web_item_code, "name")
		website_item = frappe.get_doc("Website Item", web_item_code)
		if not website_item:
			frappe.throw(_("Website Item not found for this product"))

		# Create Survey Request
		doc = frappe.new_doc("Survey Request")
		doc.customer = customer.name
		doc.website_item = website_item.name
		doc.date = getdate(date)
		doc.time = time
		
		# Set Address Fields
		doc.address = address.get("full_address")
		doc.province = address.get("province")
		doc.city = address.get("city")
		doc.subdistrict = address.get("subdistrict")
		doc.village = address.get("village")
		doc.postal_code = address.get("postal_code")
		
		# Calculate Student (taking the first one if multiple, or specific logic)
		if students and len(students) > 0:
			# Assuming we link to the first selected student or the primary student
			# Logic might need adjustment if multiple students are actually supported by DocType
			# Based on DocType definition, 'student' is a Link field, so single student.
			# We'll take the first student from the list.
			student_data = students[0]
			# If the frontend sends full student object, we need the name (ID)
			student_id = student_data.get("student_id") or student_data.get("name")
			if student_id:
				doc.student = student_id
			else:
				# If we only have name string but not ID, might need lookup, 
				# but usually frontend should send ID if selecting existing.
				pass
		
		if not doc.student:
			# Fallback: try to find a active student for this customer
			student = frappe.db.get_value("Student", {"customer": customer.name, "is_active": 1}, "name")
			if student:
				doc.student = student
			else:
				frappe.throw(_("Please select a student or ensure you have an active student profile"))

		doc.insert(ignore_permissions=True)
		
		return {
			"success": True,
			"message": _("Survey Request submitted successfully"),
			"name": doc.name,
			"web_item_route": website_item.route
		}

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Create Survey Request Error")
		return {
			"success": False,
			"message": str(e)
		}
