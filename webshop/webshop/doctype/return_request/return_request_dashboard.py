from frappe import _

def get_data():
	return {
		"fieldname": "return_request",
		"internal_links": {
			"Delivery Note": ["Delivery Note", "return_request"],
			"Sales Invoice": ["Sales Invoice", "return_request"],
		},
		"transactions": [
			{
				"label": _("Reference"),
				"items": ["Delivery Note", "Sales Invoice"],
			},
		],
	}
