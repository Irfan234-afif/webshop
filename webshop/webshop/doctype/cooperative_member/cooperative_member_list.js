frappe.listview_settings['Cooperative Member'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {
		if (doc.status === "Active") {
			return [__("Active"), "green", "status,=,Active"];
		} else if (doc.status === "Pending Approval") {
			return [__("Pending Approval"), "orange", "status,=,Pending Approval"];
		} else if (doc.status === "Pending Payment") {
			return [__("Pending Payment"), "yellow", "status,=,Pending Payment"];
		} else if (doc.status === "Rejected") {
			return [__("Rejected"), "red", "status,=,Rejected"];
		} else {
			return [__("Draft"), "gray", "status,=,Draft"];
		}
	}
};
