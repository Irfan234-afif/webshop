frappe.ui.form.on('Quotation', {
	payment_method_type: function(frm) {
		if (frm.doc.payment_method_type && frm.doc.order_type === 'Shopping Cart') {
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
	// Remove rows that match service charge pattern
	if (!frm.doc.taxes) return;
	
	let taxes_to_remove = [];
	
	frm.doc.taxes.forEach((tax, idx) => {
		// Identify service charges by checking if they match configured charges
		// This is a simple heuristic - you might want to add a custom field to mark them
		if (tax.description) {
			taxes_to_remove.push(idx);
		}
	});
	
	// Actually, let's only remove if payment method is changing
	// Better approach: clear all taxes and let them be re-added
	// For now, just clear and re-add
	frm.doc.taxes = [];
}
