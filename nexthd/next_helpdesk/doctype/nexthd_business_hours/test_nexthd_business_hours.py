import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDBusinessHours(FrappeTestCase):
	def setUp(self):
		super().setUp()
		frappe.db.delete("NextHD Business Hours", {"day": "Senin"})

	def test_create_business_hours(self):
		"""Test creating business hours"""
		bh = frappe.get_doc({
			"doctype": "NextHD Business Hours",
			"day": "Senin",
			"start_time": "08:00:00",
			"end_time": "17:00:00",
			"is_working_day": 1
		})
		bh.insert()
		self.assertEqual(bh.day, "Senin")
		self.assertEqual(bh.is_working_day, 1)

	def test_non_working_day(self):
		"""Test creating a non-working day"""
		bh = frappe.get_doc({
			"doctype": "NextHD Business Hours",
			"day": "Minggu",
			"is_working_day": 0
		})
		bh.insert()
		self.assertEqual(bh.is_working_day, 0)

	def test_unique_day(self):
		"""Test that days must be unique"""
		bh1 = frappe.get_doc({
			"doctype": "NextHD Business Hours",
			"day": "Senin"
		})
		bh1.insert()

		bh2 = frappe.get_doc({
			"doctype": "NextHD Business Hours",
			"day": "Senin"
		})
		with self.assertRaises(frappe.UniqueValidationError):
			bh2.insert()

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Business Hours", {"day": ["like", "%"]})
