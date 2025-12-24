// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payment Request', {
	refresh: function(frm) {
		// Only show approval buttons for webshop manual payment requests
		if (is_webshop_manual_payment(frm)) {
			add_approval_buttons(frm);
		}
	}
});

function is_webshop_manual_payment(frm) {
	// Check if this is a webshop manual payment that needs approval
	return (
		frm.doc.reference_doctype === "Sales Order" &&
		frm.doc.docstatus === 0 &&  // Draft status (pending approval)
		frm.doc.payment_request_type === "Inward"
	);
}

function add_approval_buttons(frm) {
	// Add Approve button
	frm.add_custom_button(__('Approve Payment'), function() {
		approve_payment(frm);
	}, __("Actions"));

	// Add Reject button
	frm.add_custom_button(__('Reject Payment'), function() {
		reject_payment(frm);
	}, __("Actions"));

	// Change button color
	frm.page.set_inner_btn_group_as_primary(__('Actions'));
}

function approve_payment(frm) {
	// Confirm approval
	frappe.confirm(
		__('Are you sure you want to approve this payment? This will mark the payment as paid.'),
		function() {
			// Submit the Payment Request (docstatus = 1)
			frm.savesubmit(function() {
				frappe.show_alert({
					message: __('Payment approved successfully'),
					indicator: 'green'
				}, 5);
			});
		}
	);
}

function reject_payment(frm) {
	// Prompt for rejection reason
	frappe.prompt([
		{
			fieldname: 'rejection_reason',
			label: __('Rejection Reason'),
			fieldtype: 'Text',
			reqd: 1
		}
	],
	function(values) {
		// Add rejection reason to remarks
		let current_remarks = frm.doc.remarks || '';
		let rejection_note = '\n\nRejection Reason: ' + values.rejection_reason;

		frm.set_value('remarks', current_remarks + rejection_note);

		// Save first, then cancel
		frm.save().then(() => {
			// Cancel the Payment Request (docstatus = 2)
			frappe.call({
				method: 'frappe.client.cancel',
				args: {
					doctype: 'Payment Request',
					name: frm.doc.name
				},
				callback: function(r) {
					if (!r.exc) {
						frm.reload_doc();
						frappe.show_alert({
							message: __('Payment rejected successfully'),
							indicator: 'red'
						}, 5);
					}
				}
			});
		});
	},
	__('Reject Payment'),
	__('Confirm')
	);
}
