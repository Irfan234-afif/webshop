import frappe
from frappe.tests.utils import FrappeTestCase
from webshop.webshop.api.cooperative import register_member, approve_member

class TestCooperativeMember(FrappeTestCase):
	def setUp(self):
		# Create Test Company if not exists
		if not frappe.db.exists("Company", "Test Cooperative"):
			doc = frappe.new_doc("Company")
			doc.company_name = "Test Cooperative"
			doc.default_currency = "IDR"
			doc.insert(ignore_permissions=True)
		
		# Create Equity Accounts
		def create_account(name, account_type="Equity"):
			if not frappe.db.exists("Account", f"{name} - TC"):
				acc = frappe.new_doc("Account")
				acc.account_name = name
				acc.company = "Test Cooperative"
				acc.parent_account = "Equity - TC" if account_type == "Equity" else "Application of Funds (Assets) - TC"
				acc.account_type = account_type
				acc.is_group = 0
				acc.insert(ignore_permissions=True)
			return f"{name} - TC"

		self.principal_account = create_account("Principal Saving")
		self.mandatory_account = create_account("Mandatory Saving")
		self.voluntary_account = create_account("Voluntary Saving")
		self.bank_account = create_account("Bank Account", "Bank")

		# Setup Cooperative Settings
		settings = frappe.get_doc("Cooperative Settings")
		settings.principal_saving_amount = 250000
		settings.mandatory_saving_amount = 50000
		settings.principal_saving_account = self.principal_account
		settings.mandatory_saving_account = self.mandatory_account
		settings.voluntary_saving_account = self.voluntary_account
		settings.default_bank_account = self.bank_account
		settings.company = "Test Cooperative"
		settings.save(ignore_permissions=True)

		# Setup Payment Method
		if not frappe.db.exists("Webshop Payment Method", "Test Manual Transfer"):
			pm = frappe.new_doc("Webshop Payment Method")
			pm.payment_method_name = "Test Manual Transfer"
			pm.title = "Transfer Manual"
			pm.payment_type = "Transfer Manual"
			pm.need_admin_approval = 1
			pm.insert(ignore_permissions=True)

		self.payment_method = "Test Manual Transfer"

		# Setup test user and customer
		self.user = "test_coop@example.com"
		if not frappe.db.exists("User", self.user):
			user = frappe.new_doc("User")
			user.email = self.user
			user.first_name = "Test Coop"
			user.insert(ignore_permissions=True)

		self.customer_name = "Test Customer Coop"
		if not frappe.db.exists("Customer", self.customer_name):
			cust = frappe.new_doc("Customer")
			cust.customer_name = self.customer_name
			cust.contact_email = self.user
			cust.customer_group = "All Customer Groups"
			cust.territory = "All Territories"
			cust.insert(ignore_permissions=True)

		frappe.set_user(self.user)

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_registration_flow(self):
		# 1. Register Member
		member_data = {
			"nik": "1234567890123456",
			"full_name": "Test Member",
			"place_of_birth": "Jakarta",
			"date_of_birth": "1990-01-01",
			"gender": "Male",
			"occupation": "Engineer",
			"marital_status": "Single",
			"email": self.user,
			"phone_number": "08123456789",
			"relationship_with_cooperative": "Self",
			"province": "DKI Jakarta",
			"city": "Jakarta",
			"district": "Kebayoran",
			"sub_district": "Senayan",
			"postal_code": "12190",
			"full_address": "Jl. Test No. 1",
			"emergency_contact_name": "Emergency Test",
			"emergency_contact_phone": "08987654321",
			"emergency_contact_relationship": "Parent",
			"emergency_contact_address": "Jl. Emergency"
		}
		
		# Set photo bypassing actual file upload for testing
		frappe.flags.ignore_links = True
		member_data["ktp_photo"] = "/files/test.png"
		
		member_name = register_member(member_data)
		frappe.flags.ignore_links = False
		
		member = frappe.get_doc("Cooperative Member", member_name)
		self.assertEqual(member.status, "Draft")
		self.assertEqual(member.total_registration_amount, 300000)

		# 2. Create Payment Request
		from webshop.webshop.api.cooperative_payment import create_registration_payment_request
		
		frappe.set_user("Administrator")
		res = create_registration_payment_request(member.name, self.payment_method)
		pr_name = res.get("payment_request")
		self.assertTrue(pr_name)

		member.reload()
		self.assertEqual(member.status, "Pending Payment")

		# 3. Approve Payment (Simulate docstatus=1 which triggers on_submit)
		pr = frappe.get_doc("Payment Request", pr_name)
		pr.payment_proof = "/files/proof.png"
		pr.submit()

		# 4. Verify Active Status & Mandatory Saving
		member.reload()
		self.assertEqual(member.status, "Active")
		
		ms_records = frappe.get_all("Mandatory Saving", filters={"cooperative_member": member.name})
		self.assertTrue(len(ms_records) > 0)

		# 5. Check Journal Entry
		jes = frappe.get_all("Journal Entry Account", filters={"party": member.customer}, fields=["parent", "account", "credit_in_account_currency"])
		
		has_principal_credit = False
		has_mandatory_credit = False
		for entry in jes:
			if entry.account == self.principal_account and entry.credit_in_account_currency == 250000:
				has_principal_credit = True
			if entry.account == self.mandatory_account and entry.credit_in_account_currency == 50000:
				has_mandatory_credit = True

		self.assertTrue(has_principal_credit, "Principal Saving Equity was not credited")
		self.assertTrue(has_mandatory_credit, "Mandatory Saving Equity was not credited")
