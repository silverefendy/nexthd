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
	
	Args:
		username: Username user yang akan dibuat
		
	Returns:
		Email dummy yang unique
	"""
	if not username:
		raise ValueError("Username is required")
	
	# Sanitize username: lowercase, remove invalid characters
	sanitized_username = username.lower().strip()
	sanitized_username = ''.join(c for c in sanitized_username if c.isalnum() or c in '._-')
	
	if not sanitized_username:
		raise ValueError("Invalid username after sanitization")
	
	# Generate base email
	base_email = f"{sanitized_username}@{DUMMY_EMAIL_DOMAIN}"
	
	# Check if email already exists, add suffix if needed
	counter = 1
	final_email = base_email
	while frappe.db.exists("User", {"email": final_email}):
		final_email = f"{sanitized_username}{counter}@{DUMMY_EMAIL_DOMAIN}"
		counter += 1
	
	return final_email


def before_insert_user_hook(doc, method):
	"""
	Hook untuk Doctype User, event before_insert.
	Didaftarkan di hooks.py:

		doc_events = {
			"User": {
				"before_insert": "nexthd.next_helpdesk.utils.email_helper.before_insert_user_hook"
			}
		}
	
	Auto-generate email dummy jika email kosong dan username tersedia.
	"""
	# Only generate dummy email if email is empty and username is provided
	if not doc.email and doc.username:
		try:
			doc.email = generate_dummy_email(doc.username)
			doc.send_welcome_email = 0  # Disable welcome email since email is dummy
		except ValueError as e:
			frappe.log_error(f"Failed to generate dummy email for user {doc.username}: {str(e)}")
			raise
