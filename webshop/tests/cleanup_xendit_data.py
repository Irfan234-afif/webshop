import frappe

def execute():
    frappe.set_user("Administrator")
    
    # helper to cancel and delete
    def cancel_and_delete(doctype, filters):
        docs = frappe.db.get_all(doctype, filters=filters, pluck="name")
        for name in docs:
            try:
                doc = frappe.get_doc(doctype, name)
                if doc.docstatus == 1:
                    doc.cancel()
                frappe.delete_doc(doctype, name, force=1)
                print(f"Deleted {doctype} {name}")
            except Exception as e:
                print(f"Error checking/deleting {doctype} {name}: {e}")

    # 1. Clean up Transactions first (children first usually better but force=1 helps)
    # Payment Request
    cancel_and_delete("Payment Request", {"party": "Test Xendit Customer"})
    
    # Sales Order
    cancel_and_delete("Sales Order", {"customer": "Test Xendit Customer"})
    
    # Quotation
    cancel_and_delete("Quotation", {"party_name": "Test Xendit Customer"})

    # 2. Clean up Master Data
    
    # Delete Addresses linked to customer
    # Need to find them via dynamic link
    addresses = frappe.db.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": "Test Xendit Customer"}, pluck="parent")
    for addr_name in addresses:
        try:
            if frappe.db.exists("Address", addr_name):
                frappe.delete_doc("Address", addr_name, force=1)
                print(f"Deleted Address {addr_name}")
        except Exception as e:
            print(f"Error creating address {addr_name}: {e}")

    # Documents with fixed names/IDs as per test_xendit.py
    docs = [
        ("User", "test_xendit@example.com"),
        ("Customer", "Test Xendit Customer"),
        ("Website Item", "Test Checkout Item"), # Delete Website Item first
        ("Item", "Test Checkout Item"),
        ("Company", "_Test Company"),
        ("Webshop Payment Method", "Virtual Account"),
        ("Xendit Settings", "Xendit Settings"),
    ]

    # Delete Payment Gateway Account via filter
    pga = frappe.db.get_value("Payment Gateway Account", {"payment_gateway": "Xendit"}, "name")
    if pga:
        try:
            frappe.delete_doc("Payment Gateway Account", pga, force=1)
            print(f"Deleted Payment Gateway Account {pga}")
        except Exception as e:
            print(f"Error deleting PGA {pga}: {e}")

    for dt, dn in docs:
        if frappe.db.exists(dt, dn):
            try:
                frappe.delete_doc(dt, dn, force=1)
                print(f"Deleted {dt} {dn}")
            except Exception as e:
                print(f"Error deleting {dt} {dn}: {e}")
                
    frappe.db.commit()
