import frappe
from frappe.utils import now_datetime

def cancel_overdue_orders():
	"""
	Scheduled task to cancel overdue Sales Orders.
	Checks for Payment Requests that are past their due date and not paid.
	"""
	try:
		# Find overdue Payment Requests that are not Paid/Cancelled
		# docstatus: 0=Draft, 1=Submitted, 2=Cancelled
		# status: 'Paid' is final success state
		# We check for payment_due_date < now
		
		# 1. Cancel if payment_method_type is NOT "Transfer Bank"
		non_transfer_requests = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Order",
				"docstatus": ["in", [0,1]], 
				"status": ["not in", ["Paid", "Cancelled"]],
				"payment_due_date": ["<", now_datetime()],
				"payment_method_type": ["!=", "Transfer Bank"]
			},
			fields=["name", "reference_name", "status", "payment_due_date"]
		)

		# 2. Cancel if payment_method_type IS "Transfer Bank" AND payment_proof is NOT set
		transfer_requests_no_proof = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Order",
				"docstatus": ["in", [0,1]], 
				"status": ["not in", ["Paid", "Cancelled"]],
				"payment_due_date": ["<", now_datetime()],
				"payment_method_type": "Transfer Bank",
				"payment_proof": ["is", "not set"]
			},
			fields=["name", "reference_name", "status", "payment_due_date"]
		)
		
		overdue_requests = non_transfer_requests + transfer_requests_no_proof
		
		for pr in overdue_requests:
			execute_cancel_order(pr)

	except Exception as e:
		frappe.log_error("Auto Cancel Job Error", frappe.get_traceback())

def execute_cancel_order(pr):
	sales_order_name = pr.reference_name
	
	# Double check Sales Order status
	if not frappe.db.exists("Sales Order", sales_order_name):
		return
		
	sales_order = frappe.get_doc("Sales Order", sales_order_name)
	
	# Skip if already completed or cancelled
	if sales_order.status in ["Completed", "Cancelled", "Closed"]:
		return
		
	# Check if fully paid (via other means)
	if sales_order.per_billed >= 100 or sales_order.advance_paid >= sales_order.grand_total:
		return
		
	frappe.log_error(
		f"Auto-cancelling overdue order {sales_order_name}. PR: {pr.name}", 
		"Auto Cancel Orders"
	)
	
	try:
		# Also cancel the Payment Request
		pr_doc = frappe.get_doc("Payment Request", pr.name)
		if pr_doc.docstatus == 1:
			pr_doc.cancel()
			sales_order.reload()
		else:
			pr_doc.db_set("docstatus", 2)
			# pr_doc.on_cancel()

		if sales_order.docstatus == 0:
			# If draft, manual cancel() throws transition error
			# So we force docstatus 2 and run on_cancel to clean up (e.g. reserved stock)
			sales_order.db_set("docstatus", 2)
			# sales_order.on_cancel()
		elif sales_order.docstatus == 1:
			sales_order.cancel()
			
		frappe.db.commit()
		
	except Exception as e:
		frappe.db.rollback()
		frappe.log_error(f"Failed to cancel order {sales_order_name}: {str(e)}", frappe.get_traceback())
	