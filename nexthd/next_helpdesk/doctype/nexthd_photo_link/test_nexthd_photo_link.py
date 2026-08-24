import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDPhotoLink(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create test user
		if not frappe.db.exists("User", "test_link_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_link_user@example.com",
				"first_name": "Test",
				"last_name": "Link User",
				"username": "testlinkuser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_link_user@example.com")

		# Create test photo
		if not frappe.db.exists("NextHD Photo", {"caption": "Test Photo for Link"}):
			self.test_photo = frappe.get_doc({
				"doctype": "NextHD Photo",
				"caption": "Test Photo for Link"
			})
			self.test_photo.insert()
		else:
			self.test_photo = frappe.get_doc("NextHD Photo", {"caption": "Test Photo for Link"})

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Ticket", {"subject": ["like", "%Test Link%"]})
		frappe.db.delete("NextHD Photo", {"caption": ["like", "%Test Photo for Link%"]})

	def test_create_photo_link(self):
		"""Test creating a photo link"""
		# Create a test ticket to attach photo link to
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Link Ticket",
			"description": "Test for photo link",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.test_user.name
		})
		ticket.insert()

		# Add photo link
		photo_link = frappe.get_doc({
			"doctype": "NextHD Photo Link",
			"parenttype": "NextHD Ticket",
			"parent": ticket.name,
			"parentfield": "photos",
			"photo": self.test_photo.name
		})
		photo_link.insert()
		self.assertEqual(photo_link.photo, self.test_photo.name)

	def test_photo_link_fetch(self):
		"""Test that photo_link fetches from photo correctly"""
		self.test_photo.caption = "Fetched Caption"
		self.test_photo.save()

		photo_link = frappe.get_doc({
			"doctype": "NextHD Photo Link",
			"photo": self.test_photo.name
		})
		photo_link.insert()
		
		# After insert, caption should be fetched from photo
		self.assertEqual(photo_link.caption, "Fetched Caption")
