// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Return Request", {
	refresh(frm) {
		if (frm.doc.status) {
			const status_colors = {
				"Draft": "red",
				"Pending Approval": "orange",
				"Approved": "blue",
				"Processing": "orange",
				"Completed": "green",
				"Rejected": "gray"
			};
			frm.page.set_indicator(__(frm.doc.status), status_colors[frm.doc.status]);
		}

		if (frm.doc.docstatus === 1 && frm.doc.status === 'Approved') {
			frm.add_custom_button(__('Sales Return'), function() {
				frappe.model.open_mapped_doc({
					method: "webshop.webshop.doctype.return_request.return_request.make_return_delivery_note",
					frm: frm
				}, __('Create'));
			});
		}
	},
});
