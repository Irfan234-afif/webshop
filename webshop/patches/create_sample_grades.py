import frappe

def execute():
    """
    Create sample Grade master data for common school levels.
    This is optional - you can delete or modify based on your school units.
    """
    
    # Get all existing school units
    school_units = frappe.get_all("School Unit", pluck="name")
    
    if not school_units:
        frappe.log_error("No School Units found. Please create School Units first before running this patch.")
        return
    
    # Sample grade templates
    # You can customize this based on your actual school structure
    grade_templates = [
        # TK grades
        {"grade_name": "TK A", "sort_order": 1},
        {"grade_name": "TK B", "sort_order": 2},
        
        # SD grades
        {"grade_name": "SD Kelas 1", "sort_order": 10},
        {"grade_name": "SD Kelas 2", "sort_order": 11},
        {"grade_name": "SD Kelas 3", "sort_order": 12},
        {"grade_name": "SD Kelas 4", "sort_order": 13},
        {"grade_name": "SD Kelas 5", "sort_order": 14},
        {"grade_name": "SD Kelas 6", "sort_order": 15},
        
        # SMP grades
        {"grade_name": "SMP Kelas 7", "sort_order": 20},
        {"grade_name": "SMP Kelas 8", "sort_order": 21},
        {"grade_name": "SMP Kelas 9", "sort_order": 22},
        
        # SMA grades
        {"grade_name": "SMA Kelas 10", "sort_order": 30},
        {"grade_name": "SMA Kelas 11", "sort_order": 31},
        {"grade_name": "SMA Kelas 12", "sort_order": 32},
    ]
    
    created_count = 0
    
    # Create grades for each school unit
    # NOTE: This creates ALL grade levels for ALL units
    # You may want to manually create grades specific to each unit instead
    for unit in school_units:
        for template in grade_templates:
            grade_name = f"{template['grade_name']} - {unit}"
            
            # Check if grade already exists
            if not frappe.db.exists("Grade", grade_name):
                try:
                    grade_doc = frappe.get_doc({
                        "doctype": "Grade",
                        "grade_name": grade_name,
                        "school_unit": unit,
                        "sort_order": template['sort_order'],
                        "enabled": 1
                    })
                    grade_doc.insert(ignore_permissions=True)
                    created_count += 1
                except Exception as e:
                    frappe.log_error(f"Error creating grade {grade_name}: {str(e)}")
    
    frappe.db.commit()
    
    if created_count > 0:
        frappe.msgprint(f"Created {created_count} Grade records successfully.")
