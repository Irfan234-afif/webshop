import frappe
from frappe import _
from frappe.utils import get_link_to_form
from erpnext.stock.doctype.item.item import Item
from webshop.webshop.doctype.override_doctype.item_group import invalidate_cache_for

class DataValidationError(frappe.ValidationError):
	pass

class WebshopItem(Item):
	def on_update(self):
		super(WebshopItem, self).on_update()
		invalidate_cache_for_item(self)
		super(WebshopItem, self).on_update()

	def before_rename(self, old_name, new_name, merge=False):
		self.validate_duplicate_website_item_before_merge(old_name, new_name)
		return super(WebshopItem, self).before_rename(old_name, new_name, merge)

	def validate_duplicate_website_item_before_merge(self, old_name, new_name):
		"""
		Block merge if both old and new items have website items against them.
		This is to avoid duplicate website items after merging.
		"""
		web_items = frappe.get_all(
			"Website Item",
			filters={"item_code": ["in", [old_name, new_name]]},
			fields=["item_code", "name"],
		)

		if len(web_items) <= 1:
			return

		old_web_item = [d.get("name") for d in web_items if d.get("item_code") == old_name][0]
		web_item_link = get_link_to_form("Website Item", old_web_item)
		old_name, new_name = frappe.bold(old_name), frappe.bold(new_name)

		msg = f"Please delete linked Website Item {frappe.bold(web_item_link)} before merging {old_name} into {new_name}"
		frappe.throw(_(msg), title=_("Cannot Merge"), exc=DataValidationError)

	def after_rename(self, old_name, new_name, merge):
		if self.published_in_website:
			invalidate_cache_for_item(self)

		super(WebshopItem, self).after_rename(old_name, new_name, merge)


def invalidate_cache_for_item(doc):
	"""Invalidate Item Group cache and rebuild ItemVariantsCacheManager."""
	invalidate_cache_for(doc, doc.item_group)

	if doc.get("old_item_group") and doc.get("old_item_group") != doc.item_group:
		invalidate_cache_for(doc, doc.old_item_group)

@frappe.whitelist()
def get_item_variants(item_code):
	"""Get all variants of a template item"""
	if not frappe.has_permission("Item"):
		frappe.throw(_("No Permission"))

	# Check if item exists and is a template
	item_doc = frappe.get_cached_doc("Item", item_code)
	if not item_doc.has_variants:
		frappe.throw(_("Item {0} is not a template item with variants.").format(item_code))

	# Get all variants
	variants = frappe.get_all(
		"Item",
		fields=["name", "item_name", "disabled"],
		filters={"variant_of": item_code, "disabled": 0},
		order_by="name",
	)

	return [v.name for v in variants]


@frappe.whitelist()
def generate_variant_prices(
	template_item,
	price_list,
	base_price,
	uom,
	valid_from=None,
	valid_upto=None,
	overwrite_existing=0,
):
	"""Generate Item Price records for all variants of a template item"""

	if not frappe.has_permission("Item Price", "write"):
		frappe.throw(_("No Permission to create Item Price"))

	# Validate inputs
	if not template_item:
		frappe.throw(_("Template Item is required"))
	if not price_list:
		frappe.throw(_("Price List is required"))
	if base_price is None:
		frappe.throw(_("Base Price is required"))

	# Check if price list exists
	if not frappe.db.exists("Price List", price_list):
		frappe.throw(_("Price List {0} does not exist").format(price_list))

	# Get price list details
	price_list_doc = frappe.get_cached_doc("Price List", price_list)
	if not price_list_doc.enabled:
		frappe.throw(_("Price List {0} is not enabled").format(price_list))

	# Get all variants
	variants = get_item_variants(template_item)
	if not variants:
		frappe.throw(_("No variants found for template item {0}").format(template_item))

	created = 0
	skipped = 0
	failed = 0

	# Generate prices for each variant
	for variant_item_code in variants:
		try:
			# Check if price already exists (simple check - same item, price_list, and uom)
			existing_price_name = frappe.db.get_value(
				"Item Price",
				{
					"item_code": variant_item_code,
					"price_list": price_list,
					"uom": uom,
				},
				"name",
			)

			if existing_price_name:
				if overwrite_existing:
					# Update existing price
					item_price_doc = frappe.get_doc("Item Price", existing_price_name)
					item_price_doc.price_list_rate = base_price
					if valid_from:
						item_price_doc.valid_from = valid_from
					if valid_upto:
						item_price_doc.valid_upto = valid_upto
					item_price_doc.save(ignore_permissions=True)
					created += 1
				else:
					skipped += 1
					continue

			else:
				# Create new price
				item_price_doc = frappe.new_doc("Item Price")
				item_price_doc.item_code = variant_item_code
				item_price_doc.price_list = price_list
				item_price_doc.price_list_rate = base_price
				item_price_doc.uom = uom
				if valid_from:
					item_price_doc.valid_from = valid_from
				if valid_upto:
					item_price_doc.valid_upto = valid_upto

				item_price_doc.insert(ignore_permissions=True)
				created += 1

		except Exception as e:
			frappe.log_error(
				title=_("Error creating price for variant {0}").format(variant_item_code),
				message=str(e),
			)
			failed += 1
			continue

	return {
		"created": created,
		"skipped": skipped,
		"failed": failed,
		"total": len(variants),
	}
