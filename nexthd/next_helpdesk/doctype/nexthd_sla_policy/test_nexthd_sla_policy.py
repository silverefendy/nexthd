import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDSLAPolicy(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test business hours
		if not frappe.db.exists("NextHD Business Hours", "Senin"):
			self.business_hours = frappe.get_doc({
				"doctype": "NextHD Business Hours",
				"day": "Senin",
				"start_time": "08:00:00",
				"end_time": "17:00:00",
				"is_working_day": 1
			})
			self.business_hours.insert()
		else:
			self.business_hours = frappe.get_doc("NextHD Business Hours", "Senin")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD SLA Policy", {"priority": ["like", "%"]})

	def test_create_sla_policy(self):
		"""Test creating an SLA policy"""
		policy = frappe.get_doc({
			"doctype": "NextHD SLA Policy",
			"priority": "Kritis",
			"response_time_minutes": 15,
			"resolution_time_minutes": 120,
			"business_hours": self.business_hours.name
		})
		policy.insert()
		self.assertEqual(policy.priority, "Kritis")
		self.assertEqual(policy.response_time_minutes, 15)

	def test_unique_priority(self):
		"""Test that priorities must be unique"""
		policy1 = frappe.get_doc({
			"doctype": "NextHD SLA Policy",
			"priority": "Tinggi",
			"response_time_minutes": 60,
			"resolution_time_minutes": 240,
			"business_hours": self.business_hours.name
		})
		policy1.insert()

		policy2 = frappe.get_doc({
			"doctype": "NextHD SLA Policy",
			"priority": "Tinggi",
			"response_time_minutes": 60,
			"resolution_time_minutes": 240,
			"business_hours": self.business_hours.name
		})
		with self.assertRaises(frappe.UniqueValidationError):
			policy2.insert()

	def test_required_fields(self):
		"""Test that required fields are validated"""
		policy = frappe.get_doc({
			"doctype": "NextHD SLA Policy",
			"priority": "Sedang"
		})
		with self.assertRaises(frappe.MandatoryError):
			policy.insert()
