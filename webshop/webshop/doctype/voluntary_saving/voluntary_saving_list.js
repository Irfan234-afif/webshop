frappe.listview_settings['Voluntary Saving'] = {
	has_indicator_for_draft: true,
	has_indicator_for_cancelled: true,
	get_indicator: function (doc) {
		if (doc.status === "Approved") {
			return [__("Approved"), "green", "status,=,Approved"];
		} else if (doc.status === "Pending Payment") {
			return [__("Pending Payment"), "orange", "status,=,Pending Payment"];
		} else if (doc.status === "Pending Approval") {
			return [__("Pending Approval"), "orange", "status,=,Pending Approval"];
		} else if (doc.status === "Rejected" || doc.status === "Cancelled") {
			return [__("Rejected"), "red", "status,=,Rejected"];
		} else {
			return [__("Draft"), "grey", "status,=,Draft"];
		}
	}
};
