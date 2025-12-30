import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
	custom_fields = {
		"Item": [
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
			}
		],
		"Website Item": [
			{
				"fieldname": "subscription_config_section",
				"fieldtype": "Section Break",
				"label": "Subscription Config",
				"insert_after": "brand"
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
			}
		],
		"Sales Order Item": [
			{
				"fieldname": "service_period_section",
				"fieldtype": "Section Break",
				"label": "Service Period",
				"insert_after": "description"
			},
			{
				"fieldname": "service_start_date",
				"fieldtype": "Date",
				"label": "Service Start Date",
				"insert_after": "service_period_section"
			},
			{
				"fieldname": "service_end_date",
				"fieldtype": "Date",
				"label": "Service End Date",
				"insert_after": "service_start_date"
			},
			{
				"fieldname": "is_subscription_item",
				"fieldtype": "Check",
				"label": "Is Subscription Item",
				"read_only": 1,
				"insert_after": "service_end_date",
				"fetch_from": "item_code.is_subscription_item"
			},
             {
				"fieldname": "subscription_plan",
				"fieldtype": "Link",
				"options": "Subscription Plan",
				"label": "Subscription Plan",
				"read_only": 1,
				"insert_after": "is_subscription_item",
                "fetch_from": "item_code.subscription_plan"
			}
		],
		"Quotation Item": [
			{
				"fieldname": "service_period_section",
				"fieldtype": "Section Break",
				"label": "Service Period",
				"insert_after": "description"
			},
			{
				"fieldname": "service_start_date",
				"fieldtype": "Date",
				"label": "Service Start Date",
				"insert_after": "service_period_section"
			},
			{
				"fieldname": "service_end_date",
				"fieldtype": "Date",
				"label": "Service End Date",
				"insert_after": "service_start_date"
			},
			{
				"fieldname": "is_subscription_item",
				"fieldtype": "Check",
				"label": "Is Subscription Item",
				"read_only": 1,
				"insert_after": "service_end_date",
				"fetch_from": "item_code.is_subscription_item"
			},
             {
				"fieldname": "subscription_plan",
				"fieldtype": "Link",
				"options": "Subscription Plan",
				"label": "Subscription Plan",
				"read_only": 1,
				"insert_after": "is_subscription_item",
                "fetch_from": "item_code.subscription_plan"
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
		]
	}

	create_custom_fields(custom_fields, update=True)
