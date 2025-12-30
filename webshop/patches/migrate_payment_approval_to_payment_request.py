# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to migrate existing Payment Approval records to Payment Request DocType
and clean up the old Payment Approval DocType
"""

import frappe
import os
import shutil


def execute():
	"""
	Migrate existing Payment Approval records to Payment Request
	and clean up old DocType
	"""
	print("=" * 80)
	print("MIGRATING PAYMENT APPROVAL TO PAYMENT REQUEST")
	print("=" * 80)

	# Step 1: Migrate existing Payment Approval records
	migrate_payment_approvals()

	# Step 2: Delete Payment Approval DocType
	cleanup_payment_approval_doctype()

	print("\n" + "=" * 80)
	print("MIGRATION COMPLETED SUCCESSFULLY")
	print("=" * 80)


def migrate_payment_approvals():
	"""Migrate existing Payment Approval records to Payment Request"""
	print("\n[1/2] Migrating Payment Approval records to Payment Request...")

	# Check if Payment Approval DocType exists
	if not frappe.db.exists("DocType", "Payment Approval"):
		print("  ℹ Payment Approval DocType not found - skipping migration")
		return

	# Get all Payment Approval records
	payment_approvals = frappe.get_all(
		"Payment Approval",
		fields=["name", "sales_order", "payment_method", "customer", "amount",
				"status", "payment_proof", "admin_approval_by", "admin_approval_time", "remarks"],
		order_by="creation"
	)

	if not payment_approvals:
		print("  ℹ No Payment Approval records found to migrate")
		return

	migrated_count = 0
	failed_count = 0
	skipped_count = 0

	print(f"  Found {len(payment_approvals)} Payment Approval records to migrate")

	for pa in payment_approvals:
		try:
			# Check if Payment Request already exists for this Sales Order
			existing_pr = frappe.get_all(
				"Payment Request",
				filters={
					"reference_doctype": "Sales Order",
					"reference_name": pa.sales_order
				},
				limit=1
			)

			if existing_pr:
				print(f"  ⊘ Skipped {pa.name}: Payment Request already exists for Sales Order {pa.sales_order}")
				skipped_count += 1
				continue

			# Get Sales Order details
			if not frappe.db.exists("Sales Order", pa.sales_order):
				print(f"  ⊘ Skipped {pa.name}: Sales Order {pa.sales_order} not found")
				skipped_count += 1
				continue

			sales_order = frappe.get_doc("Sales Order", pa.sales_order)

			# Create Payment Request
			pr = frappe.new_doc("Payment Request")
			pr.payment_request_type = "Inward"
			pr.reference_doctype = "Sales Order"
			pr.reference_name = pa.sales_order
			pr.party_type = "Customer"
			pr.party = pa.customer
			pr.party_name = frappe.get_cached_value("Customer", pa.customer, "customer_name")
			pr.grand_total = pa.amount
			pr.currency = sales_order.currency
			pr.company = sales_order.company
			pr.email_to = sales_order.contact_email or frappe.session.user
			pr.subject = f"Payment for Sales Order {pa.sales_order}"
			pr.mute_email = 1

			# Custom fields
			pr.payment_proof = pa.payment_proof
			pr.remarks = pa.remarks
			pr.admin_approval_by = pa.admin_approval_by
			pr.admin_approval_time = pa.admin_approval_time

			# Map status to docstatus
			if pa.status == "Pending":
				# Insert as Draft (docstatus = 0)
				pr.insert(ignore_permissions=True)

			elif pa.status == "Approved":
				# Insert and submit (docstatus = 1)
				pr.insert(ignore_permissions=True)
				pr.submit()
				# Mark as paid
				try:
					pr.set_as_paid()
				except Exception as e:
					print(f"  ⚠ Warning: Could not mark PR {pr.name} as paid: {str(e)}")

			elif pa.status == "Rejected":
				# Insert as Draft, then cancel (docstatus = 2)
				pr.insert(ignore_permissions=True)
				pr.cancel()

			frappe.db.commit()

			# Delete old Payment Approval record
			frappe.delete_doc("Payment Approval", pa.name, force=True, ignore_permissions=True)

			migrated_count += 1
			print(f"  ✓ Migrated {pa.name} ({pa.status}) → Payment Request {pr.name}")

		except Exception as e:
			failed_count += 1
			frappe.log_error(
				message=frappe.get_traceback(),
				title=f"Failed to migrate Payment Approval {pa.name}"
			)
			print(f"  ✗ Failed to migrate {pa.name}: {str(e)}")
			continue

	print(f"\n  Migration Summary:")
	print(f"    Successfully migrated: {migrated_count}")
	print(f"    Skipped: {skipped_count}")
	print(f"    Failed: {failed_count}")
	print(f"    Total: {len(payment_approvals)}")


def cleanup_payment_approval_doctype():
	"""Delete Payment Approval DocType and related files"""
	print("\n[2/2] Cleaning up Payment Approval DocType...")

	# 1. Delete DocType from database
	if frappe.db.exists("DocType", "Payment Approval"):
		try:
			frappe.delete_doc("DocType", "Payment Approval", force=True, ignore_permissions=True)
			print("  ✓ Deleted Payment Approval DocType from database")
		except Exception as e:
			print(f"  ⚠ Warning: Could not delete Payment Approval DocType: {str(e)}")
	else:
		print("  ℹ Payment Approval DocType already deleted")

	# 2. Delete template pages
	try:
		template_file = frappe.get_app_path("webshop", "templates", "pages", "payment_approvals.py")
		template_html = frappe.get_app_path("webshop", "templates", "pages", "payment_approvals.html")

		if os.path.exists(template_file):
			os.remove(template_file)
			print(f"  ✓ Deleted {template_file}")

		if os.path.exists(template_html):
			os.remove(template_html)
			print(f"  ✓ Deleted {template_html}")
	except Exception as e:
		print(f"  ⚠ Warning: Could not delete template files: {str(e)}")

	# 3. Delete DocType directory
	try:
		doctype_path = frappe.get_app_path("webshop", "webshop", "doctype", "payment_approval")
		if os.path.exists(doctype_path):
			shutil.rmtree(doctype_path)
			print(f"  ✓ Deleted directory {doctype_path}")
	except Exception as e:
		print(f"  ⚠ Warning: Could not delete DocType directory: {str(e)}")

	frappe.db.commit()
	print("  ✓ Cleanup completed")
