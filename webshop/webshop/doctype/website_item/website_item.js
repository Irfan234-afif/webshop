// Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Website Item', {
	onload: (frm) => {
		// should never check Private
		frm.fields_dict["website_image"].df.is_private = 0;
		if (frm.is_new()) {
			frappe.db.get_single_value('Webshop Settings', 'default_warehouse')
			.then(default_warehouse => {
				frm.set_value('website_warehouse', default_warehouse);
			})
		}
	},

	refresh: (frm) => {
		frm.add_custom_button(__("Prices"), function() {
			frappe.set_route("List", "Item Price", {"item_code": frm.doc.item_code});
		}, __("View"));

		frm.add_custom_button(__("Stock"), function() {
			frappe.route_options = {
				"item_code": frm.doc.item_code
			};
			frappe.set_route("query-report", "Stock Balance");
		}, __("View"));

		frm.add_custom_button(__("Webshop Settings"), function() {
			frappe.set_route("Form", "Webshop Settings");
		}, __("View"));

		frm.set_query('for_variant', 'website_item_images', function(doc, cdt, cdn) {
			return {
				filters: {
					variant_of: doc.item_code
				}
			};
		});
	},

	copy_from_item_group: (frm) => {
		return frm.call({
			doc: frm.doc,
			method: "copy_specification_from_item_group"
		});
	},

	set_meta_tags: (frm) => {
		frappe.utils.set_meta_tag(frm.doc.route);
	}
});
