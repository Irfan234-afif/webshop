
import frappe
from frappe.utils import set_request

frappe.init(site="development.localhost")
frappe.connect()

try:
    so = frappe.new_doc('Sales Order')
    so.company = '_Test Company'
    so.customer = '_Test Customer'
    so.insert()
    print(f"Status before: {so.status}, docstatus: {so.docstatus}")
    try:
        so.cancel()
        print(f"Status after: {so.status}, docstatus: {so.docstatus}")
    except Exception as e:
        print(f"Cancel failed as expected: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.db.rollback()
    frappe.destroy()
