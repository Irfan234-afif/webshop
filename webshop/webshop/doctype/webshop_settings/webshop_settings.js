// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Webshop Settings", {
	setup: function (frm) {
		frm.set_query("default_warehouse", function (doc) {
			return {
				filters: {
					is_group: 0,
					company: doc.company,
				},
			};
		});
	},
	onload: function(frm) {
		if(frm.doc.__onload && frm.doc.__onload.quotation_series) {
			frm.fields_dict.quotation_series.df.options = frm.doc.__onload.quotation_series;
			frm.refresh_field("quotation_series");
		}

		// Store the initial warehouse value for comparison
		if (!frm.doc.__onload) {
			frm.doc.__onload = {};
		}
		frm.doc.__onload.default_warehouse = frm.doc.default_warehouse;

		frm.set_query('payment_gateway_account', function() {
			return { 'filters': { 
				'payment_channel': ['in', ["Email", "Phone"]] 
			 } };
		});
	},
	refresh: function(frm) {
		if (frm.doc.enabled) {
			frm.get_field('store_page_docs').$wrapper.removeClass('hide-control').html(
				`<div>${__("Follow these steps to create a landing page for your store")}:
					<a href="https://docs.erpnext.com/docs/user/manual/en/website/store-landing-page"
						style="color: var(--gray-600)">
						docs/store-landing-page
					</a>
				</div>`
			);
		}

		frappe.model.with_doctype("Website Item", () => {
			const web_item_meta = frappe.get_meta('Website Item');

			const valid_fields = web_item_meta.fields.filter(df =>
				["Link", "Table MultiSelect"].includes(df.fieldtype) && !df.hidden
			).map(df =>
				({ label: df.label, value: df.fieldname })
			);

			frm.get_field("filter_fields").grid.update_docfield_property(
				'fieldname', 'options', valid_fields
			);
		});
	},
	enabled: function(frm) {
		if (frm.doc.enabled === 1) {
			frm.set_value('enable_variants', 1);
		}
		else {
			frm.set_value('company', '');
			frm.set_value('price_list', '');
			frm.set_value('default_customer_group', '');
			frm.set_value('quotation_series', '');
		}
	},
	default_warehouse: function(frm) {
		// Check if warehouse value actually changed from the saved value
		if (!frm.doc.__islocal && frm.doc.default_warehouse && 
			frm.doc.default_warehouse !== frm.doc.__onload?.default_warehouse) {
			
			frappe.confirm(
				__('Do you want to update all Website Items with this warehouse?'),
				function() {
					// User confirmed - trigger background job
					frappe.call({
						method: 'webshop.webshop.doctype.webshop_settings.webshop_settings.update_website_items_warehouse',
						args: {
							warehouse: frm.doc.default_warehouse
						},
						freeze: true,
						freeze_message: __('Queueing background job...'),
						callback: function(r) {
							if (!r.exc) {
								frappe.show_alert({
									message: __('Background job has been queued to update all Website Items'),
									indicator: 'green'
								}, 5);
							}
						}
					});
				},
				function() {
					// User cancelled - do nothing
					frappe.show_alert({
						message: __('Website Items will not be updated'),
						indicator: 'blue'
					}, 3);
				}
			);
		}
	}
});
