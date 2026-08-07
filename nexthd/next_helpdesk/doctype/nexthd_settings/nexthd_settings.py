import frappe
from frappe.model.document import Document


class NextHDSettings(Document):
	def get_settings(self):
		"""Get NextHD Settings singleton"""
		return frappe.get_single("NextHD Settings")

	def get_telegram_bot_token(self):
		"""Get Telegram bot token from settings"""
		settings = self.get_settings()
		return settings.telegram_bot_token

	def get_telegram_bot_username(self):
		"""Get Telegram bot username from settings"""
		settings = self.get_settings()
		return settings.telegram_bot_username

	def is_telegram_notification_enabled(self):
		"""Check if Telegram notification is enabled"""
		settings = self.get_settings()
		return settings.enable_telegram_notification
