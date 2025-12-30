
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
		
		overdue_requests = frappe.get_all(
			"Payment Request",
			filters={
				"reference_doctype": "Sales Order",
				"docstatus": ["in", [0, 1]], 
				"status": ["not in", ["Paid", "Cancelled", "Failed"]],
				"payment_due_date": ["<", now_datetime()]
			},
			fields=["name", "reference_name", "status"]
		)
		
		for pr in overdue_requests:
			sales_order_name = pr.reference_name
			
			# Double check Sales Order status
			if not frappe.db.exists("Sales Order", sales_order_name):
				continue
				
			sales_order = frappe.get_doc("Sales Order", sales_order_name)
			
			# Skip if already completed or cancelled
			if sales_order.status in ["Completed", "Cancelled", "Closed"]:
				continue
				
			# Check if fully paid (via other means)
			if sales_order.per_billed >= 100 or sales_order.advance_paid >= sales_order.grand_total:
				continue
				
			frappe.log_error(
				f"Auto-cancelling overdue order {sales_order_name}. PR: {pr.name}", 
				"Auto Cancel Orders"
			)
			
			# Cancel the Sales Order
			# We need to submit it first if it's draft? No, cancel works on draft too but usually docstatus 2.
			# But user said "sales order should be auto cancelled".
			# If it's submitted (docstatus=1), we cancel it.
			# If it's draft (docstatus=0), we cancel it (delete or set status?).
			# Standard practice: Cancel means docstatus=2.
			
			try:
				if sales_order.docstatus == 0:
					# If draft, we can just cancel (set to 2)
					sales_order.cancel()
				elif sales_order.docstatus == 1:
					sales_order.cancel()
					
				# Also cancel the Payment Request
				pr_doc = frappe.get_doc("Payment Request", pr.name)
				if pr_doc.docstatus < 2:
					pr_doc.cancel()
					
				frappe.db.commit()
				
			except Exception as e:
				frappe.db.rollback()
				frappe.log_error(f"Failed to cancel order {sales_order_name}: {str(e)}", "Auto Cancel Failure")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Auto Cancel Job Error")
