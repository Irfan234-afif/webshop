import frappe

def setup_data():
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

    if not frappe.db.exists('Supplier Group', 'All Supplier Groups'):
        frappe.get_doc({
            'doctype': 'Supplier Group',
            'supplier_group_name': 'All Supplier Groups',
            'is_group': 1
        }).insert(ignore_permissions=True)

    if not frappe.db.exists('Item Group', 'All Item Groups'):
        frappe.get_doc({
            'doctype': 'Item Group',
            'item_group_name': 'All Item Groups',
            'is_group': 1
        }).insert(ignore_permissions=True)

    stock_entry_types = [
        "Material Issue", "Material Receipt", "Material Transfer",
        "Material Transfer for Manufacture", "Material Consumption for Manufacture",
        "Manufacture", "Repack", "Send to Subcontractor", "Disassemble",
        "Receive from Customer", "Return Raw Material to Customer",
        "Subcontracting Delivery", "Subcontracting Return"
    ]
    for set_name in stock_entry_types:
        if not frappe.db.exists('Stock Entry Type', set_name):
            print(f"Creating Stock Entry Type {set_name}...")
            frappe.get_doc({
                'doctype': 'Stock Entry Type',
                'name': set_name,
                'purpose': set_name,
                'is_standard': 1
            }).insert(ignore_permissions=True)
        else:
            # Force update is_standard if it exists
            print(f"Updating Stock Entry Type {set_name} to be standard...")
            frappe.db.set_value("Stock Entry Type", set_name, "is_standard", 1)
    
    frappe.db.commit()

    # Create a BOM if needed for test records dependencies
    # Wipe ALL Item Prices to avoid duplicates during test record generation
    print("Wiping ALL Item Price records...")
    frappe.db.delete("Item Price")

    # Wipe ALL Tax Rules to avoid ConflictingTaxRule
    print("Wiping ALL Tax Rule records...")
    frappe.db.delete("Tax Rule")

    # Set default company to avoid BOM validation errors
    frappe.db.set_default("company", "_Test Company")

    # Fix Account Types for _Test Company to avoid Journal Entry validation errors
    accounts_to_fix = [
        ("Debtors - _TC", "Receivable"),
        ("Creditors - _TC", "Payable")
    ]
    for acc_name, acc_type in accounts_to_fix:
        if frappe.db.exists("Account", acc_name):
            print(f"Updating {acc_name} to {acc_type}...")
            frappe.db.set_value("Account", acc_name, "account_type", acc_type)
            # Clear cache for this document to ensure next reads are fresh
            frappe.clear_document_cache("Account", acc_name)
    
    # Debug Account Details
    d = frappe.get_doc("Account", "Debtors - _TC")
    print(f"DEBUG: Debtors - _TC: account_type={d.account_type}, root_type={d.root_type}, report_type={d.report_type}, is_group={d.is_group}, company={d.company}")

    frappe.db.commit()
    frappe.clear_cache() # Clear global cache to be safe

    # Create a BOM if needed for test records dependencies
    pass

    print("Checking fixtures...")
    if not frappe.db.exists('Territory', 'All Territories'):
        print("Creating All Territories...")
        frappe.get_doc({
            'doctype': 'Territory',
            'territory_name': 'All Territories',
            'is_group': 1
        }).insert(ignore_permissions=True)

    if not frappe.db.exists('Company', '_Test Company'):
        print("Creating _Test Company...")
        frappe.get_doc({
            'doctype': 'Company',
            'company_name': '_Test Company',
            'abbr': '_TC',
            'default_currency': 'IDR',
            'country': 'Indonesia',
            'create_chart_of_accounts_based_on': 'Standard Template',
            'chart_of_accounts': 'Standard'
        }).insert(ignore_permissions=True)
        frappe.db.commit() # Commit immediately after Company creation

    if frappe.db.exists('Company', '_Test Company'):
        print("Trigerring save on _Test Company to create defaults...")
        c = frappe.get_doc("Company", "_Test Company")
        c.save()
        frappe.db.commit()

    if not frappe.db.exists('Cost Center', '_Test Company - _TC'):
       print("Cost Center _Test Company - _TC still missing after save!")

    frappe.db.commit()
    print("Fixtures setup complete.")
