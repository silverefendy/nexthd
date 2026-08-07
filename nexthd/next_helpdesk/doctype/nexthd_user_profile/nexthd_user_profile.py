import frappe
from frappe.model.document import Document


class NextHDUserProfile(Document):
	def validate(self):
		"""Validate that user is unique"""
		if self.user:
			# Check if another profile exists for this user
			existing = frappe.db.exists("NextHD User Profile", {"user": self.user})
			if existing and existing != self.name:
				frappe.throw(f"User Profile already exists for user {self.user}")

	def on_update(self):
		"""Auto-create User Profile if it doesn't exist when User is created"""
		pass

	def get_telegram_chat_id(self):
		"""Get Telegram chat ID for this user profile"""
		return self.telegram_chat_id

	def is_telegram_linked(self):
		"""Check if Telegram account is linked"""
		return bool(self.telegram_chat_id)
