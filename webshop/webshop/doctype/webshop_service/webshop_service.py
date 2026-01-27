import frappe
from frappe.model.document import Document
from frappe import _

class WebshopService(Document):
	def validate(self):
		if self.enabled:
			self.check_max_enabled()

	def check_max_enabled(self):
		# Count existing enabled services, excluding current one if it's already saved
		filters = {"enabled": 1}
		if not self.is_new():
			filters["name"] = ["!=", self.name]
			
		count = frappe.db.count("Webshop Service", filters=filters)
		
		if count >= 4:
			frappe.throw(_("You can only have a maximum of 4 enabled Webshop Services."))

	@frappe.whitelist()
	def get_services(self):
		# Helper meant to be called from API or standard list
		pass

@frappe.whitelist(allow_guest=True)
def get_active_services():
	"""
	Returns the list of active services with generated gradient string.
	"""
	services = frappe.get_all(
		"Webshop Service",
		filters={"enabled": 1},
		fields=["name", "title", "description", "route", "icon_svg", "icon_color", "gradient_start_color", "gradient_end_color"],
		order_by="creation asc",
		limit=4
	)
	
	for s in services:
		# Construct the gradient string expected by frontend
		# Default angle as seen in original code: 141.87deg
		# Fallback colors if missing
		start = s.gradient_start_color or "#AC208E"
		end = s.gradient_end_color or "#C263AD"
		s.bg_gradient = f"linear-gradient(141.87deg, {start} 0%, {end} 100.03%)"
		
	return services
