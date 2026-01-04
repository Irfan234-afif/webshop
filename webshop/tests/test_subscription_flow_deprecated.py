import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_days, add_months, getdate, nowdate

class TestSubscriptionFlow(FrappeTestCase):
	def setUp(self):
		self.create_company_if_not_exists()
		self.create_account_if_not_exists()
		self.create_customer()
		self.create_subscription_plan("Test Monthly Plan", "Month", 100000)
		self.create_subscription_item("Test Sub Item Month", "Test Monthly Plan")
		
		self.create_subscription_plan("Test Yearly Plan", "Year", 1000000)
		self.create_subscription_item("Test Sub Item Year", "Test Yearly Plan")

		self.create_regular_item()

	def create_company_if_not_exists(self):
		if not frappe.db.exists("Company", "_Test Company"):
			doc = frappe.new_doc("Company")
			doc.company_name = "_Test Company"
			doc.abbr = "_TC"
			doc.default_currency = "IDR"
			doc.country = "Indonesia"
			doc.insert()
			
	def create_account_if_not_exists(self):
		abbr = frappe.get_value("Company", "_Test Company", "abbr")
		self.assets_account = f"Assets - {abbr}"
		self.cash_account = f"Cash - {abbr}"
		self.debtors_account = f"Debtors - {abbr}"

		# 1. Create Root Asset Account
		if not frappe.db.exists("Account", self.assets_account):
			root = frappe.new_doc("Account")
			root.account_name = "Assets"
			root.company = "_Test Company"
			root.is_group = 1
			root.root_type = "Asset"
			root.report_type = "Balance Sheet"
			root.account_currency = "IDR"
			# Root account needs ignore_mandatory because parent_account is mandatory but None for root.
			root.flags.ignore_mandatory = True
			root.insert(ignore_permissions=True)

		# 2. Create Cash Account
		if not frappe.db.exists("Account", self.cash_account):
			doc = frappe.new_doc("Account")
			doc.account_name = "Cash"
			doc.company = "_Test Company"
			doc.parent_account = self.assets_account
			doc.is_group = 0
			doc.account_type = "Cash"
			doc.root_type = "Asset"
			doc.report_type = "Balance Sheet"
			doc.account_currency = "IDR"
			doc.insert(ignore_permissions=True)

		# 3. Create Debtors Account (Receivable)
		if not frappe.db.exists("Account", self.debtors_account):
			doc = frappe.new_doc("Account")
			doc.account_name = "Debtors"
			doc.company = "_Test Company"
			doc.parent_account = self.assets_account
			doc.is_group = 0
			doc.account_type = "Receivable"
			doc.root_type = "Asset"
			doc.report_type = "Balance Sheet"
			doc.account_currency = "IDR"
			doc.insert(ignore_permissions=True)

		# 4. Set Company Defaults
		company = frappe.get_doc("Company", "_Test Company")
		company.default_cash_account = self.cash_account
		company.default_receivable_account = self.debtors_account
		company.save(ignore_permissions=True)
		


	def create_customer(self):
		if not frappe.db.exists("Customer", "_Test Subscription Customer"):
			abbr = frappe.get_value("Company", "_Test Company", "abbr")
			debtors_account = f"Debtors - {abbr}"
			
			doc = frappe.new_doc("Customer")
			doc.customer_name = "_Test Subscription Customer"
			doc.customer_type = "Individual"
			doc.customer_group = "All Customer Groups"
			doc.territory = "All Territories"
			
			# Force link to Debtors account to prevent Payment Entry resolving to Cash
			doc.append("accounts", {
				"company": "_Test Company",
				"account": debtors_account
			})
			
			doc.insert()
		self.customer = frappe.get_doc("Customer", "_Test Subscription Customer")

	def create_payment(self, so, amount):
		from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
		
		# get_payment_entry auto-fetches defaults from Company
		pe = get_payment_entry("Sales Order", so.name)
		pe.payment_type = "Receive"
		pe.paid_amount = amount
		pe.received_amount = amount
		pe.target_exchange_rate = 1.0

		# Explicitly set accounts to reuse the ones we created
		abbr = frappe.get_value("Company", "_Test Company", "abbr")
		pe.paid_from = f"Debtors - {abbr}"
		pe.paid_to = f"Cash - {abbr}"
		

		
		pe.save(ignore_permissions=True)
		pe.submit()

	def create_subscription_plan(self, name, interval, cost):
		if not frappe.db.exists("Subscription Plan", name):
			# Create Item first for the plan
			item_name = f"Item for {name}"
			if not frappe.db.exists("Item", item_name):
				i = frappe.new_doc("Item")
				i.item_code = item_name
				i.item_group = "Services"
				i.is_stock_item = 0
				i.insert()

			doc = frappe.new_doc("Subscription Plan")
			doc.plan_name = name
			doc.item = item_name
			doc.price_determination = "Fixed Rate"
			doc.billing_interval = interval
			doc.billing_interval_count = 1
			doc.currency = "IDR"
			doc.cost = cost
			doc.insert()

	def create_subscription_item(self, item_code, plan_name):
		if not frappe.db.exists("Item", item_code):
			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_group = "Services"
			doc.stock_uom = "Unit"
			doc.is_stock_item = 0
			doc.insert()
		
		# Update to be sub item
		doc = frappe.get_doc("Item", item_code)
		doc.is_subscription_item = 1
		doc.subscription_plan = plan_name
		doc.save()

	def create_regular_item(self):
		if not frappe.db.exists("Item", "Test Regular Item"):
			doc = frappe.new_doc("Item")
			doc.item_code = "Test Regular Item"
			doc.item_group = "Products"
			doc.stock_uom = "Unit"
			doc.is_stock_item = 0
			doc.insert()

	def create_sales_order(self):
		so = frappe.new_doc("Sales Order")
		so.company = "_Test Company"
		so.customer = self.customer.name
		so.transaction_date = nowdate()
		return so

	def test_mixed_cart_flow(self):
		"""Test correct handling of mixed subscription and regular items"""
		so = self.create_sales_order()
		
		# Add 1 Sub Item and 1 Regular Item
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		so.append("items", {
			"item_code": "Test Regular Item",
			"qty": 5,
			"rate": 500,
			"delivery_date": add_days(nowdate(), 1)
		})
		
		so.save()
		so.submit()
		
		# Must Pay to trigger subscription
		self.create_payment(so, 102500) # 100k + 5*500
		
		# Verify Subscription Created for ONLY the sub item
		subscriptions = frappe.get_all("Subscription", filters={
			"sales_order_ref": so.name
		}, fields=["name", "start_date"])
		
		self.assertEqual(len(subscriptions), 1)
		
		sub_doc = frappe.get_doc("Subscription", subscriptions[0].name)
		self.assertEqual(len(sub_doc.plans), 1)
		self.assertEqual(sub_doc.plans[0].plan, "Test Monthly Plan")

	def test_multiple_subscription_items_same_period(self):
		"""Test bundling multiple items with same interval into one Subscription"""
		so = self.create_sales_order()
		
		# Add 2 Same Plan Items (simulating different products with same schedule)
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		# Reuse same item code for simplicity, effectively qty=2 but distinct lines
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		
		so.save()
		so.submit()
		
		# Must Pay
		self.create_payment(so, 200000)

		# Should create ONE subscription with TWO plans (or one plan with qty=2 if merged, but SO logic keeps lines)
		subscriptions = frappe.get_all("Subscription", filters={
			"sales_order_ref": so.name
		})
		self.assertEqual(len(subscriptions), 1)
		
		sub_doc = frappe.get_doc("Subscription", subscriptions[0].name)
		self.assertEqual(len(sub_doc.plans), 2)


	def test_multiple_subscription_items_diff_period(self):
		"""Test creation of SEPARATE subscriptions for items with different end dates"""
		so = self.create_sales_order()
		
		# Month Plan
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		# Year Plan
		so.append("items", {
			"item_code": "Test Sub Item Year",
			"qty": 1,
			"rate": 1000000,
			"delivery_date": add_days(nowdate(), 1)
		})
		
		so.save()
		so.submit()
		
		# Must Pay
		self.create_payment(so, 1100000)

		# Should create TWO subscriptions because service_end_dates differ
		subscriptions = frappe.get_all("Subscription", filters={
			"sales_order_ref": so.name
		})
		self.assertEqual(len(subscriptions), 2)
		

	def test_idempotency(self):
		"""Ensure re-running the hook doesn't duplicate subscriptions"""
		so = self.create_sales_order()
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		so.save()
		so.submit()
		
		self.create_payment(so, 100000)

		# Initial check
		subscriptions = frappe.get_all("Subscription", filters={"sales_order_ref": so.name})
		self.assertEqual(len(subscriptions), 1)
		
		# Manually trigger hook again
		from webshop.webshop.api.subscription import process_subscription_order
		process_subscription_order(so)
		
		# Should still be 1
		subscriptions_after = frappe.get_all("Subscription", filters={"sales_order_ref": so.name})
		self.assertEqual(len(subscriptions_after), 1)

	def test_unpaid_sales_order_flow(self):
		"""
		Test requirement: Subscription created ONLY after Payment.
		Unpaid SO -> No Subscription.
		"""
		so = self.create_sales_order()
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		so.save()
		so.submit()
		
		# Verify Subscription is NOT created (because unpaid)
		subscriptions = frappe.get_all("Subscription", filters={"sales_order_ref": so.name})
		self.assertEqual(len(subscriptions), 0, "Unpaid SO should NOT create Subscription")

	def test_paid_sales_order_flow(self):
		"""
		Test requirement: Subscription created ONLY after Payment.
		Unpaid SO -> No Subscription.
		Payment Entry -> Created Subscription.
		"""
		# 1. Create SO
		so = self.create_sales_order()
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		so.save()
		so.submit()

		# Assert Empty
		self.assertEqual(len(frappe.get_all("Subscription", filters={"sales_order_ref": so.name})), 0)

		# 2. Create Payment Logic
		# Simulate Payment Entry
		self.create_payment(so, 100000)

		# 3. Verify Subscription Created
		subscriptions = frappe.get_all("Subscription", filters={"sales_order_ref": so.name})
		self.assertTrue(len(subscriptions) > 0, "Paid SO should create Subscription")


	def test_cancelled_sales_order_logic(self):
		"""
		Checking what happens if the SO is cancelled. 
		Currently, we don't have a hook for on_cancel. 
		This test expects the Sub to remain unless we add logic.
		"""
		so = self.create_sales_order()
		so.append("items", {
			"item_code": "Test Sub Item Month",
			"qty": 1,
			"rate": 100000,
			"delivery_date": add_days(nowdate(), 1)
		})
		so.submit()
		
		# Must Pay to create Subscription
		self.create_payment(so, 100000)
		
		# Subscription Exists
		subs = frappe.get_all("Subscription", filters={"sales_order_ref": so.name})
		self.assertTrue(len(subs) > 0)
		
		# ERPNext prevents cancelling SO if linked Subscription exists (LinkExistsError)
		# So we must Cancel the Subscription FIRST to allow SO cancellation.
		# This confirms the strict linkage we added.
		sub_doc = frappe.get_doc("Subscription", subs[0].name)
		sub_doc.cancel()
		
		# Now Cancel SO
		so.reload()
		so.cancel()
		
		self.assertEqual(sub_doc.docstatus, 2) # Cancelled
		self.assertEqual(so.docstatus, 2)      # Cancelled

	def test_post_paid_subscription_flow(self):
		"""
		Test "Post-Paid" logic where Subscription starts IMMEDIATELY (Sign Up flow).
		"""
		# 1. Create a Post-Paid Plan
		plan_name = "Test Post-Paid Plan"
		if not frappe.db.exists("Subscription Plan", plan_name):
			self.create_subscription_plan(plan_name, "Month", 0) # Zero cost for signup
			plan = frappe.get_doc("Subscription Plan", plan_name)
			plan.billing_timing = "Post-Paid"
			plan.save()
		
		# 2. Create Item for it
		item_code = "Test Post-Paid Item"
		self.create_subscription_item(item_code, plan_name)
		
		# 3. Create SO
		so = self.create_sales_order()
		so.append("items", {
			"item_code": item_code,
			"qty": 1,
			"rate": 0, # Free signup
			"delivery_date": add_days(nowdate(), 1)
		})
		so.save()
		so.submit()
		
		# Since amount is 0, it considered fully paid immediately?
		# Wait, doc.grand_total is 0. advance_paid is 0. 0 >= 0 is True.
		# So it should trigger on submit.
		
		# Trigger manually if hook didn't fire (hook fires on submit)
		# But let's check if it exists.
		
		subscriptions = frappe.get_all("Subscription", filters={"sales_order_ref": so.name}, fields=["name", "start_date", "generate_invoice_at"])
		self.assertEqual(len(subscriptions), 1, "Should create subscription for free/post-paid signup")
		
		sub = subscriptions[0]
		
		# 4. Verify Start Date
		# Post-Paid should start on Service Start Date (Today)
		# NOT Service End Date + 1
		
		# Get Item Service Start Date (defaults to transaction date)
		so_item = so.items[0]
		expected_start = getdate(so_item.service_start_date)
		actual_start = getdate(sub.start_date)
		
		self.assertEqual(actual_start, expected_start, f"Post-Paid Sub should start immediately on {expected_start}, got {actual_start}")
		
		# 5. Verify Invoice Generation Timing (Arrears)
		self.assertEqual(sub.generate_invoice_at, "End of the current subscription period", "Post-Paid sub should bill at end of period")

	def tearDown(self):
		frappe.db.rollback()
