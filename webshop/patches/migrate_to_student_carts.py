# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Migration patch to add student support to existing customers and carts
"""

import frappe
from frappe import _


def execute():
	"""
	Migrate existing carts and customers to support student linkage

	Steps:
	1. Create default "General" School Unit if it doesn't exist
	2. For each Individual Customer without students, create a default student
	3. Link existing shopping cart quotations to default students
	"""
	frappe.reload_doc("webshop", "doctype", "school_unit")
	frappe.reload_doc("webshop", "doctype", "customer_student")

	print("Starting migration to student-based carts...")

	# Step 1: Create default "General" school unit
	create_default_school_unit()

	# Step 2: Create default students for existing customers
	migrate_customers()

	# Step 3: Link existing carts to default students
	migrate_shopping_carts()

	print("Migration completed successfully!")


def create_default_school_unit():
	"""Create default 'General' school unit if it doesn't exist"""
	if not frappe.db.exists("School Unit", "GENERAL"):
		print("Creating default 'General' school unit...")

		unit = frappe.get_doc({
			"doctype": "School Unit",
			"unit_name": "General",
			"unit_code": "GENERAL",
			"description": "Default unit for existing students migrated from previous system",
			"is_active": 1
		})

		unit.insert(ignore_permissions=True)
		frappe.db.commit()

		print("✓ Default school unit created")
	else:
		print("✓ Default school unit already exists")


def migrate_customers():
	"""Create default students for customers that don't have any"""
	print("Migrating customers...")

	# Get all Individual customers
	customers = frappe.get_all(
		"Customer",
		filters={"customer_type": "Individual"},
		fields=["name", "customer_name"]
	)

	migrated_count = 0
	skipped_count = 0

	for customer in customers:
		try:
			customer_doc = frappe.get_doc("Customer", customer.name)

			# Skip if customer already has students
			if customer_doc.get("students"):
				skipped_count += 1
				continue

			# Create default student
			customer_doc.append("students", {
				"student_name": customer_doc.customer_name or customer_doc.name,
				"student_id": f"{customer_doc.name}-DEFAULT",
				"school_unit": "GENERAL",
				"is_active": 1
			})

			customer_doc.save(ignore_permissions=True)
			migrated_count += 1

			# Commit every 20 customers to avoid large transactions
			if migrated_count % 20 == 0:
				frappe.db.commit()
				print(f"  Processed {migrated_count} customers...")

		except Exception as e:
			print(f"  Error migrating customer {customer.name}: {str(e)}")
			frappe.log_error(f"Customer migration error: {str(e)}", "Student Migration")
			continue

	frappe.db.commit()
	print(f"✓ Migrated {migrated_count} customers, skipped {skipped_count} customers with existing students")


def migrate_shopping_carts():
	"""Link existing shopping cart quotations to default students"""
	print("Migrating shopping cart quotations...")

	# Get all draft shopping cart quotations without student linkage
	quotations = frappe.get_all(
		"Quotation",
		filters={
			"order_type": "Shopping Cart",
			"docstatus": 0,
			"student_id": ["in", [None, ""]]
		},
		fields=["name", "party_name"]
	)

	migrated_count = 0
	skipped_count = 0

	for quot in quotations:
		try:
			# Get customer's default student
			customer_doc = frappe.get_doc("Customer", quot.party_name)

			if not customer_doc.students:
				skipped_count += 1
				continue

			# Use first student as default
			default_student = customer_doc.students[0]

			# Update quotation with student info
			frappe.db.set_value(
				"Quotation",
				quot.name,
				{
					"student_id": default_student.student_id,
					"student_name": default_student.student_name,
					"school_unit": default_student.school_unit
				},
				update_modified=False
			)

			migrated_count += 1

			# Commit every 20 quotations
			if migrated_count % 20 == 0:
				frappe.db.commit()
				print(f"  Processed {migrated_count} quotations...")

		except Exception as e:
			print(f"  Error migrating quotation {quot.name}: {str(e)}")
			frappe.log_error(f"Quotation migration error: {str(e)}", "Student Migration")
			continue

	frappe.db.commit()
	print(f"✓ Migrated {migrated_count} quotations, skipped {skipped_count} quotations without customers")


def create_indexes():
	"""Create database indexes for better performance"""
	print("Creating database indexes...")

	try:
		# Index on customer_student.student_id
		frappe.db.sql("""
			ALTER TABLE `tabCustomer Student`
			ADD INDEX IF NOT EXISTS `idx_student_id` (`student_id`)
		""")

		# Index on customer_student.school_unit
		frappe.db.sql("""
			ALTER TABLE `tabCustomer Student`
			ADD INDEX IF NOT EXISTS `idx_school_unit` (`school_unit`)
		""")

		# Index on quotation.student_id
		frappe.db.sql("""
			ALTER TABLE `tabQuotation`
			ADD INDEX IF NOT EXISTS `idx_student_id` (`student_id`)
		""")

		# Index on sales_order.student_id
		frappe.db.sql("""
			ALTER TABLE `tabSales Order`
			ADD INDEX IF NOT EXISTS `idx_student_id` (`student_id`)
		""")

		frappe.db.commit()
		print("✓ Database indexes created")

	except Exception as e:
		print(f"  Warning: Could not create indexes - {str(e)}")
		# Don't fail the migration if indexes can't be created
		pass
