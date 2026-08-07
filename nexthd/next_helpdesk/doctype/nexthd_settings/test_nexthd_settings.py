import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDSettings(FrappeTestCase):
	def test_get_settings(self):
		"""Test getting NextHD Settings singleton"""
		settings = frappe.get_single("NextHD Settings")
		self.assertEqual(settings.doctype, "NextHD Settings")

	def test_set_telegram_bot_token(self):
		"""Test setting Telegram bot token"""
		settings = frappe.get_single("NextHD Settings")
		settings.telegram_bot_token = "test_token_12345"
		settings.save()
		
		reloaded = frappe.get_single("NextHD Settings")
		self.assertEqual(reloaded.telegram_bot_token, "test_token_12345")

	def test_set_telegram_bot_username(self):
		"""Test setting Telegram bot username"""
		settings = frappe.get_single("NextHD Settings")
		settings.telegram_bot_username = "test_bot"
		settings.save()
		
		reloaded = frappe.get_single("NextHD Settings")
		self.assertEqual(reloaded.telegram_bot_username, "test_bot")

	def test_enable_telegram_notification(self):
		"""Test enabling/disabling Telegram notification"""
		settings = frappe.get_single("NextHD Settings")
		settings.enable_telegram_notification = 1
		settings.save()
		
		reloaded = frappe.get_single("NextHD Settings")
		self.assertEqual(reloaded.enable_telegram_notification, 1)

	def test_default_language(self):
		"""Test default language setting"""
		settings = frappe.get_single("NextHD Settings")
		self.assertEqual(settings.default_language, "ID")
