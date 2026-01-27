import frappe

@frappe.whitelist(allow_guest=True)
def get_offers():
	def _get_offers():
		return frappe.get_all(
			"Webshop Offers",
			fields=["title", "highlight", "subtitle", "description", "image", "theme_color", "cta_url"],
			filters={"is_active": 1},
			order_by="creation asc"
		)
	
	return _get_offers()
