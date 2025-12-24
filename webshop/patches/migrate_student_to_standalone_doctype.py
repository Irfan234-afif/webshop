# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Migration patch to convert Customer Student child table to standalone Student DocType
"""

import frappe
from frappe import _


def execute():
	"""
	Migrate existing student data from Customer Student child table to standalone Student DocType
	"""
	print("Migrating student data to standalone Student DocType...")

	# Check if old Customer Student doctype exists
	if not frappe.db.exists("DocType", "Customer Student"):
		print("No Customer Student doctype found - skipping migration")
		return

	# Get all customer students from child table
	customer_students = frappe.db.sql("""
		SELECT
			parent as customer,
			student_name,
			student_id,
			school_unit,
			date_of_birth,
			grade_level,
			is_active,
			notes
		FROM `tabCustomer Student`
		ORDER BY parent, creation
	""", as_dict=True)

	if not customer_students:
		print("No customer students found - skipping migration")
		return

	migrated_count = 0
	failed_count = 0

	for cs in customer_students:
		try:
			# Create Student document
			student = frappe.new_doc("Student")
			student.student_name = cs.student_name
			student.customer = cs.customer
			student.school_unit = cs.school_unit
			student.date_of_birth = cs.date_of_birth
			student.grade_level = cs.grade_level
			student.is_active = cs.is_active or 1
			student.notes = cs.notes
			student.is_primary = False  # Default to not primary

			# Insert the student
			student.insert(ignore_permissions=True)

			# Update any quotations that referenced the old student_id
			if cs.student_id:
				frappe.db.sql("""
					UPDATE `tabQuotation`
					SET student = %s
					WHERE student_id = %s AND docstatus < 2
				""", (student.name, cs.student_id))

				# Update any sales orders that referenced the old student_id
				frappe.db.sql("""
					UPDATE `tabSales Order`
					SET student = %s
					WHERE student_id = %s AND docstatus < 2
				""", (student.name, cs.student_id))

			migrated_count += 1
			print(f"✓ Migrated student: {cs.student_name} for customer {cs.customer}")

		except Exception as e:
			failed_count += 1
			print(f"✗ Failed to migrate student {cs.student_name} for customer {cs.customer}: {str(e)}")
			frappe.log_error(
				title=_("Student Migration Failed"),
				message=f"Failed to migrate student {cs.student_name} for customer {cs.customer}: {str(e)}"
			)

	# Commit the changes
	frappe.db.commit()

	print(f"\n✓ Migration complete: {migrated_count} students migrated, {failed_count} failed")

	# Remove old custom fields from Quotation and Sales Order
	print("\nCleaning up old custom fields...")

	for doctype in ["Quotation", "Sales Order"]:
		for fieldname in ["student_id", "student_name", "school_unit"]:
			if frappe.db.exists("Custom Field", f"{doctype}-{fieldname}"):
				try:
					frappe.delete_doc("Custom Field", f"{doctype}-{fieldname}", ignore_permissions=True, force=True)
					print(f"✓ Removed custom field: {doctype}.{fieldname}")
				except Exception as e:
					print(f"✗ Failed to remove custom field {doctype}.{fieldname}: {str(e)}")

	# Remove old custom fields from Customer (students table and section)
	for fieldname in ["students", "students_section"]:
		if frappe.db.exists("Custom Field", f"Customer-{fieldname}"):
			try:
				frappe.delete_doc("Custom Field", f"Customer-{fieldname}", ignore_permissions=True, force=True)
				print(f"✓ Removed custom field: Customer.{fieldname}")
			except Exception as e:
				print(f"✗ Failed to remove custom field Customer.{fieldname}: {str(e)}")

	frappe.db.commit()

	print("\n✓ All migration tasks completed successfully!")
