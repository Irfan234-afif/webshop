# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerStudent(Document):
	"""Customer Student Child DocType - represents a student/child linked to a parent/customer"""

	def validate(self):
		"""Validation hook"""
		# Auto-generate student_id if not provided
		if not self.student_id:
			self.student_id = self.generate_student_id()

	def generate_student_id(self):
		"""Generate unique student ID"""
		import random
		import string

		# Get parent customer name
		parent_name = self.parent

		# Generate random suffix
		random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

		# Format: CUSTOMERNAME-RANDOMSUFFIX
		student_id = f"{parent_name}-{random_suffix}"

		# Ensure uniqueness
		while frappe.db.exists("Customer Student", {"student_id": student_id}):
			random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
			student_id = f"{parent_name}-{random_suffix}"

		return student_id

	def on_trash(self):
		"""Called before delete - check for linked carts/orders"""
		# Check if any quotations are linked to this student
		linked_quotations = frappe.db.count("Quotation", {"student_id": self.student_id, "docstatus": 0})

		if linked_quotations > 0:
			frappe.msgprint(
				frappe._("Warning: {0} draft quotation(s) are linked to this student. They will not be accessible after deletion.").format(
					linked_quotations
				),
				indicator="orange"
			)

		# Check if any sales orders are linked to this student
		linked_orders = frappe.db.count("Sales Order", {"student_id": self.student_id})

		if linked_orders > 0:
			frappe.msgprint(
				frappe._("Warning: {0} sales order(s) are linked to this student. Historical data will remain but student reference will be broken.").format(
					linked_orders
				),
				indicator="orange"
			)
