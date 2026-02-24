// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Voluntary Saving', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.status === 'Pending Payment' && frm.doc.transaction_type === 'Deposit') {
			if (frm.doc.payment_request) {
				frm.add_custom_button(__('View Payment Request'), function() {
					frappe.set_route('Form', 'Payment Request', frm.doc.payment_request);
				}, __('Actions'));
			} else {
				frm.add_custom_button(__('Make Payment'), function() {
					show_payment_dialog(frm);
				}, __('Actions'));
			}
		}
	}
});

function show_payment_dialog(frm) {
	let dialog = new frappe.ui.Dialog({
		title: __('Create Payment Request'),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'help_html',
				options: `<p class="text-muted">${__('Select payment method for this deposit:')}</p>`
			},
			{
				label: 'Amount',
				fieldname: 'amount',
				fieldtype: 'Currency',
				default: frm.doc.amount,
				read_only: 1
			},
			{
				label: 'Payment Method',
				fieldname: 'payment_method_type',
				fieldtype: 'Link',
				options: 'Webshop Payment Method',
				reqd: 1
			}
		],
		primary_action_label: __('Create'),
		primary_action: function(values) {
			frappe.call({
				method: 'webshop.webshop.doctype.voluntary_saving.voluntary_saving.make_payment_request',
				args: {
					doc_name: frm.doc.name,
					payment_method_type: values.payment_method_type
				},
				freeze: true,
				freeze_message: __('Creating Payment Request ...'),
				callback: function(r) {
					if (!r.exc && r.message) {
						dialog.hide();
						frappe.show_alert({
							message: __('Payment Request {0} created', [r.message]),
							indicator: 'green'
						});
						frm.reload_doc();
						frappe.set_route('Form', 'Payment Request', r.message);
					}
				}
			});
		}
	});

	dialog.show();
}
