import frappe
import subprocess
import json


TRANSACTIONAL_DOCTYPES = [
	"NextHD Ticket",
	"NextHD Problem",
	"NextHD Change Request",
	"NextHD Known Error",
	"NextHD Asset",
	"NextHD Photo",
]

NAMING_PREFIXES = ["TKT-", "PRB-", "CHG-", "AST-", "KE-", "IMG-"]


@frappe.whitelist()
def reset_demo_data(confirm_text=None):
	"""Hapus semua data transaksi NextHD. Hanya System Manager. Backup otomatis dulu."""

	if "System Manager" not in frappe.get_roles(frappe.session.user):
		frappe.throw("Hanya System Manager yang boleh melakukan reset data.")

	if confirm_text != "RESET":
		frappe.throw("Konfirmasi tidak valid. Ketik RESET untuk melanjutkan.")

	from frappe.utils.backups import new_backup
	new_backup(ignore_files=True)

	deleted_summary = {}
	for doctype in TRANSACTIONAL_DOCTYPES:
		count = frappe.db.count(doctype)
		frappe.db.delete(doctype)
		deleted_summary[doctype] = count

	for child_doctype in ["NextHD Photo Link", "NextHD Ticket Waiting Log", "NextHD Problem Ticket"]:
		frappe.db.delete(child_doctype)

	for prefix in NAMING_PREFIXES:
		frappe.db.sql("DELETE FROM `tabSeries` WHERE name LIKE %s", (prefix + "%",))

	frappe.db.commit()
	frappe.clear_cache()

	return deleted_summary


@frappe.whitelist()
def add_reset_shortcut_block():
	"""Tambahkan shortcut tombol reset ke content JSON Workspace NextHD (idempotent)."""
	ws = frappe.get_doc("Workspace", "NextHD")
	content = json.loads(ws.content)

	already_added = any(b.get("id") == "sc-reset-demo" for b in content)

	if already_added:
		return "Sudah ada sebelumnya, tidak ditambah lagi"

	header_block = {
		"id": "hdr-admin",
		"type": "header",
		"data": {"text": '<span class="h4"><b>Admin</b></span>', "col": 12},
	}
	shortcut_block = {
		"id": "sc-reset-demo",
		"type": "shortcut",
		"data": {"shortcut_name": "Reset Data Demo", "col": 3},
	}

	content.append(header_block)
	content.append(shortcut_block)
	frappe.db.set_value("Workspace", "NextHD", "content", json.dumps(content))
	frappe.db.commit()
	return "Berhasil ditambahkan"
