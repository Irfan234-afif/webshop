
import frappe
from frappe import _
from webshop.webshop.shopping_cart.cart import get_party

@frappe.whitelist()
def get_unpaid_bills():
	"""
	Fetch unpaid Sales Invoices linked to Subscriptions for the current user.
	"""
	party = get_party()
	if not party:
		frappe.throw(_("No link to a Customer found for this user."), title=_("Authentication Required"))

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={
			"customer": party.name,
			"docstatus": 1, 
			"outstanding_amount": [">", 0],
			"subscription": ["is", "set"] # Only subscription-generated invoices
		},
		fields=[
			"name",
			"posting_date",
			"due_date",
			"grand_total",
			"outstanding_amount",
			"currency",
			"subscription",
			"status"
		],
		order_by="due_date asc"
	)

	return {
		"bills": invoices
	}
