import frappe
doctypes = ["NextHD Change Request", "NextHD Problem"]
for dt in doctypes:
    current = frappe.db.get_value("DocType", dt, "is_submittable")
    print(dt + " - is_submittable sebelum: " + str(current))
    frappe.db.set_value("DocType", dt, "is_submittable", 1)
    roles_to_grant = ["Agent", "Agent Manager", "IT Manager"]
    for role in roles_to_grant:
        perm_name = frappe.db.get_value("DocPerm", {"parent": dt, "role": role}, "name")
        if perm_name:
            frappe.db.set_value("DocPerm", perm_name, "submit", 1)
            print(dt + " - submit=1 diset untuk role " + role + " (DocPerm " + str(perm_name) + ")")
        else:
            print(dt + " - WARNING: tidak ketemu DocPerm untuk role " + role + ", skip")
frappe.db.commit()
print("DONE")
