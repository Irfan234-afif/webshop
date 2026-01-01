import frappe
from frappe.tests.utils import FrappeTestCase
from webshop.webshop.doctype.override_doctype.item import generate_subscription_plans

class TestSubscriptionGeneration(FrappeTestCase):
	def setUp(self):
		pass

	def test_generate_plans(self):
		# 1. Create Price List
		if not frappe.db.exists("Price List", "Test Subscription PL"):
			frappe.get_doc({
				"doctype": "Price List",
				"price_list_name": "Test Subscription PL",
				"selling": 1,
				"currency": "USD"
			}).insert()

		# 2. Create Template Item
		template_item_code = "Test Sub Template"
		if not frappe.db.exists("Item", template_item_code):
			item = frappe.get_doc({
				"doctype": "Item",
				"item_code": template_item_code,
				"item_name": "Test Sub Template",
				"item_group": "All Item Groups",
				"has_variants": 1,
				"variant_based_on": "Item Attribute",
				"attributes": [{"attribute": "Size"}] # Assuming Size exists or I need to create it
			})
			# Assuming 'Size' attribute exists, if not create it
			if not frappe.db.exists("Item Attribute", "Size"):
				frappe.get_doc({
					"doctype": "Item Attribute",
					"attribute_name": "Size",
					"item_attribute_values": [{"attribute_value": "S"}, {"attribute_value": "M"}]
				}).insert()
			
			item.attributes = [{"attribute": "Size"}]
			item.insert()
		
		# 3. Create Variants
		variant_s = "Test Sub Template-S"
		if not frappe.db.exists("Item", variant_s):
			variant = frappe.new_doc("Item")
			variant.variant_of = template_item_code
			variant.item_code = variant_s
			variant.attributes = [{"attribute": "Size", "attribute_value": "S"}]
			variant.insert()

		# 4. Create Item Price for Variant
		# Price = 1200
		if not frappe.db.exists("Item Price", {"item_code": variant_s, "price_list": "Test Subscription PL"}):
			frappe.get_doc({
				"doctype": "Item Price",
				"item_code": variant_s,
				"price_list": "Test Subscription PL",
				"price_list_rate": 1200
			}).insert()
		
		# 5. Run Generation
		# Divide by 12 -> Cost should be 100
		result = generate_subscription_plans(
			template_item=template_item_code,
			price_list="Test Subscription PL",
			division_factor=12,
			billing_interval="Month",
			billing_timing="Post-Paid"
		)
		
		self.assertEqual(result["created"], 1)
		
		# 6. Verify Subscription Plan
		plan_name_check = frappe.db.get_value(
            "Subscription Plan",
            {"item": variant_s, "billing_interval": "Month", "billing_interval_count": 1},
            "name"
        )
		self.assertTrue(plan_name_check, "Subscription Plan should be created")
		
		plan_cost = frappe.db.get_value("Subscription Plan", plan_name_check, "cost")
		self.assertEqual(plan_cost, 100.0)

		# 7. Run again (Idempotency / Update)
		# Update Price to 2400
		frappe.db.set_value("Item Price", {"item_code": variant_s, "price_list": "Test Subscription PL"}, "price_list_rate", 2400)
		
		result = generate_subscription_plans(
			template_item=template_item_code,
			price_list="Test Subscription PL",
			division_factor=12, # Should now be 200
			billing_interval="Month"
		)
		
		self.assertEqual(result["created"], 1) # Should count as created/updated
		plan_cost_updated = frappe.db.get_value("Subscription Plan", plan_name_check, "cost")
		self.assertEqual(plan_cost_updated, 200.0)

		# 8. Verify Item Link
		item_subscription_plan = frappe.db.get_value("Item", variant_s, "subscription_plan")
		self.assertEqual(item_subscription_plan, plan_name_check)

		# 9. Test Use Fixed Period
		result = generate_subscription_plans(
			template_item=template_item_code,
			price_list="Test Subscription PL",
			division_factor=1,
			billing_interval="Month",
			use_fixed_period=1
		)
		plan_fixed_period = frappe.db.get_value("Subscription Plan", plan_name_check, "use_fixed_period")
		self.assertEqual(plan_fixed_period, 1)
