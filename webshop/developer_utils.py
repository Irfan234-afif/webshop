import frappe
import json

def print_custom_fields_config():
	"""
	Prints all Custom Fields in the system dictionary format
	ready to be pasted into install.py
	"""
	print("\nGenerating Custom Fields Config...\n")
	
	# Fetch all custom fields for Webshop module
	# Make sure your custom fields in the system have Module set to 'Webshop'
	custom_fields = frappe.get_all(
		"Custom Field",
		filters={"module": "Webshop"},
		fields="*",
		order_by="dt asc, idx asc"
	)
	
	# Organize by DoctType
	fields_by_doctype = {}
	
	# Fields to exclude from the output
	exclude_fields = [
		"name", "creation", "modified", "modified_by", "owner", 
		"docstatus", "idx", "dt", "_user_tags", "_comments", 
		"_assign", "_liked_by", "standard_error", "module"
	]

	for field in custom_fields:
		doctype = field.pop("dt")
		
		# Clean up the field dict
		cleaned_field = {}
		for key, value in field.items():
			# Skip excluded fields
			if key in exclude_fields:
				continue
				
			# Skip empty/None values to keep it clean, except specific ones like default which could be 0
			if value is None or value == "":
				continue
				
			# Skip default 0 for checkbox if you want minimal diff, but usually 0 is explicit for check.
			# Let's keep 0.
			
			# Add to cleaned dict
			cleaned_field[key] = value

		if doctype not in fields_by_doctype:
			fields_by_doctype[doctype] = []
		
		fields_by_doctype[doctype].append(cleaned_field)

	# Convert to formatted JSON string but looks like Python dict
	# We can use json.dumps with indent, but we want it to look valid in Python code
	# which JSON mostly is, except needed True/False/None adjustment
	
	output = "custom_fields = {\n"
	
	for doctype, fields in fields_by_doctype.items():
		output += f'\t"{doctype}": [\n'
		for f in fields:
			output += "\t\t{\n"
			for key, value in f.items():
				# Format value based on type
				val_str = repr(value)
				output += f'\t\t\t"{key}": {val_str},\n'
			output += "\t\t},\n"
		output += "\t],\n"
	
	output += "}"
	
	print(output)
	print("\n\n" + "-"*50)
	print("Copy the dictionary above into your install.py's add_custom_fields function.")
	print("-"*50 + "\n")
