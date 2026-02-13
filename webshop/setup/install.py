import click
import frappe

from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from webshop.webshop.utils.setup import has_ecommerce_fields

def after_install():
	run_patches()
	copy_from_ecommerce_settings()
	drop_ecommerce_settings()
	remove_ecommerce_settings_doctype()
	add_custom_fields()
	navbar_add_products_link()
	say_thanks()


def copy_from_ecommerce_settings():
	if not has_ecommerce_fields():
		return

	frappe.reload_doc("webshop", "doctype", "webshop_settings")

	qb = frappe.qb
	table = frappe.qb.Table("tabSingles")
	old_doctype = "E Commerce Settings"
	new_doctype = "Webshop Settings"

	entries = (
		qb.from_(table)
		.select(table.field, table.value)
		.where((table.doctype == old_doctype) & (table.field != "name"))
		.run(as_dict=True)
	)

	for e in entries:
		qb.into(table).insert(new_doctype, e.field, e.value).run()

	for doctype in ["Website Filter Field", "Website Attribute"]:
		table = qb.DocType(doctype)
		query = (
			qb.update(table)
			.set(table.parent, new_doctype)
			.set(table.parenttype, new_doctype)
			.where(table.parent == old_doctype)
		)

		query.run()

def drop_ecommerce_settings():
	frappe.delete_doc_if_exists("DocType", "E Commerce Settings", force=True)


def remove_ecommerce_settings_doctype():
	if not has_ecommerce_fields():
		return

	table = frappe.qb.Table("tabSingles")
	old_doctype = "E Commerce Settings"

	frappe.qb.from_(table).delete().where(table.doctype == old_doctype).run()


def add_custom_fields():
	custom_fields = {
		"Quotation": [
			{
				"fieldname": "school_section",
				"fieldtype": "Section Break",
				"label": "School Information",
				"insert_after": "party_name",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"collapsible": 1
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "school_section",
				"read_only": 1,
				"depends_on": "eval:doc.order_type=='Shopping Cart'"
			},
			{
				"fieldname": "delivery_date",
				"fieldtype": "Date",
				"label": "Delivery Date",
				"insert_after": "transaction_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'"
			},
			{
				"fieldname": "delivery_time",
				"fieldtype": "Time",
				"label": "Delivery Time",
				"insert_after": "delivery_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'"
			},
			{
				"fieldname": "checkout_section",
				"fieldtype": "Section Break",
				"label": "Checkout Information",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"collapsible": 1
			},
			{
				"fieldname": "pickup_type",
				"fieldtype": "Select",
				"label": "Jenis Pengambilan",
				"options": "\nAmbil di koperasi\nAmbil secara online",
				"insert_after": "checkout_section",
				"depends_on": "eval:doc.order_type=='Shopping Cart'"
			},
			{
				"fieldname": "column_break_checkout",
				"fieldtype": "Column Break",
				"insert_after": "pickup_type"
			},
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Metode Pembayaran",
				"options": "Webshop Payment Method",
				"insert_after": "column_break_checkout",
				"depends_on": "eval:doc.order_type=='Shopping Cart'"
			},
			{
				"fieldname": "school_unit",
				"fieldtype": "Link",
				"label": "School Unit",
				"options": "School Unit",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"fetch_from": "student.school_unit",
    			"read_only": 1
			},
			{
				"fieldname": "return_request",
				"label": "Return Request",
				"fieldtype": "Link",
				"options": "Return Request",
				"insert_after": "is_return",
				"read_only": 1,
				"print_hide": 1
			},
			{
				"fieldname": "return_request",
				"label": "Return Request",
				"fieldtype": "Link",
				"options": "Return Request",
				"insert_after": "is_return",
				"read_only": 1,
				"print_hide": 1
			},
			{
				"fieldname": "payment_channel",
				"fieldtype": "Data",
				"label": "Payment Channel",
				"insert_after": "payment_method_type",
				"no_copy": 1
			}
		],
		"Sales Order": [
			{
				"fieldname": "school_section",
				"fieldtype": "Section Break",
				"label": "School Information",
				"insert_after": "customer",
				"collapsible": 1
			},
			{
				"fieldname": "student",
				"fieldtype": "Link",
				"label": "Student",
				"options": "Student",
				"insert_after": "school_section",
				"read_only": 1
			},
			{
				"fieldname": "delivery_time",
				"fieldtype": "Time",
				"label": "Delivery Time",
				"insert_after": "delivery_date",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"read_only": 1
			},
			{
				"fieldname": "checkout_section",
				"fieldtype": "Section Break",
				"label": "Checkout Information",
				"insert_after": "student",
				"collapsible": 1
			},
			{
				"fieldname": "pickup_type",
				"fieldtype": "Select",
				"label": "Jenis Pengambilan",
				"options": "\nAmbil di koperasi\nAmbil secara online",
				"insert_after": "checkout_section",
				"read_only": 1
			},
			{
				"fieldname": "column_break_checkout",
				"fieldtype": "Column Break",
				"insert_after": "pickup_type"
			},
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Metode Pembayaran",
				"options": "Webshop Payment Method",
				"insert_after": "column_break_checkout",
			},
			{
				"fieldname": "school_unit",
				"fieldtype": "Link",
				"label": "School Unit",
				"options": "School Unit",
				"insert_after": "student",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
    			"fetch_from": "student.school_unit",
    			"read_only": 1
			},
			{
				"fieldname": "ecommerce_delivery_section",
				"fieldtype": "Section Break",
				"label": "E-commerce Delivery Status",
				"insert_after": "status",
				"collapsible": 1
			},
			{
				"fieldname": "ecommerce_delivery_status",
				"fieldtype": "Select",
				"label": "E-commerce Delivery Status",
				"options": "\nPending\nProcessing\nShipped\nDelivered\nCompleted",
				"default": "Pending",
				"depends_on": "eval:doc.order_type=='Shopping Cart'",
				"allow_on_submit": 1,
				"insert_after": "ecommerce_delivery_section",
				"description": "Customer-facing delivery status for e-commerce orders"
			},
			{
				"fieldname": "column_break_ecommerce_delivery",
				"fieldtype": "Column Break",
				"insert_after": "ecommerce_delivery_status"
			},
			{
				"fieldname": "shipped_date",
				"fieldtype": "Datetime",
				"label": "Shipped Date",
				"insert_after": "column_break_ecommerce_delivery",
				"read_only": 1,
				"description": "Timestamp when order was marked as Shipped"
			},
			{
				"fieldname": "delivered_date",
				"fieldtype": "Datetime",
				"label": "Delivered Date",
				"insert_after": "shipped_date",
				"read_only": 1,
				"description": "Timestamp when customer confirmed delivery"
			},
			{
				"fieldname": "payment_channel",
				"fieldtype": "Data",
				"label": "Payment Channel",
				"insert_after": "payment_method_type",
				"read_only": 1,
				"no_copy": 1
			}
		],
		"Item": [
			{
				"default": 0,
				"depends_on": "published_in_website",
				"fieldname": "published_in_website",
				"fieldtype": "Check",
				"ignore_user_permissions": 1,
				"insert_after": "default_manufacturer_part_no",
				"label": "Published In Website",
				"read_only": 1,
				"no_copy": 1,
			},
			{
				"fieldname": "subscription_config_section",
				"fieldtype": "Section Break",
				"label": "Subscription Config",
				"insert_after": "image"
			},
			{
				"fieldname": "is_subscription_item",
				"fieldtype": "Check",
				"label": "Is Subscription Item",
				"insert_after": "subscription_config_section"
			},
			{
				"fieldname": "subscription_plan",
				"fieldtype": "Link",
				"options": "Subscription Plan",
				"label": "Subscription Plan",
				"depends_on": "is_subscription_item",
				"insert_after": "is_subscription_item"
			},
			{
                "fieldname": "grade",
                "fieldtype": "Link",
                "label": "Kelas/Grade",
                "description": "Grade level for this item",
                "options": "Grade",
                "insert_after": "school_unit"
            },
			{
                "fieldname": "school_unit",
                "fieldtype": "Link",
                "label": "School Unit",
                "description": "For grouping the categories",
                "options": "School Unit",
                "insert_after": "item_group"
            }
		],
		"Item Group": [
			{
				"fieldname": "custom_website_settings",
				"fieldtype": "Section Break",
				"label": "Website Settings",
				"insert_after": "taxes",
			},
			{
				"default": "0",
				"description": "Make Item Group visible in website",
				"fieldname": "show_in_website",
				"fieldtype": "Check",
				"label": "Show in Website",
				"insert_after": "custom_website_settings",
			},
			{
				"depends_on": "show_in_website",
				"fieldname": "route",
				"fieldtype": "Data",
				"label": "Route",
				"no_copy": 1,
				"unique": 1,
				"insert_after": "show_in_website",
			},
			{
				"depends_on": "show_in_website",
				"fieldname": "website_title",
				"fieldtype": "Data",
				"label": "Title",
				"insert_after": "route",
			},
			{
				"depends_on": "show_in_website",
				"description": "HTML / Banner that will show on the top of product list.",
				"fieldname": "description",
				"fieldtype": "Text Editor",
				"label": "Description",
				"insert_after": "website_title",
			},
			{
				"default": "0",
				"depends_on": "show_in_website",
				"description": "Include Website Items belonging to child Item Groups",
				"fieldname": "include_descendants",
				"fieldtype": "Check",
				"label": "Include Descendants",
				"insert_after": "website_title",
			},
			{
				"fieldname": "column_break_16",
				"fieldtype": "Column Break",
				"insert_after": "include_descendants",
			},
			{
				"depends_on": "show_in_website",
				"fieldname": "weightage",
				"fieldtype": "Int",
				"label": "Weightage",
				"insert_after": "column_break_16",
			},
			{
				"depends_on": "show_in_website",
				"description": "Show this slideshow at the top of the page",
				"fieldname": "slideshow",
				"fieldtype": "Link",
				"label": "Slideshow",
				"options": "Website Slideshow",
				"insert_after": "weightage",
			},
			{
				"depends_on": "show_in_website",
				"fieldname": "website_specifications",
				"fieldtype": "Table",
				"label": "Website Specifications",
				"options": "Item Website Specification",
				"insert_after": "description",
			},
			{
				"collapsible": 1,
				"depends_on": "show_in_website",
				"fieldname": "website_filters_section",
				"fieldtype": "Section Break",
				"label": "Website Filters",
				"insert_after": "website_specifications",
			},
			{
				"fieldname": "filter_fields",
				"fieldtype": "Table",
				"label": "Item Fields",
				"options": "Website Filter Field",
				"insert_after": "website_filters_section",
			},
			{
				"fieldname": "filter_attributes",
				"fieldtype": "Table",
				"label": "Attributes",
				"options": "Website Attribute",
				"insert_after": "filter_fields",
			},
		],
		"Payment Request": [
			{
				"fieldname": "payment_method_type",
				"fieldtype": "Link",
				"label": "Payment Method Type",
				"options": "Webshop Payment Method",
				"insert_after": "mode_of_payment",
				"read_only": 1,
				"description": "Webshop payment method selected by customer",
			},
			{
				"fieldname": "payment_due_date",
				"label": "Payment Due Date",
				"fieldtype": "Datetime",
				"insert_after": "transaction_date",
				"no_copy": 1,
				"print_hide": 1
			},
			{
				"fieldname": "webshop_approval_section",
				"fieldtype": "Section Break",
				"label": "Webshop Approval Details",
				"insert_after": "payment_url",
				"collapsible": 1
			},
			{
				"fieldname": "payment_proof",
				"fieldtype": "Attach",
				"label": "Payment Proof",
				"insert_after": "webshop_approval_section",
				"description": "Upload proof of payment (bank transfer receipt, etc.)"
			},
			{
				"fieldname": "column_break_webshop",
				"fieldtype": "Column Break",
				"insert_after": "payment_proof"
			},
			{
				"fieldname": "remarks",
				"fieldtype": "Text",
				"label": "Remarks",
				"insert_after": "column_break_webshop",
				"description": "Admin notes or rejection reasons"
			},
			{
				"fieldname": "approval_metadata_section",
				"fieldtype": "Section Break",
				"label": "Approval Metadata",
				"insert_after": "remarks",
				"collapsible": 1,
				"depends_on": "eval:doc.docstatus > 0"
			},
			{
				"fieldname": "admin_approval_by",
				"fieldtype": "Link",
				"label": "Approved/Rejected By",
				"options": "User",
				"insert_after": "approval_metadata_section",
				"read_only": 1
			},
			{
				"fieldname": "admin_approval_time",
				"fieldtype": "Datetime",
				"label": "Approval/Rejection Time",
				"insert_after": "admin_approval_by",
				"read_only": 1
			},
			{
				"fieldname": "payment_channel_code",
				"fieldtype": "Data",
				"label": "Payment Channel Code",
				"read_only": 1,
				"insert_after": "payment_channel"
			},
			{
				"fieldname": "virtual_account_number",
				"fieldtype": "Data",
				"label": "Virtual Account Number",
				"read_only": 1,
				"insert_after": "payment_channel_code"
			},
			{
				"fieldname": "virtual_account_bank",
				"fieldtype": "Data",
				"label": "Virtual Account Bank",
				"read_only": 1,
				"insert_after": "virtual_account_number"
			}
		],
		"Subscription": [
			{
				"fieldname": "sales_order_ref",
				"fieldtype": "Link",
				"options": "Sales Order",
				"label": "Source Sales Order",
				"read_only": 1,
				"insert_after": "party"
			}
		],
		"Subscription Plan": [
			{
				"fieldname": "billing_timing",
				"fieldtype": "Select",
				"label": "Billing Timing",
				"options": "Pre-Paid\nPost-Paid",
				"default": "Pre-Paid",
				"insert_after": "billing_interval_count",
				"description": "Pre-Paid: Subscription starts AFTER initial period. Post-Paid: Subscription starts IMMEDIATELY.",
				"reqd": 1
			},
			{
				"fieldname": "use_fixed_period",
				"label": "Use Fixed Period",
				"fieldtype": "Check",
				"insert_after": "billing_interval_count",
				"description": "If checked, subscription will use the Subscription End Date as invoice end date instead of calculating from billing interval. Useful for one-time fixed period subscriptions (e.g., catering service for specific date range).",
				"default": 0
			}
		],
		"Delivery Note": [
			{
				"fieldname": "image",
				"label": "Image",
				"fieldtype": "Attach Image",
				"insert_after": "driver_name",
				"print_hide": 1
			}
		]
	}

	frappe.make_property_setter(
		{
			"doctype": "Item Group",
			"doctype_or_field": "DocType",
			"fieldname": "allow_guest_to_view",
			"property": "allow_guest_to_view",
			"value": 1,
			"property_type": "Check"
		},
		is_system_generated=True,
	)

	return create_custom_fields(custom_fields)

def navbar_add_products_link():
	website_settings = frappe.get_doc("Website Settings")
	if website_settings.top_bar_items:
		return

	website_settings.append(
		"top_bar_items",
		{
			"label": _("Products"),
			"url": "/all-products",
			"right": False,
		},
	)

	website_settings.save()


def say_thanks():
	click.secho("Thank you for installing Frappe Webshop!", color="green")


patches = [
	"create_website_items",
	"populate_e_commerce_settings",
	"add_homepage_field",
	"make_homepage_products_website_items",
	"fetch_thumbnail_in_website_items",
	"convert_to_website_item_in_item_card_group_template",
	"shopping_cart_to_ecommerce",
	"copy_custom_field_filters_to_website_item",
]

def run_patches():
	# Customers migrating from v13 to v15 directly need to run all below patches

	frappe.flags.in_patch = True

	try:
		for patch in patches:
			frappe.get_attr(f"webshop.patches.{patch}.execute")()

	finally:
		frappe.flags.in_patch = False


