# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SchoolUnit(Document):
	"""School Unit DocType - represents divisions like High School, Elementary, etc."""

	def validate(self):
		"""Validation hook"""
		# Ensure unit_code is uppercase for consistency
		if self.unit_code:
			self.unit_code = self.unit_code.upper()

	def on_update(self):
		"""Called after save"""
		pass

	def on_trash(self):
		"""Called before delete"""
		# Check if any students are linked to this unit
		linked_students = frappe.db.count("Student", {"school_unit": self.name})

		if linked_students > 0:
			frappe.throw(
				frappe._("Cannot delete School Unit '{0}' as it is linked to {1} student(s). Please reassign or remove students first.").format(
					self.unit_name, linked_students
				)
			)
