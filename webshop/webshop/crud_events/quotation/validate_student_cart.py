# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Validation hook for Quotation to ensure shopping cart quotations have student linkage
"""

import frappe
from frappe import _


def execute(doc, method=None):
	"""
	Validate that shopping cart quotations have student linkage if required

	Args:
		doc: Quotation document
		method: Hook method name (unused)
	"""
	# Only validate shopping cart quotations
	if doc.order_type != "Shopping Cart":
		return

	# Check webshop settings for student requirement
	try:
		webshop_settings = frappe.get_cached_doc("Webshop Settings")
		require_student = webshop_settings.get("require_student_for_cart", 0)
	except Exception:
		# Settings not available or field doesn't exist yet - skip validation
		return

	# If student is required and not set, throw error
	if require_student and not doc.get("student"):
		frappe.throw(
			_("Please select a student before adding items to cart"),
			title=_("Student Required")
		)
