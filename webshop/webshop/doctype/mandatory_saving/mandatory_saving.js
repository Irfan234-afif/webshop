// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Mandatory Saving', {
	refresh: function(frm) {
		if (frm.doc.docstatus === 1) {
			// Check if there are unpaid months
			let has_unpaid = frm.doc.monthly_details.some(d => d.status === "Unpaid");
			
			if (has_unpaid) {
				frm.add_custom_button(__('Make Payment'), function() {
					show_payment_dialog(frm);
				}, __('Actions'));
			}
		}
	}
});

function show_payment_dialog(frm) {
	let unpaid_months = frm.doc.monthly_details.filter(d => d.status === "Unpaid");
	
	let dialog_fields = [
		{
			fieldtype: 'HTML',
			fieldname: 'help_html',
			options: `<p class="text-muted">${__('Select unpaid months to create a Payment Request:')}</p>`
		}
	];
	
	unpaid_months.forEach(d => {
		dialog_fields.push({
			fieldtype: 'Check',
			fieldname: d.name,
			label: `${d.month_name} - ${format_currency(d.amount, frm.doc.currency || 'IDR')}`
		});
	});

	dialog_fields.push(
		{ fieldtype: 'Section Break' },
		{
			label: 'Payment Method',
			fieldname: 'payment_method_type',
			fieldtype: 'Link',
			options: 'Webshop Payment Method',
			reqd: 1
		}
	);

	let dialog = new frappe.ui.Dialog({
		title: __('Create Payment Request'),
		fields: dialog_fields,
		primary_action_label: __('Create'),
		primary_action: function(values) {
			let selected_months = [];
			unpaid_months.forEach(d => {
				if (values[d.name]) {
					selected_months.push(d.month);
				}
			});
			    
			if (selected_months.length === 0) {
			    frappe.msgprint(__('Please select at least one month'));
			    return;
			}
			
			frappe.call({
				method: 'webshop.webshop.doctype.mandatory_saving.mandatory_saving.make_payment_request',
				args: {
					doc_name: frm.doc.name,
					months: selected_months,
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
