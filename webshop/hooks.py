from . import __version__ as _version

app_name = "webshop"
app_title = "Webshop"
app_publisher = "Frappe Technologies Pvt. Ltd."
app_description = "Open Source eCommerce Platform"
app_email = "contact@frappe.io"
app_icon = "fa fa-shopping-basket"
app_license = "GNU General Public License (v3)"
app_version = _version

add_to_apps_screen = [
	{
		"name": app_name,
		"title": app_title,
		"route": "/desk",
	}
]


required_apps = ["payments", "erpnext"]

web_include_css = "webshop-web.bundle.css"

web_include_js = "web.bundle.js"

after_install = "webshop.setup.install.after_install"
on_logout = "webshop.webshop.shopping_cart.utils.clear_cart_count"
on_session_creation = [
	"webshop.webshop.utils.portal.update_debtors_account",
	"webshop.webshop.shopping_cart.utils.set_cart_count",
	"webshop.webshop.shopping_cart.student_utils.restore_active_student_from_cookie"
]

update_website_context = [
	"webshop.webshop.shopping_cart.utils.update_website_context"
]

# scheduler_events = {
# 	"hourly": [
# 		"webshop.webshop.api.scheduled_tasks.cancel_overdue_orders"
# 	]
# }

website_generators = ["Website Item", "Item Group"]

override_doctype_class = {
    "Payment Request": "webshop.webshop.doctype.override_doctype.payment_request.PaymentRequest",
    "Item Group": "webshop.webshop.doctype.override_doctype.item_group.WebshopItemGroup",
    "Item": "webshop.webshop.doctype.override_doctype.item.WebshopItem",
    "Subscription": "webshop.overrides.subscription_override.CustomSubscription",
}

doctype_js = {
    "Item": "public/js/override/item.js",
    "Homepage": "public/js/override/homepage.js",
    "Payment Request": "webshop/doctype/override_doctype/payment_request.js",
    "Quotation": "public/js/quotation.js",
    "Sales Order": "public/js/sales_order.js",
}

doctype_list_js = {
    "Item": "public/js/override/item_list.js",
}

doc_events = {
    "Item": {
        "on_update": [
            "webshop.webshop.crud_events.item.update_website_item.execute",
            "webshop.webshop.crud_events.item.invalidate_item_variants_cache.execute",
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "after_insert": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "on_trash": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "before_rename": [
            "webshop.webshop.crud_events.item.validate_duplicate_website_item.execute",
        ],
        "after_rename": [
            "webshop.webshop.crud_events.item.invalidate_item_variants_cache.execute",
        ],
    },
    "Website Item": {
        "on_update": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "after_insert": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "on_trash": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
    },
    "Item Price": {
        "on_update": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "after_insert": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
        "on_trash": [
            "webshop.webshop.api.cache_utils.clear_product_cache",
        ],
    },
    "Sales Taxes and Charges Template": {
        "on_update": [
            "webshop.webshop.doctype.webshop_settings.webshop_settings.validate_cart_settings",
        ],
    },
    "Quotation": {
        "validate": [
            "webshop.webshop.crud_events.quotation.validate_shopping_cart_items.execute",
            "webshop.webshop.crud_events.quotation.validate_student_cart.execute",
        ],
    },
    "Sales Order": {
        "validate": [
            "webshop.webshop.api.subscription.validate_subscription_dates"
        ],
        "on_submit": [
            "webshop.webshop.api.subscription.process_subscription_order"
        ]
    },
    "Payment Entry": {
        "on_submit": "webshop.webshop.api.subscription.process_payment_entry"
    },
    "Price List": {
        "validate": [
            "webshop.webshop.crud_events.price_list.check_impact_on_cart.execute"
        ],
    },
    "Delivery Note": {
        "on_submit": "webshop.webshop.doctype.return_request.return_request.update_return_request_on_dn_submit"
    },
    "Sales Invoice": {
        "on_submit": "webshop.webshop.doctype.return_request.return_request.update_return_request_on_si_submit"
    },
    "Tax Rule": {
        "validate": [
            "webshop.webshop.crud_events.tax_rule.validate_use_for_cart.execute",
        ],
    },
}

has_website_permission = {
    "Website Item": "webshop.webshop.doctype.website_item.website_item.has_website_permission_for_website_item",
    "Item Group": "webshop.webshop.doctype.website_item.website_item.has_website_permission_for_item_group"
}

# Fixtures
fixtures = [
    "Grade",
    "School Unit",
    "Item Attribute"
]
