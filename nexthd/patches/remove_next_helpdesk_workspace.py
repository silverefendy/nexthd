import frappe

def execute():
    if frappe.db.exists("Workspace", "Next Helpdesk"):
        frappe.db.delete("Workspace Shortcut", {"parent": "Next Helpdesk"})
        frappe.db.delete("Workspace", {"name": "Next Helpdesk"})
        frappe.db.commit()
        frappe.clear_cache()
        print("OK: Next Helpdesk workspace deleted")
    else:
        print("SKIP: Next Helpdesk not found")
