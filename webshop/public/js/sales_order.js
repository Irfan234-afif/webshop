frappe.ui.form.on('Sales Order', {
	payment_method_type: function(frm) {
		if (frm.doc.payment_method_type) {
			apply_payment_service_charges(frm);
		}
	}
});

function apply_payment_service_charges(frm) {
	// Clear existing service charges (to avoid duplicates)
	clear_service_charges(frm);
	
	// Fetch payment method charges
	frappe.call({
		method: 'webshop.webshop.doctype.webshop_payment_method.webshop_payment_method.get_payment_method_charges',
		args: {
			payment_method_name: frm.doc.payment_method_type
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				r.message.forEach(charge => {
					let charge_amount = 0;
					let rate = 0;
					
					if (charge.charge_type === 'On Net Total') {
						// Percentage-based charge
						rate = charge.rate;
						charge_amount = (frm.doc.net_total * rate) / 100;
					} else {
						// Fixed amount (Actual)
						charge_amount = charge.tax_amount;
					}
					
					let row = frm.add_child('taxes', {
						charge_type: charge.charge_type,
						account_head: charge.account_head,
						description: charge.description,
						rate: rate,
						tax_amount: charge_amount,
						cost_center: charge.cost_center || frm.doc.cost_center
					});
				});
				
				frm.refresh_field('taxes');
				frm.trigger('calculate_taxes_and_totals');
			}
		}
	});
}

function clear_service_charges(frm) {
	// Clear all existing taxes before adding service charges
	// This is a simple approach - in production you might want to only clear service charges
	if (!frm.doc.taxes) return;
	
	frm.doc.taxes = [];
}
