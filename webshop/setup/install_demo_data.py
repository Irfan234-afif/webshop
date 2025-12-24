
import frappe
import json
import os

def install_demo_data():
    create_attributes()
    create_item_group()
    create_items()
    frappe.db.commit()
    print("Webshop Demo Data Installed Successfully")

def create_attributes():
    attributes = ["Size", "Color"]
    for attr in attributes:
        if attr == "Size":
            values = ["Small", "Medium", "Large", "Extra Large", "8", "9", "10"]
        elif attr == "Color":
            values = ["Red", "Blue", "Black", "Grey", "White"]

        if not frappe.db.exists("Item Attribute", attr):
            doc = frappe.new_doc("Item Attribute")
            doc.attribute_name = attr
            doc.item_attribute_values = []
            for val in values:
                doc.append("item_attribute_values", {"attribute_value": val, "abbr": val[:3].upper()})
            doc.insert(ignore_permissions=True)
            print(f"Created Item Attribute: {attr}")
        else:
            doc = frappe.get_doc("Item Attribute", attr)
            existing_values = [d.attribute_value for d in doc.item_attribute_values]
            modified = False
            for val in values:
                if val not in existing_values:
                    doc.append("item_attribute_values", {"attribute_value": val, "abbr": val[:3].upper()})
                    modified = True
            
            if modified:
                doc.save(ignore_permissions=True)
                print(f"Updated Item Attribute: {attr}")

def create_item_group():
    if not frappe.db.exists("Item Group", "Demo Item Group"):
        doc = frappe.new_doc("Item Group")
        doc.item_group_name = "Demo Item Group"
        doc.parent_item_group = "All Item Groups"
        doc.is_group = 0
        doc.insert(ignore_permissions=True)
        print("Created Item Group: Demo Item Group")

def create_items():
    file_path = os.path.join(os.path.dirname(__file__), "demo_data", "item.json")
    with open(file_path, "r") as f:
        items = json.load(f)

    for item_data in items:
        if not frappe.db.exists("Item", item_data.get("item_code")):
            doc = frappe.get_doc(item_data)
            doc.insert(ignore_permissions=True)
            print(f"Created Item: {item_data.get('item_code')}")
        else:
            print(f"Item already exists: {item_data.get('item_code')}")

if __name__ == "__main__":
    frappe.init(site="development.localhost", sites_path=os.path.join(os.getcwd(), "sites"))
    frappe.connect()
    install_demo_data()
