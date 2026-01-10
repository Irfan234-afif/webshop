frappe.listview_settings['Return Request'] = {
	get_indicator: function(doc) {
		const status_colors = {
			"Draft": "red",
			"Pending Approval": "orange",
			"Approved": "blue",
			"Processing": "orange",
			"Completed": "green",
			"Rejected": "gray"
		};
		return [__(doc.status), status_colors[doc.status], "status,=," + doc.status];
	}
};
