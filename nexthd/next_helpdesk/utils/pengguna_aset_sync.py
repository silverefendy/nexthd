import frappe


def ambil_info_user(user):
	"""Kembalikan (bagian, kontak) dari User Frappe."""
	if not user:
		return None, None
	info = frappe.db.get_value("User", user, ["department", "phone", "mobile_no"], as_dict=True)
	if not info:
		return None, None
	return info.department or None, info.phone or info.mobile_no or None


def sync_pengguna_aset(doc, method=None):
	"""Hook User.on_update: perbarui bagian dan kontak di semua baris Pengguna Aset."""
	bagian, kontak = ambil_info_user(doc.name)
	frappe.db.sql("UPDATE `tabNextHD Asset User` SET bagian=%s, kontak=%s WHERE user=%s", (bagian, kontak, doc.name))
