import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Item" : [
            {
                "fieldname": "grade",
                "fieldtype": "Link",
                "label": "Kelas/Grade",
                "description": "Grade level for this item",
                "options": "Grade",
                "insert_after": "school_unit"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
