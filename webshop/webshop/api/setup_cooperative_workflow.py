import frappe

def execute():
	frappe.reload_doc("webshop", "doctype", "cooperative_member")
	
	# 1. Reset docstatus of existing records to 0
	frappe.db.sql("UPDATE `tabCooperative Member` SET docstatus=0 WHERE docstatus=1")
	frappe.db.commit()

	# 2. Create Workflow States
	states = {
		"Draft": "",
		"Pending Approval": "Warning",
		"Pending Payment": "Warning",
		"Active": "Success",
		"Rejected": "Danger"
	}
	for state, style in states.items():
		if not frappe.db.exists("Workflow State", state):
			doc = frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state
			})
			if style:
				doc.style = style
			doc.insert(ignore_permissions=True)
		else:
			if style:
				frappe.db.set_value("Workflow State", state, "style", style)

	# 3. Create Workflow Actions
	actions = ["Submit for Review", "Approve", "Reject", "Resubmit"]
	for action in actions:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action
			}).insert(ignore_permissions=True)

	# 4. Create Workflow
	workflow_name = "Cooperative Registration Flow"
	if not frappe.db.exists("Workflow", workflow_name):
		wf = frappe.new_doc("Workflow")
		wf.workflow_name = workflow_name
		wf.document_type = "Cooperative Member"
		wf.is_active = 1
		wf.workflow_state_field = "workflow_state"
		
		# Set States
		# All our states are Doc Status 0 now since the DocType is no longer submittable
		wf_states = [
			{"state": "Draft", "doc_status": "0", "allow_edit": "System Manager", "update_field": "status", "update_value": "Draft"},
			{"state": "Draft", "doc_status": "0", "allow_edit": "Customer", "update_field": "status", "update_value": "Draft"},
			{"state": "Pending Approval", "doc_status": "0", "allow_edit": "System Manager", "update_field": "status", "update_value": "Pending Approval"},
			{"state": "Pending Payment", "doc_status": "0", "allow_edit": "System Manager", "update_field": "status", "update_value": "Pending Payment"},
			{"state": "Active", "doc_status": "0", "allow_edit": "System Manager", "update_field": "status", "update_value": "Active"},
			{"state": "Rejected", "doc_status": "0", "allow_edit": "System Manager", "update_field": "status", "update_value": "Rejected"}
		]
		
		# To avoid duplicating roles per state in Frappe UI array, just add the broadest permission:
		# Customer can edit Draft, System Manager can edit everything
		for s in wf_states:
			wf.append("states", s)

		# Set Transitions
		transitions = [
			{"state": "Draft", "action": "Submit for Review", "next_state": "Pending Approval", "allowed": "Customer", "allow_self_approval": 1},
			{"state": "Draft", "action": "Submit for Review", "next_state": "Pending Approval", "allowed": "System Manager"},
			{"state": "Pending Approval", "action": "Approve", "next_state": "Pending Payment", "allowed": "System Manager"},
			{"state": "Pending Approval", "action": "Reject", "next_state": "Rejected", "allowed": "System Manager"},
			# Resubmit
			{"state": "Rejected", "action": "Resubmit", "next_state": "Pending Approval", "allowed": "Customer", "allow_self_approval": 1},
			{"state": "Rejected", "action": "Resubmit", "next_state": "Pending Approval", "allowed": "System Manager"}
		]
		
		for t in transitions:
			wf.append("transitions", t)
			
		wf.insert(ignore_permissions=True)
		print(f"Workflow '{workflow_name}' created successfully.")
	else:
		print(f"Workflow '{workflow_name}' already exists.")

	# 5. Provide initial workflow_state for existing records
	# This must run AFTER the workflow is created because workflow creation adds the column
	try:
		frappe.db.sql("UPDATE `tabCooperative Member` SET workflow_state = status WHERE workflow_state IS NULL OR workflow_state = ''")
		frappe.db.commit()
	except Exception as e:
		print(f"Failed to update workflow_state: {e}")


def sync_workflow_states():
	"""
	Fix existing Cooperative Member records where workflow_state doesn't match status.
	Run with: bench execute webshop.webshop.api.setup_cooperative_workflow.sync_workflow_states
	"""
	updated = frappe.db.sql("""
		UPDATE `tabCooperative Member`
		SET workflow_state = status
		WHERE status != workflow_state
		   OR workflow_state IS NULL
		   OR workflow_state = ''
	""")
	frappe.db.commit()
	print(f"Synced workflow_state = status for all mismatched Cooperative Member records.")
