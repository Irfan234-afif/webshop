
import frappe
from frappe.tests.utils import FrappeTestCase
from webshop.webshop.api.subscription_checkout import create_subscription_request


class TestSubscriptionRequest(FrappeTestCase):
	def setUp(self):
		# Create Test Customer
		if not frappe.db.exists("Customer", "_Test Customer Sub"):
			self.customer = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": "_Test Customer Sub",
				"customer_type": "Individual",
				"customer_group": "All Customer Groups",
				"territory": "All Territories",
				"email_id": "test_sub_customer@example.com"
			}).insert(ignore_permissions=True)
		else:
			self.customer = frappe.get_doc("Customer", "_Test Customer Sub")
			
		# Create User if not exists
		if not frappe.db.exists("User", "test_sub_customer@example.com"):
			self.user = frappe.get_doc({
				"doctype": "User",
				"email": "test_sub_customer@example.com",
				"first_name": "Test Sub",
				"enabled": 1,
				"roles": [{"role": "Customer"}]
			}).insert(ignore_permissions=True)

		# Create Item (Initially without Plan to avoid circular dependency)
		if not frappe.db.exists("Item", "_Test Sub Item"):
			self.item = frappe.get_doc({
				"doctype": "Item",
				"item_code": "_Test Sub Item",
				"item_group": "All Item Groups",
				"is_stock_item": 0,
				"is_subscription_item": 1
			}).insert(ignore_permissions=True)
		else:
			self.item = frappe.get_doc("Item", "_Test Sub Item")

		# Create Subscription Plan
		if not frappe.db.exists("Subscription Plan", "_Test Sub Plan"):
			self.plan = frappe.get_doc({
				"doctype": "Subscription Plan",
				"plan_name": "_Test Sub Plan",
				"billing_interval": "Month",
				"billing_interval_count": 1,
				"cost": 100000,
				"currency": "IDR",
				"billing_timing": "Post-Paid",
				"item": "_Test Sub Item", # Link to Item
				"price_determination": "Fixed Rate"
			}).insert(ignore_permissions=True)
			
		# Update Item with Plan
		frappe.db.set_value("Item", "_Test Sub Item", "subscription_plan", "_Test Sub Plan")

	def test_create_request_api(self):
		frappe.set_user("test_sub_customer@example.com")
		
		data = {
			"item_code": "_Test Sub Item",
			"start_date": "2025-01-15",
			"notes": "Test API Request"
		}
		
		req_name = create_subscription_request(data)
		self.assertTrue(req_name)
		
		doc = frappe.get_doc("Subscription Request", req_name)
		self.assertEqual(doc.customer, self.customer.name)
		self.assertEqual(doc.item, "_Test Sub Item")
		self.assertEqual(str(doc.start_date), "2025-01-15")
		# end_date should be auto-calculated based on plan billing interval
		self.assertTrue(doc.end_date, "end_date should be auto-calculated")
		self.assertEqual(doc.docstatus, 0)

	def test_submit_creates_subscription(self):
		frappe.set_user("Administrator")
		
		# Create Request
		req = frappe.get_doc({
			"doctype": "Subscription Request",
			"customer": self.customer.name,
			"item": "_Test Sub Item",
			"subscription_plan": "_Test Sub Plan",
			"start_date": "2025-02-01",
			"notes": "Testing Submission"
		}).insert()
		
		# Submit
		req.submit()
		self.assertEqual(req.docstatus, 1)
		
		# Check Subscription Ref
		self.assertTrue(req.subscription_ref)
		
		# Validate Created Subscription
		sub = frappe.get_doc("Subscription", req.subscription_ref)
		self.assertEqual(sub.party, self.customer.name)
		self.assertEqual(str(sub.start_date), "2025-02-01")
		# end_date should be auto-calculated (for Monthly plan, should be ~2025-03-01)
		self.assertTrue(sub.end_date, "Subscription should have end_date from auto-calculation")
		self.assertEqual(sub.docstatus, 1) # Should be submitted/active
		self.assertEqual(sub.docstatus, 1) # Should be submitted/active
		self.assertEqual(sub.generate_invoice_at, "End of the current subscription period")
		self.assertEqual(sub.plans[0].plan, "_Test Sub Plan")

	def test_get_item_details(self):
		from webshop.webshop.api.subscription_checkout import get_subscription_item_details
		
		# Test with existing item
		details = get_subscription_item_details("_Test Sub Item")
		self.assertEqual(details["item_code"], "_Test Sub Item")
		self.assertEqual(details["plan_name"], "_Test Sub Plan")
		self.assertEqual(details["billing_interval"], "Month")

	def test_auto_create_customer(self):
		# check if Webshop Settings enabled (required for get_party to create customer)
		# Do this as Administrator
		frappe.set_user("Administrator")
		settings = frappe.get_doc("Webshop Settings")
		settings.enabled = 1
		
		# Find or Create Payment Gateway Account
		pga = frappe.db.get_value("Payment Gateway Account", {"currency": "IDR"}, "name")
		if not pga:
			# Setup dependencies
			gateway_name = "Wire Transfer"
			if not frappe.db.exists("Payment Gateway", gateway_name):
				frappe.get_doc({"doctype": "Payment Gateway", "gateway": gateway_name}).insert(ignore_permissions=True)
			
			# Get Company from settings or default
			company = settings.company or "_Test Company"
			
			# Ensure we have a bank/cash account
			bank_acc = frappe.db.get_value("Account", {"company": company, "is_group": 0, "root_type": "Asset"}, "name")
			
			pga_doc = frappe.get_doc({
				"doctype": "Payment Gateway Account",
				"payment_gateway": gateway_name,
				"payment_account": bank_acc,
				"currency": "IDR"
			})
			pga_doc.insert(ignore_permissions=True)
			pga = pga_doc.name
			
		settings.payment_gateway_account = pga
		settings.save(ignore_permissions=True)

		# Create a new user without customer
		new_user = "new_sub_user@example.com"
		if not frappe.db.exists("User", new_user):
			frappe.get_doc({
				"doctype": "User",
				"email": new_user,
				"first_name": "New Sub User",
				"enabled": 1,
				"roles": [{"role": "Customer"}]
			}).insert(ignore_permissions=True)
			
		frappe.set_user(new_user)
		
		# Ensure no customer exists for this user initially
		# (Cleanup if exists from prev run)
		# ... relying on test transaction rollback mostly
		
		data = {
			"item_code": "_Test Sub Item",
			"start_date": "2025-03-01",
			"notes": "Auto Create Customer Test"
		}
		
		req_name = create_subscription_request(data)
		self.assertTrue(req_name)
		
		doc = frappe.get_doc("Subscription Request", req_name)
		self.assertTrue(doc.customer, "Customer should be auto-created and linked")
		
		# Verify it's not the default test customer
		self.assertNotEqual(doc.customer, self.customer.name)

	def tearDown(self):
		frappe.set_user("Administrator")
		# frappe.db.rollback() # TestCase handles rollback usually? FrappeTestCase does.
