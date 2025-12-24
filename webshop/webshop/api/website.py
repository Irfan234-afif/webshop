import frappe

@frappe.whitelist(allow_guest=True)
def get_banner_content(banner_key):
	"""
	Fetch Webshop Banner content by key.
	"""
	if not banner_key:
		return {}

	try:
		# Since banner_key is the name (autoname field:banner_key), we can try to get via get_doc or get_value
		# But wait, I set autoname to field:banner_key, so the "name" of the doc IS the key.
		# However, spaces in Select options might be handled differently in naming. 
		# "Home Hero" -> "Home Hero" usually.
		
		banner = frappe.db.get_value(
			"Webshop Banner",
			{"banner_key": banner_key, "is_active": 1},
			["type", "image", "title", "subtitle", "cta_text", "cta_url", "secondary_cta_text", "secondary_cta_url", "right_image"],
			as_dict=1
		)
		
		return banner or {}
	except Exception as e:
		frappe.log_error(f"Error fetching banner {banner_key}: {str(e)}")
		return {}
