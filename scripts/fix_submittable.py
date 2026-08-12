"""
Script sekali-pakai: aktifkan is_submittable + submit permission untuk
NextHD Change Request dan NextHD Problem (state "Ditutup" di workflow
kedua doctype ini punya doc_status=1, artinya butuh mekanisme submit).

Cara jalankan di server:
    bench --site desk.ciptamebel.co.id console < scripts/fix_submittable.py

Setelah jalan, boleh dihapus lagi (bukan bagian permanen dari app),
atau dibiarkan sebagai referensi/dokumentasi kalau perlu re-run di
server lain.
"""
import frappe


def run():
    doctypes = ["NextHD Change Request", "NextHD Problem"]

    for dt in doctypes:
        current = frappe.db.get_value("DocType", dt, "is_submittable")
        print(f"{dt} - is_submittable sebelum: {current}")
        frappe.db.set_value("DocType", dt, "is_submittable", 1)

        roles_to_grant = ["Agent", "Agent Manager", "IT Manager"]
        for role in roles_to_grant:
            perm_name = frappe.db.get_value(
                "DocPerm", {"parent": dt, "role": role}, "name"
            )
            if perm_name:
                frappe.db.set_value("DocPerm", perm_name, "submit", 1)
                print(f"{dt} - submit=1 diset untuk role {role} (DocPerm {perm_name})")
            else:
                print(f"{dt} - WARNING: tidak ketemu DocPerm untuk role {role}, skip")

    frappe.db.commit()
    print("DONE")


run()
