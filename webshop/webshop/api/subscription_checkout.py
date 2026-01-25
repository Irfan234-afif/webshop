import frappe
from frappe import _
from frappe.utils import getdate
from webshop.webshop.shopping_cart.product_info import get_product_info_for_website
from frappe.utils import flt

@frappe.whitelist()
def create_subscription_request(data):
	"""
	Creates a Subscription Request from the frontend.
	Data Expected:
	{
		"item_code": "SUB-ITEM-001",
		"start_date": "2025-01-01",
		"notes": "Please deliver on Mondays only."
	}
	"""
	if isinstance(data, str):
		import json
		data = json.loads(data)

	if not frappe.session.user or frappe.session.user == "Guest":
		frappe.throw(_("Please login to subscribe"), frappe.PermissionError)
	
	try:
		item_code = data.get("item_code")
		start_date = data.get("start_date")
		notes = data.get("notes")
		student = data.get("student")
		
		if not item_code or not start_date or not student:
			frappe.throw(_("Missing required fields"))

		# Validate student if provided
		if student and not frappe.db.exists("Student", student):
			frappe.throw(_("Invalid student"))

		from webshop.webshop.shopping_cart.cart import get_party
		
		customer = get_party()
		if not customer:
			frappe.throw(_("Customer profile not found for this user."))

		customer_name = customer.name

		# Get Plan
		plan = frappe.db.get_value("Item", item_code, "subscription_plan")
		if not plan:
			plan_name = frappe.db.get_value("Subscription Plan", {"item": item_code})
			if not plan_name:
				frappe.throw(_("This item is not configured as a Subscription Plan."))
		else:
			plan_name = plan

		doc = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": customer_name,
			"item": item_code,
			"subscription_plan": plan_name,
			"start_date": start_date,
			"notes": notes,
		})
		
		# Set student (Mandatory)
		doc.student = student
		
		# Note: end_date will be auto-calculated in the DocType controller
		doc.insert(ignore_permissions=True) # Ignore perms to allow Customer to create if not granted explicit create rights in JSON
		frappe.db.commit()
		return doc.name
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(frappe.get_traceback())
		raise e

@frappe.whitelist(allow_guest=True)
def get_subscription_item_details(item_code):
	"""
	Returns details needed for the Subscription Checkout page.
	"""
	item = frappe.get_doc("Item", item_code)
	
	# Assuming 'subscription_plan' field on Item.
	# If strict architecture, verify field existence.
	# For now, fetching it.
	
	plan = None
	if item.is_subscription_item: # Custom field check
		if not item.subscription_plan:
			plan_name = frappe.db.get_value("Subscription Plan", {"item": item_code})
			plan = frappe.get_doc("Subscription Plan", plan_name)
		else:
			plan = frappe.get_doc("Subscription Plan", item.subscription_plan)
	else:
		frappe.throw(_("This item is not configured as a Subscription Plan."))
		
	image = item.image
	if not image:
		image = frappe.db.get_value("Website Item", {"item_code": item_code}, "website_image")

	product_info = get_product_info_for_website(item_code, skip_quotation_creation=True)
	cost = 0
	if product_info and product_info.product_info:
		price_info = product_info.product_info.get("price")
		if price_info:
			cost = flt(price_info.price_list_rate) if price_info.price_list_rate else 0
	return {
		"item_name": item.item_name,
		"item_code": item.item_code,
		"image": image,
		"description": item.description,
		"plan_name": plan.plan_name if plan else None,
		"cost": cost,
		"billing_interval": plan.billing_interval if plan else "Month",
		"billing_timing": plan.billing_timing if plan else "Pre-Paid"
	}
