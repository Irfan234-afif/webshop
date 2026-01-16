// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Webshop Payment Method', {
	onload: function(frm) {
		// Setup tax filters for payment_charges table (Sales Taxes and Charges)
		erpnext.accounts.taxes.setup_tax_filters("Sales Taxes and Charges");
	},
	
	refresh: function(frm) {
		// Additional refresh logic if needed
	}
});

// Setup grid for payment_charges child table
frappe.ui.form.on('Sales Taxes and Charges', {
	payment_charges_add: function(frm, cdt, cdn) {
		// When a new row is added to payment_charges table
		let row = locals[cdt][cdn];
		
		// Set default charge_type to Actual for fixed amounts
		if (!row.charge_type) {
			frappe.model.set_value(cdt, cdn, 'charge_type', 'Actual');
		}
	}
});