# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

"""
Patch to migrate existing hardcoded payment methods to the new Webshop Payment Method doctype
"""

import frappe

def execute():
	"""
	Migrate existing hardcoded payment methods to the new Webshop Payment Method doctype
	"""
	print("Migrating existing payment methods to Webshop Payment Method doctype...")
	
	# Define the existing payment methods as they appear in the current get_payment_methods function
	payment_methods = [
		{
			"payment_method_name": "Virtual Account",
			"title": "Virtual Account",
			"description": "Bayar pesanan dengan Virtual Account melalui mobile banking atau ATM sesuai bank yang dipilih.",
			"payment_gateway_account": "Midtrans - IDR - ISD",
			"payment_type": "Payment Gateway",
			"need_admin_approval": False,
			"enabled": True,
			"icon": "receipt"
		},
		{
			"payment_method_name": "Transfer Bank",
			"title": "Transfer Bank",
			"description": "Lakukan transfer manual ke rekening resmi koperasi sesuai instruksi yang diberikan.",
			"payment_type": "Transfer Manual",
			"need_admin_approval": True,  # Bank transfer typically needs admin approval
			"enabled": True,
			"bank_account": "Koperasi - Bank Central Asia - 1234567890 - BCA",
			"account_holder_name": "Koperasi Sekolah",
			"icon": "credit-card"
		},
		{
			"payment_method_name": "Cash",
			"title": "Cash",
			"description": "Bayar langsung secara tunai di koperasi sekolah pada jam operasional yang tersedia.",
			"payment_type": "Cash",  # Cash is treated as manual since it needs admin confirmation
			"need_admin_approval": True,
			"enabled": True,
			"icon": "dollar-sign"
		},
		{
			"payment_method_name": "Cicilan Koperasi",
			"title": "Cicilan Koperasi",
			"description": "Cicilan tidak tersedia karena Pesanan tidak memenuhi Syarat & Ketentuan.",
			"bank_account": "Koperasi - Bank Central Asia - 1234567890 - BCA",
			"account_holder_name": "Koperasi Sekolah",
			"payment_type": "Transfer Manual",
			"need_admin_approval": True,
			"enabled": False,  # Disabled as per current implementation
			"icon": "calculator"
		}
	]
	
	# Create each payment method in the new doctype
	for method in payment_methods:
		if not frappe.db.exists("Webshop Payment Method", method["payment_method_name"]):
			doc = frappe.new_doc("Webshop Payment Method")
			doc.payment_method_name = method["payment_method_name"]
			doc.title = method["title"]
			doc.description = method["description"]
			doc.payment_type = method["payment_type"]
			if "payment_gateway_account" in method:
				doc.payment_gateway_account = method["payment_gateway_account"]
			if "bank_account" in method:
				doc.bank_account = method["bank_account"]
			if "account_holder_name" in method:
				doc.account_holder_name = method["account_holder_name"]
			doc.need_admin_approval = method["need_admin_approval"]
			doc.enabled = method["enabled"]
			doc.icon = method["icon"]
			doc.insert(ignore_permissions=True)
			print(f"Created payment method: {method['payment_method_name']}")
		else:
			print(f"Payment method already exists: {method['payment_method_name']}")
	
	frappe.db.commit()
	print("Payment methods migration completed successfully!")