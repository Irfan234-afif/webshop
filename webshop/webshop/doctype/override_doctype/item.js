frappe.ui.form.on("Item", {
    refresh: function (frm) {
        frm.add_custom_button(
            __("Generate Variant Prices"),
            function () {
                erpnext.item.show_generate_variant_prices_dialog(frm);
            },
            __("Actions")
        );
    }
})

$.extend(erpnext.item, {
    show_generate_variant_prices_dialog: function (frm) {
        // First, get all variants to show count
        frappe.call({
            method: "webshop.webshop.doctype.override_doctype.item.get_item_variants",
            args: {
                item_code: frm.doc.name,
            },
            callback: function (r) {
                if (!r.message || r.message.length === 0) {
                    frappe.msgprint({
                        message: __("No variants found for this item template."),
                        indicator: "orange",
                        title: __("No Variants"),
                    });
                    return;
                }

                let variant_count = r.message.length;
                let dialog = new frappe.ui.Dialog({
                    title: __("Generate Prices for Variants"),
                    fields: [
                        {
                            fieldtype: "HTML",
                            fieldname: "info",
                            options: `<div class="alert alert-info">
								${__("This will create Item Price records for all {0} variants of this template.", [variant_count])}
							</div>`,
                        },
                        {
                            fieldtype: "Section Break",
                            label: __("Price List Details"),
                        },
                        {
                            fieldname: "price_list",
                            fieldtype: "Link",
                            options: "Price List",
                            label: __("Price List"),
                            reqd: 1,
                            get_query: function () {
                                return {
                                    filters: {
                                        enabled: 1,
                                    },
                                };
                            },
                        },
                        {
                            fieldname: "currency",
                            fieldtype: "Data",
                            label: __("Currency"),
                            read_only: 1,
                            depends_on: "eval:doc.price_list",
                        },
                        {
                            fieldtype: "Column Break",
                        },
                        {
                            fieldname: "base_price",
                            fieldtype: "Currency",
                            label: __("Base Price"),
                            reqd: 1,
                            description: __("This price will be applied to all variants. You can modify prices individually after creation."),
                        },
                        {
                            fieldtype: "Section Break",
                        },
                        {
                            fieldname: "uom",
                            fieldtype: "Link",
                            options: "UOM",
                            label: __("Unit of Measure"),
                            reqd: 1,
                            default: frm.doc.stock_uom || "",
                            description: __("Unit of measure for the price"),
                        },
                        {
                            fieldtype: "Column Break",
                        },
                        {
                            fieldname: "valid_from",
                            fieldtype: "Date",
                            label: __("Valid From"),
                            default: frappe.datetime.get_today(),
                        },
                        {
                            fieldname: "valid_upto",
                            fieldtype: "Date",
                            label: __("Valid Upto"),
                        },
                        {
                            fieldtype: "Section Break",
                        },
                        {
                            fieldname: "overwrite_existing",
                            fieldtype: "Check",
                            label: __("Overwrite Existing Prices"),
                            description: __("If checked, existing prices for the same price list will be updated. Otherwise, existing prices will be skipped."),
                            default: 0,
                        },
                    ],
                    primary_action_label: __("Generate Prices"),
                    primary_action: function (values) {
                        if (!values) return;

                        dialog.hide();
                        frappe.call({
                            method: "webshop.webshop.doctype.override_doctype.item.generate_variant_prices",
                            args: {
                                template_item: frm.doc.name,
                                price_list: values.price_list,
                                base_price: values.base_price,
                                uom: values.uom,
                                valid_from: values.valid_from,
                                valid_upto: values.valid_upto,
                                overwrite_existing: values.overwrite_existing || 0,
                            },
                            freeze: true,
                            freeze_message: __("Generating prices for variants..."),
                            callback: function (r) {
                                if (r.message) {
                                    frappe.show_alert({
                                        message: __("Successfully created {0} price records.", [r.message.created]),
                                        indicator: "green",
                                    });
                                    if (r.message.skipped > 0) {
                                        frappe.show_alert({
                                            message: __("{0} prices were skipped (already exist).", [r.message.skipped]),
                                            indicator: "orange",
                                        });
                                    }
                                    if (r.message.failed > 0) {
                                        frappe.show_alert({
                                            message: __("{0} prices failed to create.", [r.message.failed]),
                                            indicator: "red",
                                        });
                                    }
                                    // Refresh the form
                                    frm.reload_doc();
                                }
                            },
                        });
                    },
                });

                // Update currency when price list changes
                dialog.fields_dict.price_list.$input.on("change", function () {
                    let price_list = dialog.get_value("price_list");
                    if (price_list) {
                        frappe.db.get_value("Price List", price_list, "currency", (r) => {
                            if (r && r.currency) {
                                dialog.set_value("currency", r.currency);
                            }
                        });
                    } else {
                        dialog.set_value("currency", "");
                    }
                });

                dialog.show();
            },
        });
    },
});