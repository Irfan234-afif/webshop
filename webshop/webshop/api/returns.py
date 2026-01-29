# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Returns API Endpoints

Provides API endpoints for managing sales returns
"""

import frappe
from frappe import _
from frappe.utils import getdate, add_days, nowdate
from webshop.webshop.shopping_cart.cart import get_party


@frappe.whitelist()
def get_eligible_orders_for_return():
	"""
	Get customer's delivered sales orders eligible for return
	
	Returns:
		list: List of eligible sales orders with details
	"""
	# Check if returns are enabled
	settings = frappe.get_single("Webshop Settings")
	if not settings.get("enable_returns"):
		return []
	
	# Get current customer
	customer = get_party().name
	
	# Get eligibility days
	eligibility_days = settings.return_eligibility_days or 7
	cutoff_date = add_days(nowdate(), -eligibility_days)
	
	# Get delivered sales orders
	orders = frappe.db.sql("""
		SELECT DISTINCT
			so.name as sales_order,
			so.transaction_date,
			so.grand_total,
			dn.name as delivery_note,
			dn.posting_date as delivery_date
		FROM `tabSales Order` so
		INNER JOIN `tabDelivery Note Item` dni ON dni.against_sales_order = so.name
		INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent
		LEFT JOIN `tabReturn Request` rr ON rr.sales_order = so.name AND rr.docstatus != 2
		WHERE so.customer = %(customer)s
			AND so.docstatus = 1
			AND dn.docstatus = 1
			AND dn.is_return = 0
			AND dn.posting_date >= %(cutoff_date)s
			AND rr.name IS NULL
		ORDER BY dn.posting_date DESC
	""", {
		"customer": customer,
		"cutoff_date": cutoff_date
	}, as_dict=True)
	
	# Get items for each order
	for order in orders:
		items = frappe.get_all("Sales Order Item",
			filters={"parent": order.sales_order},
			fields=["item_code", "item_name", "qty", "rate", "amount"]
		)
		order["items"] = items
		order["days_since_delivery"] = (getdate(nowdate()) - getdate(order.delivery_date)).days
		order["eligible_until"] = add_days(order.delivery_date, eligibility_days)
	
	return orders


@frappe.whitelist()
def check_order_return_eligibility(sales_order):
	"""
	Check if a specific sales order is eligible for return
	
	Args:
		sales_order (str): Sales Order name
		
	Returns:
		dict: Eligibility status and reason
	"""
	# Check if returns are enabled
	settings = frappe.get_single("Webshop Settings")
	if not settings.get("enable_returns"):
		return {
			"eligible": False,
			"reason": "Returns are currently not available"
		}
	
	# Get current customer
	customer = get_party().name
	
	# Validate sales order belongs to customer
	so_customer = frappe.db.get_value("Sales Order", sales_order, "customer")
	if not so_customer:
		return {
			"eligible": False,
			"reason": "Order not found"
		}
	
	if so_customer != customer:
		return {
			"eligible": False,
			"reason": "Invalid order"
		}
	
	# Check if order has a submitted delivery note
	delivery_note = frappe.db.sql("""
		SELECT dn.name, dn.posting_date
		FROM `tabDelivery Note` dn
		INNER JOIN `tabDelivery Note Item` dni ON dni.parent = dn.name
		WHERE dni.against_sales_order = %(sales_order)s
			AND dn.docstatus = 1
			AND dn.is_return = 0
		LIMIT 1
	""", {"sales_order": sales_order}, as_dict=True)
	
	if not delivery_note:
		return {
			"eligible": False,
			"reason": "Order has not been delivered yet"
		}
	
	# Check if delivery is within return eligibility window
	eligibility_days = settings.return_eligibility_days or 7
	cutoff_date = add_days(nowdate(), -eligibility_days)
	delivery_date = delivery_note[0].posting_date
	
	if getdate(delivery_date) < getdate(cutoff_date):
		return {
			"eligible": False,
			"reason": f"Return window has expired (must be within {eligibility_days} days of delivery)"
		}
	
	# Check if return request already exists for this order
	existing_return = frappe.db.exists("Return Request", {
		"sales_order": sales_order,
		"docstatus": ["!=", 2]  # Not cancelled
	})
	
	if existing_return:
		return {
			"eligible": False,
			"reason": "A return request already exists for this order"
		}
	
	# Order is eligible
	return {
		"eligible": True,
		"reason": None,
		"delivery_date": delivery_date,
		"eligible_until": add_days(delivery_date, eligibility_days)
	}


@frappe.whitelist()
def get_return_reasons():
	"""
	Get active return reasons
	
	Returns:
		list: List of active return reasons
	"""
	reasons = frappe.get_all("Return Reason",
		filters={"enabled": 1},
		fields=["name", "reason_name", "description"],
		order_by="reason_name"
	)
	
	return reasons


@frappe.whitelist()
def get_refund_payment_methods():
	"""
	Get payment methods allowed for refunds
	
	Returns:
		list: List of payment methods with allow_on_return=1
	"""
	methods = frappe.get_all("Webshop Payment Method",
		filters={
			"enabled": 1,
			"allow_on_return": 1
		},
		fields=["name", "title", "payment_type", "mode_of_payment", "description"],
		order_by="sort_order"
	)
	
	return methods


@frappe.whitelist()
def create_return_request(data):
	"""
	Create a return request from frontend
	
	Args:
		data (dict): Return request data
		
	Returns:
		dict: Created return request details
	"""
	import json

	try:
		if isinstance(data, str):
			data = json.loads(data)
		
		# Get current customer
		customer = get_party().name
		
		# Validate sales order belongs to customer
		so_customer = frappe.db.get_value("Sales Order", data.get("sales_order"), "customer")
		if so_customer != customer:
			frappe.throw(_("Invalid Sales Order"))
		
		# Create return request
		doc = frappe.get_doc({
			"doctype": "Return Request",
			"sales_order": data.get("sales_order"),
			"return_reason": data.get("return_reason"),
			"other_reason": data.get("other_reason"),
			"supporting_documents": data.get("supporting_documents"),
			"refund_payment_mode": data.get("refund_payment_mode"),
			"bank_name": data.get("bank_name"),
			"account_number": data.get("account_number"),
			"account_holder_name": data.get("account_holder_name")
		})
		
		doc.insert(ignore_permissions=True)
		
		return {
			"name": doc.name,
			"sales_order": doc.sales_order,
			"status": doc.status
		}
	except Exception as e:
		frappe.log_error(f"Error creating return request", e)
		frappe.throw(f"Error creating return request: {str(e)}")


@frappe.whitelist()
def get_customer_return_requests(filters=None):
	"""
	Get customer's return requests with filtering
	
	Args:
		filters (dict): Optional filters
		
	Returns:
		list: List of return requests
	"""
	import json

	if not filters:
		filters = {}

	if isinstance(filters, str):
		filters = json.loads(filters) if filters else {}
	
	# Get current customer
	customer = get_party().name
	
	# Build filters
	query_filters = {
		"customer": customer
	}
	
	status_filter = filters.get("status")
	if status_filter:
		if status_filter == "Pending Approval":
			query_filters["status"] = ["in", ["Draft", "Pending Approval"]]
		else:
			query_filters["status"] = status_filter
	
	# Get return requests
	requests = frappe.get_all("Return Request",
		filters=query_filters,
		fields=[
			"name",
			"sales_order",
			"posting_date",
			"return_reason",
			"refund_payment_mode",
			"status",
			"return_delivery_note",
			"credit_note",
			"bank_name",
			"account_number",
			"account_holder_name",
			"other_reason"
		],
		order_by="posting_date desc",
		start=filters.get("start", 0),
		page_length=filters.get("page_length", 20)
	)

	# Fetch additional details for each request
	for req in requests:
		# Get Sales Order details
		so = frappe.db.get_value("Sales Order", req.sales_order, 
			["grand_total", "student", "transaction_date"], as_dict=True)
		
		if so:
			req.grand_total = so.grand_total
			req.transaction_date = so.transaction_date
			req.student = so.student
			
			if so.student:
				req.student_name = frappe.db.get_value("Student", so.student, "student_name")

			# Get Delivery Note for pickup/delivery info
			dn = frappe.db.get_value("Delivery Note Item", 
				{"against_sales_order": req.sales_order, "docstatus": 1}, 
				"parent")
			
			# Dynamic fetch of optional fields from Sales Order
			optional_fields = ["pickup_type", "pickup_schedule", "virtual_account", "payment_method_type"]
			so_meta = frappe.get_meta("Sales Order")
			fields_to_fetch = [f for f in optional_fields if so_meta.has_field(f)]
			
			if fields_to_fetch:
				so_details = frappe.db.get_value("Sales Order", req.sales_order, fields_to_fetch, as_dict=True)
				if so_details:
					for field in fields_to_fetch:
						req[field] = so_details.get(field)

	return requests


@frappe.whitelist()
def get_return_request_detail(name):
	"""
	Get complete return request details
	
	Args:
		name (str): Return Request name
		
	Returns:
		dict: Complete return request details
	"""
	# Get current customer
	customer = get_party().name
	
	# Validate ownership
	doc_customer = frappe.db.get_value("Return Request", name, "customer")
	if doc_customer != customer:
		frappe.throw(_("Access denied"))
	
	# Get return request
	doc = frappe.get_doc("Return Request", name)
	
	# Get payment method details
	payment_method = None
	if doc.refund_payment_mode:
		payment_method = frappe.get_doc("Webshop Payment Method", doc.refund_payment_mode)
	
	# Get return delivery note details
	return_delivery_note_image = None
	if doc.return_delivery_note:
		return_delivery_note_image = frappe.db.get_value("Delivery Note", doc.return_delivery_note, "image")

	return {
		"name": doc.name,
		"sales_order": doc.sales_order,
		"customer": doc.customer,
		"posting_date": doc.posting_date,
		"return_reason": doc.return_reason,
		"other_reason": doc.other_reason,
		"supporting_documents": doc.supporting_documents,
		"refund_payment_mode": doc.refund_payment_mode,
		"payment_method_title": payment_method.title if payment_method else None,
		"payment_type": payment_method.payment_type if payment_method else None,
		"bank_name": doc.bank_name,
		"account_number": doc.account_number,
		"account_holder_name": doc.account_holder_name,
		"items": [
			{
				"item_code": item.item_code,
				"item_name": item.item_name,
				"qty": item.qty,
				"rate": item.rate,
				"amount": item.amount
			}
			for item in doc.items
		],
		"status": doc.status,
		"return_delivery_note": doc.return_delivery_note,
		"return_proof_image": return_delivery_note_image,
		"credit_note": doc.credit_note
	}


@frappe.whitelist()
def process_return_documents(return_request_name):
	"""
	Process return documents - create Delivery Note (Return) and Credit Note
	Admin only function
	
	Args:
		return_request_name (str): Return Request name
		
	Returns:
		dict: Created document names
	"""
	# Check permissions
	if not frappe.has_permission("Return Request", "write"):
		frappe.throw(_("Insufficient permissions"))
	
	# Get return request
	doc = frappe.get_doc("Return Request", return_request_name)
	
	# Call the method
	result = doc.create_return_documents()
	
	frappe.db.commit()
	
	return result
