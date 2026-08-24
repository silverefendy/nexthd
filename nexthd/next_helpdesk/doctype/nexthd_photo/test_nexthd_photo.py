import frappe
from frappe.tests.utils import FrappeTestCase
import os


class TestNextHDPhoto(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create test user
		if not frappe.db.exists("User", "test_photo_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_photo_user@example.com",
				"first_name": "Test",
				"last_name": "Photo User",
				"username": "testphotouser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_photo_user@example.com")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Photo", {"caption": ["like", "%Test%"]})

	def test_create_photo(self):
		"""Test creating a basic photo record"""
		photo = frappe.get_doc({
			"doctype": "NextHD Photo",
			"caption": "Test Photo"
		})
		# Note: Actual image upload requires file handling, this tests the basic creation
		photo.insert()
		self.assertEqual(photo.caption, "Test Photo")
		self.assertEqual(photo.uploaded_by, frappe.session.user)
		self.assertIsNotNone(photo.uploaded_on)

	def test_auto_fill_uploaded_by(self):
		"""Test that uploaded_by is auto-filled"""
		photo = frappe.get_doc({
			"doctype": "NextHD Photo",
			"caption": "Auto Fill Test"
		})
		photo.insert()
		self.assertEqual(photo.uploaded_by, frappe.session.user)

	def test_auto_fill_uploaded_on(self):
		"""Test that uploaded_on is auto-filled"""
		photo = frappe.get_doc({
			"doctype": "NextHD Photo",
			"caption": "Auto Date Test"
		})
		photo.insert()
		self.assertIsNotNone(photo.uploaded_on)
