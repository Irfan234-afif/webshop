import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Item" : [
            {
                "fieldname": "school_unit",
                "fieldtype": "Link",
                "label": "School Unit",
                "description": "For grouping the categories",
                "options": "School Unit",
                "insert_after": "item_group"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)