// Item List View Settings - Bulk Actions
frappe.listview_settings['Item'] = {
	add_fields: ["item_name", "stock_uom", "item_group", "image", "has_variants", "end_of_life", "disabled"],
	filters: [["disabled", "=", "0"]],
	onload: function(listview) {
		// Add custom bulk action for publishing items to website
		listview.page.add_action_item(__('Publish in Website'), function() {
			let selected_items = listview.get_checked_items();
			
			if (selected_items.length === 0) {
				frappe.msgprint(__('Please select at least one item'));
				return;
			}

			// Confirm before publishing
			frappe.confirm(
				__('Are you sure you want to publish {0} item(s) to the website?', [selected_items.length]),
				function() {
					// Process bulk publish
					frappe.call({
						method: 'webshop.webshop.doctype.override_doctype.item.bulk_publish_items',
						args: {
							items: selected_items.map(item => item.name)
						},
						freeze: true,
						freeze_message: __('Publishing {0} items...', [selected_items.length]),
						callback: function(r) {
							if (r.message) {
								let msg = '';
								if (r.message.success > 0) {
									msg += __('Successfully published {0} item(s).', [r.message.success]) + '<br>';
								}
								if (r.message.skipped > 0) {
									msg += __('Skipped {0} item(s) (already published).', [r.message.skipped]) + '<br>';
								}
								if (r.message.failed > 0) {
									msg += __('Failed to publish {0} item(s).', [r.message.failed]);
								}

								frappe.msgprint({
									message: msg,
									title: __('Bulk Publish Complete'),
									indicator: r.message.failed > 0 ? 'orange' : 'green'
								});

								// Refresh list view
								listview.refresh();
							}
						}
					});
				}
			);
		});
	},

	get_indicator: function (doc) {
		if (doc.disabled) {
			return [__("Disabled"), "grey", "disabled,=,Yes"];
		} else if (doc.end_of_life && doc.end_of_life < frappe.datetime.get_today()) {
			return [__("Expired"), "grey", "end_of_life,<,Today"];
		} else if (doc.has_variants) {
			return [__("Template"), "orange", "has_variants,=,Yes"];
		} else if (doc.variant_of) {
			return [__("Variant"), "green", "variant_of,=," + doc.variant_of];
		}
	},

	reports: [
		{
			name: "Stock Summary",
			route: "/app/stock-balance",
		},
		{
			name: "Stock Ledger",
			report_type: "Script Report",
		},
		{
			name: "Stock Balance",
			report_type: "Script Report",
		},
		{
			name: "Stock Projected Qty",
			report_type: "Script Report",
		},
	],
};
