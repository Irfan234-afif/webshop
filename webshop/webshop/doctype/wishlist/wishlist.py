# -*- coding: utf-8 -*-
# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from webshop.webshop.doctype.webshop_settings.webshop_settings import (
    get_shopping_cart_settings,
)
from webshop.webshop.shopping_cart.cart import _set_price_list, get_party
from erpnext.utilities.product import get_price
from erpnext.stock.doctype.warehouse.warehouse import get_child_warehouses


class Wishlist(Document):
	pass


@frappe.whitelist()
def add_to_wishlist(item_code):
	"""Insert Item into wishlist."""
	if frappe.db.exists("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user}):
		return get_wishlist_items()

	web_item_data = frappe.db.get_value(
		"Website Item",
		{"item_code": item_code},
		[
			"website_image",
			"website_warehouse",
			"name",
			"web_item_name",
			"item_name",
			"item_group",
			"route",
		],
		as_dict=1,
	)

	wished_item_dict = {
		"item_code": item_code,
		"item_name": web_item_data.get("item_name"),
		"item_group": web_item_data.get("item_group"),
		"website_item": web_item_data.get("name"),
		"web_item_name": web_item_data.get("web_item_name"),
		"image": web_item_data.get("website_image"),
		"warehouse": web_item_data.get("website_warehouse"),
		"route": web_item_data.get("route"),
	}

	if not frappe.db.exists("Wishlist", frappe.session.user):
		# initialise wishlist
		wishlist = frappe.get_doc({"doctype": "Wishlist"})
		wishlist.user = frappe.session.user
		wishlist.append("items", wished_item_dict)
		wishlist.save(ignore_permissions=True)
	else:
		wishlist = frappe.get_doc("Wishlist", frappe.session.user)
		item = wishlist.append("items", wished_item_dict)
		item.db_insert()

	if hasattr(frappe.local, "cookie_manager"):
		frappe.local.cookie_manager.set_cookie("wish_count", str(len(wishlist.items)))

	return get_wishlist_items()


@frappe.whitelist()
def remove_from_wishlist(item_code):
	if frappe.db.exists("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user}):
		frappe.db.delete("Wishlist Item", {"item_code": item_code, "parent": frappe.session.user})
		frappe.db.commit()  # nosemgrep

		wishlist_items = frappe.db.get_values("Wishlist Item", filters={"parent": frappe.session.user})

		if hasattr(frappe.local, "cookie_manager"):
			frappe.local.cookie_manager.set_cookie("wish_count", str(len(wishlist_items)))

	return get_wishlist_items()


def get_stock_availability(item_code, warehouse):
	if warehouse and frappe.get_cached_value("Warehouse", warehouse, "is_group") == 1:
		warehouses = get_child_warehouses(warehouse)
	else:
		warehouses = [warehouse] if warehouse else []

	stock_qty = 0.0
	for warehouse in warehouses:
		stock_qty += frappe.utils.flt(
			frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
		)

	return bool(stock_qty)


@frappe.whitelist()
def get_wishlist_items():
	if not frappe.session.user or frappe.session.user == "Guest":
		return []

	if not frappe.db.exists("Wishlist", frappe.session.user):
		return []

	items = frappe.db.get_all(
		"Wishlist Item",
		filters={"parent": frappe.session.user},
		fields=[
			"web_item_name",
			"item_code",
			"item_name",
			"website_item",
			"warehouse",
			"image",
			"item_group",
			"route",
		],
	)

	# Fetch settings and price list
	settings = get_shopping_cart_settings()
	selling_price_list = _set_price_list(settings)

	# Enrich items with price and stock details
	for item in items:
		if settings.show_stock_availability:
			item.available = get_stock_availability(
				item.item_code, item.get("warehouse")
			)

		party = get_party()

		price_details = get_price(
			item.item_code,
			selling_price_list,
			settings.default_customer_group,
			settings.company,
			party=party,
		)

		if price_details:
			item.price = price_details.get("price_list_rate")
			item.formatted_price = price_details.get("formatted_price")
			item.formatted_mrp = price_details.get("formatted_mrp")
			if item.formatted_mrp:
				item.discount = price_details.get("discount_percent")

	return items
