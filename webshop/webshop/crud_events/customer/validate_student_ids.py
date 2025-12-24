# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Validation hook for Customer to ensure student IDs are unique
"""

import frappe
from frappe import _


def execute(doc, method=None):
	"""
	Ensure student IDs are unique within customer and globally

	Args:
		doc: Customer document
		method: Hook method name (unused)
	"""
	if not doc.get("students"):
		return

	# Track student IDs within this document
	student_ids_in_doc = []

	for student in doc.students:
		if not student.student_id:
			continue

		# Check for duplicates within this customer
		if student.student_id in student_ids_in_doc:
			frappe.throw(
				_("Student ID {0} is duplicated in this customer record").format(
					frappe.bold(student.student_id)
				),
				title=_("Duplicate Student ID")
			)

		student_ids_in_doc.append(student.student_id)

		# Check for duplicates globally (across all customers)
		existing = frappe.db.sql("""
			SELECT parent
			FROM `tabCustomer Student`
			WHERE student_id = %s AND parent != %s
		""", (student.student_id, doc.name))

		if existing:
			frappe.throw(
				_("Student ID {0} already exists in customer {1}").format(
					frappe.bold(student.student_id),
					frappe.bold(existing[0][0])
				),
				title=_("Student ID Already Exists")
			)
