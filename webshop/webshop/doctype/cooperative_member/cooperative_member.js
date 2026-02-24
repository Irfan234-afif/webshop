// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cooperative Member', {
	refresh: function(frm) {
		// Only show button if status is Pending Payment and no existing payment request
		if (frm.doc.status === 'Pending Payment') {
			// Check if there is already a payment request
			frappe.db.get_list('Payment Request', {
				filters: {
					'reference_doctype': 'Cooperative Member',
					'reference_name': frm.doc.name,
					'docstatus': ['<', 2] // Not cancelled
				}
			}).then(records => {
				if (records.length === 0) {
					frm.add_custom_button(__('Create Payment Request'), function() {
						create_payment_request(frm);
					}, __('Actions'));
				} else {
					frm.add_custom_button(__('View Payment Request'), function() {
						frappe.set_route('Form', 'Payment Request', records[0].name);
					}, __('Actions'));
				}
			});
		}
		
		// Show "Create Next Year Saving" button for active members
		if (frm.doc.status === 'Active') {
			frm.add_custom_button(__('Create Next Year Saving'), function() {
				frappe.call({
					method: 'webshop.webshop.api.cooperative_payment.create_next_year_saving',
					args: { member_name: frm.doc.name },
					freeze: true,
					freeze_message: __('Creating Mandatory Saving records...'),
					callback: function(r) {
						if (r.message) {
							frappe.msgprint({
								title: __('Mandatory Saving Created'),
								message: __('Next year record: {0}', [r.message.next_year]),
								indicator: 'green'
							});
							frm.reload_doc();
						}
					}
				});
			}, __('Actions'));
		}
	}
});

function create_payment_request(frm) {
	frappe.model.open_mapped_doc({
		method: "webshop.webshop.doctype.cooperative_member.cooperative_member.make_payment_request",
		frm: frm,
		freeze: true,
		freeze_message: __('Creating Payment Request ...')
	});
}
