# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Student(Document):
	def validate(self):
		"""Validate student data"""
		self.validate_school_unit()
		self.validate_date_of_birth()

	def validate_school_unit(self):
		"""Ensure school unit exists and is active"""
		if self.school_unit:
			school_unit = frappe.get_cached_value(
				"School Unit",
				self.school_unit,
				["is_active"],
				as_dict=True
			)
			if school_unit and not school_unit.is_active:
				frappe.throw(_("School Unit {0} is not active").format(frappe.bold(self.school_unit)))

	def validate_date_of_birth(self):
		"""Validate date of birth is not in future"""
		if self.date_of_birth:
			from frappe.utils import getdate, today
			if getdate(self.date_of_birth) > getdate(today()):
				frappe.throw(_("Date of Birth cannot be in the future"))

	def on_trash(self):
		"""Check for linked quotations and sales orders before deletion"""
		self.check_linked_transactions()

	def check_linked_transactions(self):
		"""Prevent deletion if student has linked quotations or sales orders"""
		# Check for linked quotations
		quotations = frappe.get_all(
			"Quotation",
			filters={"student": self.name, "docstatus": ["<", 2]},
			fields=["name"],
			limit=5
		)
		if quotations:
			quotation_links = ", ".join([frappe.bold(q.name) for q in quotations])
			frappe.throw(
				_("Cannot delete Student {0} as it is linked to Quotation(s): {1}").format(
					frappe.bold(self.name),
					quotation_links
				),
				title=_("Student Linked to Transactions")
			)

		# Check for linked sales orders
		sales_orders = frappe.get_all(
			"Sales Order",
			filters={"student": self.name, "docstatus": ["<", 2]},
			fields=["name"],
			limit=5
		)
		if sales_orders:
			order_links = ", ".join([frappe.bold(so.name) for so in sales_orders])
			frappe.throw(
				_("Cannot delete Student {0} as it is linked to Sales Order(s): {1}").format(
					frappe.bold(self.name),
					order_links
				),
				title=_("Student Linked to Transactions")
			)


def get_students_for_customer(customer):
	"""Get all students linked to a customer

	Args:
		customer (str): Customer name

	Returns:
		list: List of student dictionaries
	"""
	if not customer:
		return []

	students = frappe.get_all(
		"Student",
		filters={"customer": customer},
		fields=["name", "student_name", "school_unit", "date_of_birth", "grade_level", "is_active", "is_primary", "notes"],
		order_by="is_primary desc, creation asc"
	)

	return students
