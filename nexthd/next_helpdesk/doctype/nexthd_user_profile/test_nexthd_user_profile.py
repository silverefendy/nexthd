import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDUserProfile(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test user
		if not frappe.db.exists("User", "test_profile_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_profile_user@example.com",
				"first_name": "Test",
				"last_name": "Profile User",
				"username": "testprofileuser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_profile_user@example.com")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD User Profile", {"user": self.test_user.name})

	def test_create_user_profile(self):
		"""Test creating a user profile"""
		profile = frappe.get_doc({
			"doctype": "NextHD User Profile",
			"user": self.test_user.name,
			"preferred_language": "ID",
			"department": "IT"
		})
		profile.insert()
		self.assertEqual(profile.user, self.test_user.name)
		self.assertEqual(profile.preferred_language, "ID")

	def test_telegram_linking(self):
		"""Test linking Telegram account"""
		profile = frappe.get_doc({
			"doctype": "NextHD User Profile",
			"user": self.test_user.name,
			"telegram_chat_id": "123456789",
			"telegram_username": "testuser_telegram"
		})
		profile.insert()
		self.assertTrue(profile.is_telegram_linked())
		self.assertEqual(profile.get_telegram_chat_id(), "123456789")

	def test_unique_user(self):
		"""Test that user must be unique"""
		profile1 = frappe.get_doc({
			"doctype": "NextHD User Profile",
			"user": self.test_user.name
		})
		profile1.insert()

		profile2 = frappe.get_doc({
			"doctype": "NextHD User Profile",
			"user": self.test_user.name
		})
		with self.assertRaises(frappe.ValidationError):
			profile2.insert()

	def test_default_language(self):
		"""Test default language is ID"""
		profile = frappe.get_doc({
			"doctype": "NextHD User Profile",
			"user": self.test_user.name
		})
		profile.insert()
		self.assertEqual(profile.preferred_language, "ID")
