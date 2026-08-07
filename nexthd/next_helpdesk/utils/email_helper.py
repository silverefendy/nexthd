"""
NextHD - Email Helper Utility

Menangani generate email dummy untuk user tanpa email asli.
Referensi: NEXTHD_SPEC.md bagian 4

STATUS: SKELETON - belum diimplementasikan, untuk Devin
"""

import frappe

DUMMY_EMAIL_DOMAIN = "noemail.internal"


def generate_dummy_email(username: str) -> str:
	"""
	Generate email dummy dari username.
	Format: {username}@noemail.internal

	TODO (Devin):
	- Pastikan hasil selalu unique (cek dulu ke DB, kalau collision tambahkan suffix)
	- Sanitize username (lowercase, hapus karakter tidak valid untuk email)
	"""
	raise NotImplementedError


def before_insert_user_hook(doc, method):
	"""
	Hook untuk Doctype User, event before_insert.
	Didaftarkan di hooks.py:

		doc_events = {
			"User": {
				"before_insert": "nexthd.next_helpdesk.utils.email_helper.before_insert_user_hook"
			}
		}

	TODO (Devin):
	- Kalau doc.email kosong DAN ada context bahwa user ini dibuat dari
	  form NextHD (bukan dari Administrator/System Manager buat user biasa),
	  auto-isi doc.email dengan generate_dummy_email(doc.username)
	- Set doc.send_welcome_email = 0
	"""
	pass
