import frappe


def execute():
	"""
	Data migration patch for Cooperative Member Workflow adoption.

	The Workflow definition itself is loaded via fixtures (hooks.py).
	This patch handles existing data that needs to be migrated:
	  1. Reset docstatus=1 records back to 0 (DocType is now non-Submittable)
	  2. Backfill workflow_state = status for all existing records
	"""
	frappe.reload_doc("webshop", "doctype", "cooperative_member")

	# Reset any previously-submitted records back to Draft docstatus
	frappe.db.sql("UPDATE `tabCooperative Member` SET docstatus=0 WHERE docstatus=1")
	frappe.db.commit()

	# Backfill workflow_state from status for all existing records
	# (workflow_state column is added by bench migrate when the Workflow fixture is synced)
	try:
		frappe.db.sql("""
			UPDATE `tabCooperative Member`
			SET workflow_state = status
			WHERE status != workflow_state
			   OR workflow_state IS NULL
			   OR workflow_state = ''
		""")
		frappe.db.commit()
	except Exception:
		pass  # Column may not exist yet on very first migrate — fixtures will handle it
