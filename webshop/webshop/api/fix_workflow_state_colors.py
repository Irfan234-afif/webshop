import frappe


def execute():
	"""
	Set style/color on Workflow States used by Cooperative Member workflow.
	Run with: bench execute webshop.webshop.api.fix_workflow_state_colors.execute
	"""
	state_styles = {
		"Draft": "",
		"Pending Approval": "Warning",
		"Pending Payment": "Warning",
		"Active": "Success",
		"Rejected": "Danger",
	}

	for state_name, style in state_styles.items():
		if frappe.db.exists("Workflow State", state_name):
			frappe.db.set_value("Workflow State", state_name, "style", style)
			print(f"Set Workflow State '{state_name}' style to '{style or '(empty)'}'")
		else:
			print(f"Workflow State '{state_name}' not found, skipping.")

	frappe.db.commit()
	print("Done. Please run 'bench clear-cache' and refresh the browser.")
