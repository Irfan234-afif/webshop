import frappe


def execute(doc, method=None):
    """Update Website Item if change in Item impacts it."""
    web_item = frappe.db.exists("Website Item", {"item_code": doc.item_code})

    if web_item:
        changed = {}
        editable_fields = [
            "item_name",
            "item_group",
            "stock_uom",
            "brand",
            "description",
            "disabled",
        ]
        doc_before_save = doc.get_doc_before_save()

        for field in editable_fields:
            old_value = doc_before_save.get(field) if doc_before_save else None
            new_value = doc.get(field)
            
            if old_value != new_value:
                if field == "disabled":
                    changed["published"] = not doc.get(field)
                else:
                    changed[field] = doc.get(field)

                if not changed:
                    return

                web_item_doc = frappe.get_doc("Website Item", web_item)
                web_item_doc.update(changed)
                web_item_doc.save()
