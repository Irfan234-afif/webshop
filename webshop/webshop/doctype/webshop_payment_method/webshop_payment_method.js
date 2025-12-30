// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Webshop Payment Method', {
	setup: function(frm) {
		// Set up any form-level configurations
	},
	
	refresh: function(frm) {
		// Show/hide fields based on payment type
		toggle_fields_visibility(frm);
	},
	
	payment_type: function(frm) {
		toggle_fields_visibility(frm);
	}
});

function toggle_fields_visibility(frm) {
	if (frm.doc.payment_type === "Transfer Manual") {
		frm.toggle_display("payment_gateway_account", false);
		frm.toggle_display("bank_account", true);
		frm.toggle_display("account_holder_name", true);
	} else if (frm.doc.payment_type === "Payment Gateway") {
		frm.toggle_display("payment_gateway_account", true);
		frm.toggle_display("bank_account", false);
		frm.toggle_display("account_holder_name", false);
	} else {
		frm.toggle_display("payment_gateway_account", false);
		frm.toggle_display("bank_account", false);
		frm.toggle_display("account_holder_name", false);
	}
}