import frappe

def close_so_on_full_return(doc, method=None):
	"""
	Closes the Sales Order if it is fully returned.
	Triggered on Sales Invoice / Delivery Note on_submit.
	"""
	if not doc.is_return:
		return

	sales_orders = set()
	
	# Collect Sales Orders from items
	for item in doc.items:
		# Sales Invoice Item uses 'sales_order'
		# Delivery Note Item uses 'against_sales_order'
		so_name = item.get("sales_order") or item.get("against_sales_order")
		
		# If we have a reference, track it
		if so_name:
			sales_orders.add(so_name)

	for so_name in sales_orders:
		check_and_close_sales_order(so_name)

def check_and_close_sales_order(so_name):
	so_doc = frappe.get_doc("Sales Order", so_name)
	
	# Reload to ensure we have latest returned_qty if needed
	# (Though get_doc should fetch fresh from DB, standard ledger updates happen in on_submit of Return Doc)
	
	all_returned = True
	
	for item in so_doc.items:
		# Tolerate float precision issues if any, but standard compare is usually fine
		# Check if stock is returned (Physical Return)
		stock_returned = item.returned_qty >= item.qty
		
		# Check if amount is credited (Financial Return)
		# billed_amt reduces on Credit Note (Return Sales Invoice)
		# We check if billed_amt is zero (or negative due to some edge case)
		# If billed_amt <= 0, it means the item is fully credited or was never billed.
		# Combined with stock_returned=True, it implies "Back to square one".
		financial_returned = item.billed_amt <= 0.0

		if not (stock_returned and financial_returned):
			all_returned = False
			break
	
	if all_returned:
		if so_doc.status != "Closed":
			# Use db_set to avoid triggering validations that might block closing
			# or use workflow action if applicable. Standard way is Update status.
			# But 'Closed' is a standard status.
			
			# We also add a comment
			msg = "Sales Order closed automatically because all items were returned."
			frappe.msgprint(msg)
			# so_doc.add_comment("Info", msg)
			
			# Update status
			so_doc.db_set("status", "Closed")
