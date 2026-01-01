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


@frappe.whitelist()
def generate_subscription_plans(
	template_item,
	price_list,
	division_factor=1,
	billing_interval="Month",
	billing_timing="Post-Paid",
	use_fixed_period=0,
):
	"""Generate Subscription Plan records for all variants of a template item"""

	if not frappe.has_permission("Subscription Plan", "write"):
		frappe.throw(_("No Permission to create Subscription Plan"))

	# Validate inputs
	if not template_item:
		frappe.throw(_("Template Item is required"))
	if not price_list:
		frappe.throw(_("Price List is required"))
	
	try:
		division_factor = float(division_factor)
	except ValueError:
		frappe.throw(_("Division Factor must be a number"))

	if division_factor <= 0:
		frappe.throw(_("Division Factor must be greater than 0"))

	# Get all variants
	variants = get_item_variants(template_item)
	if not variants:
		frappe.throw(_("No variants found for template item {0}").format(template_item))

	created = 0
	failed = 0

	# Generate plans for each variant
	for variant_item_code in variants:
		try:
			# 1. Get Item Price
			item_price = frappe.db.get_value(
				"Item Price",
				{"item_code": variant_item_code, "price_list": price_list},
				"price_list_rate",
			)

			if not item_price:
				# Skip if no price found
				continue

			# 2. Calculate Cost
			plan_cost = item_price / division_factor

			# 3. Create or Update Subscription Plan
			# Check existing plan for this item and interval
			existing_plan = frappe.db.get_value(
				"Subscription Plan",
				{
					"item": variant_item_code, 
					"billing_interval": billing_interval,
					"billing_interval_count": 1
				},
				"name"
			)

			if existing_plan:
				plan_doc = frappe.get_doc("Subscription Plan", existing_plan)
				plan_doc.cost = plan_cost
				plan_doc.billing_timing = billing_timing
				plan_doc.use_fixed_period = use_fixed_period
				plan_doc.save(ignore_permissions=True)
				
				# Update Item with this plan
				frappe.db.set_value("Item", variant_item_code, "subscription_plan", existing_plan)
				
				created += 1
			else:
				variant_item = frappe.db.get_value("Item", variant_item_code, "item_name")
				plan_name = f"{variant_item} - {billing_interval}"
				
				new_plan = frappe.new_doc("Subscription Plan")
				new_plan.plan_name = plan_name
				new_plan.item = variant_item_code
				new_plan.price_determination = "Fixed Rate"
				new_plan.cost = plan_cost
				new_plan.billing_interval = billing_interval
				new_plan.billing_interval_count = 1
				new_plan.billing_timing = billing_timing # Custom field
				new_plan.use_fixed_period = use_fixed_period
				
				# Fetch currency from Price List if not set (Subscription Plan usually inherits or has currency)
				# Standard Subscription Plan might not have currency field directly, usually it's in the Plan or derived.
				# Checking schema, usually it has currency.
				price_list_currency = frappe.db.get_value("Price List", price_list, "currency")
				if price_list_currency:
					new_plan.currency = price_list_currency

				new_plan.insert(ignore_permissions=True)
				
				# Update Item with this plan
				frappe.db.set_value("Item", variant_item_code, "subscription_plan", new_plan.name)
				
				created += 1

		except Exception as e:
			frappe.log_error(
				title=_("Error creating subscription plan for variant {0}").format(variant_item_code),
				message=str(e),
			)
			failed += 1
			continue

	return {
		"created": created,
		"failed": failed,
		"total": len(variants),
	}
