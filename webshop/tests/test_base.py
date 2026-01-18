
import frappe
from frappe.tests.utils import FrappeTestCase

class WebshopTestCase(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.setup_webshop_fixtures()

	@classmethod
	def setup_webshop_fixtures(cls):
		"""
		Setup basic fixtures required for Webshop tests.
		This includes Companies, Stock Entry Types, Accounts, etc.
		to prevent standard ERPNext validation errors during test record creation.
		"""
		frappe.flags.ignore_permissions = True

		# 1. Clean up conflicting data from previous runs or standard test records
		cls.cleanup_conflicts()

		# 2. Setup Basic Definitions (Groups, Territories)
		cls.setup_basic_definitions()

		# 3. Setup Company and Defaults
		cls.setup_company()
		

		# 4. Setup Accounting
		cls.setup_accounting()
		
		# 5. Setup Inventory/Stock
		cls.setup_stock_fixtures()

		# 6. Setup Webshop Settings
		cls.setup_webshop_settings()
		
		frappe.db.commit()

	@classmethod
	def setup_basic_definitions(cls):
		# Customer Groups
		if not frappe.db.exists('Customer Group', 'All Customer Groups'):
			frappe.get_doc({
				'doctype': 'Customer Group',
				'customer_group_name': 'All Customer Groups',
				'is_group': 1
			}).insert(ignore_permissions=True)

		if not frappe.db.exists('Customer Group', 'Individual'):
			frappe.get_doc({
				'doctype': 'Customer Group',
				'customer_group_name': 'Individual',
				'parent_customer_group': 'All Customer Groups',
				'is_group': 0
			}).insert(ignore_permissions=True)

		# Supplier Groups
		if not frappe.db.exists('Supplier Group', 'All Supplier Groups'):
			frappe.get_doc({
				'doctype': 'Supplier Group',
				'supplier_group_name': 'All Supplier Groups',
				'is_group': 1
			}).insert(ignore_permissions=True)

		# Item Groups
		if not frappe.db.exists('Item Group', 'All Item Groups'):
			frappe.get_doc({
				'doctype': 'Item Group',
				'item_group_name': 'All Item Groups',
				'is_group': 1
			}).insert(ignore_permissions=True)
			
		# Territories
		if not frappe.db.exists('Territory', 'All Territories'):
			frappe.get_doc({
				'doctype': 'Territory',
				'territory_name': 'All Territories',
				'is_group': 1
			}).insert(ignore_permissions=True)

	@classmethod
	def cleanup_conflicts(cls):
		# Wipe Item Prices to prevent ItemPriceDuplicateItem error during make_test_records
		frappe.db.delete("Item Price")
		
		# Wipe Tax Rules to prevent ConflictingTaxRule error
		frappe.db.delete("Tax Rule")

	@classmethod
	def setup_company(cls):
		company_name = "_Test Company"
		if not frappe.db.exists("Company", company_name):
			frappe.get_doc({
				"doctype": "Company",
				"company_name": company_name,
				"abbr": "_TC",
				"default_currency": "IDR",
				"country": "Indonesia",
				"create_chart_of_accounts_based_on": "Standard Template",
				"chart_of_accounts": "Standard",
			}).insert(ignore_permissions=True)
		
		# Set as default company to avoid missing company errors in BOM/etc
		frappe.db.set_default("company", company_name)
		
		# Note: Skipping company.save() as it may trigger validation errors
		# in certain ERPNext versions (e.g., enable_item_wise_inventory_account attribute error)
		# The company is already created above, so this save is not strictly necessary


	@classmethod
	def setup_accounting(cls):
		# Fix Account Types for Journal Entry validation
		accounts_to_fix = [
			("Debtors - _TC", "Receivable"),
			("Creditors - _TC", "Payable")
		]
		for acc_name, acc_type in accounts_to_fix:
			if frappe.db.exists("Account", acc_name):
				frappe.db.set_value("Account", acc_name, "account_type", acc_type)
				frappe.clear_document_cache("Account", acc_name)
		
		# Clear global cache to ensure account type changes are picked up
		frappe.clear_cache()

	@classmethod
	def setup_stock_fixtures(cls):
		# Create only the standard Stock Entry Types that are valid in ERPNext v16
		# Based on the error message, valid options are:
		stock_entry_types = [
			"Material Issue", "Material Receipt", "Material Transfer",
			"Material Transfer for Manufacture", "Material Consumption for Manufacture",
			"Manufacture", "Repack", "Send to Subcontractor", "Disassemble"
		]
		for set_name in stock_entry_types:
			if not frappe.db.exists("Stock Entry Type", set_name):
				frappe.get_doc({
					"doctype": "Stock Entry Type",
					"name": set_name,
					"purpose": set_name,
					"is_standard": 1
				}).insert(ignore_permissions=True)
			else:
				# Ensure it is marked as standard
				if not frappe.db.get_value("Stock Entry Type", set_name, "is_standard"):
					frappe.db.set_value("Stock Entry Type", set_name, "is_standard", 1)



		# Create Stock Account if not exists
		account_name = "_Test Warehouse - _TC"
		if not frappe.db.exists("Account", account_name):
			parent = frappe.db.get_value("Account", {"account_name": "Stock Assets", "company": "_Test Company"}, "name")
			if not parent:
				# Fallback to any Asset Group
				parent = frappe.db.get_value("Account", {"is_group": 1, "root_type": "Asset", "company": "_Test Company"}, "name")
			
			if parent:
				# Use ignore_if_duplicate to prevent errors if account already exists
				try:
					frappe.get_doc({
						"doctype": "Account",
						"account_name": "_Test Warehouse",
						"parent_account": parent,
						"company": "_Test Company",
						"account_type": "Stock",
						"currency": "IDR"
					}).insert(ignore_permissions=True, ignore_if_duplicate=True)
				except frappe.DuplicateEntryError:
					# Account already exists, skip
					pass


		# Ensure generic Warehouse exists

	@classmethod
	def setup_webshop_settings(cls):
		# Ensure settings exist and are configured
		settings = frappe.get_doc("Webshop Settings")
		settings.enabled = 1
		settings.company = "_Test Company"
		settings.price_list = "Standard Selling"
		settings.default_customer_group = "All Customer Groups"
		settings.quotation_series = "QTN-.YYYY.-"
		settings.flags.ignore_mandatory = True
		settings.save(ignore_permissions=True)
		
		# Ensure Price List exists and has correct currency
		if not frappe.db.exists("Price List", "Standard Selling"):
			frappe.get_doc({
				"doctype": "Price List",
				"price_list_name": "Standard Selling",
				"enabled": 1,
				"buying": 0,
				"selling": 1,
				"currency": "IDR" 
			}).insert(ignore_permissions=True)
		else:
			# Verify currency matches company
			frappe.db.set_value("Price List", "Standard Selling", "currency", "IDR")
