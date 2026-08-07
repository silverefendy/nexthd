import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDServiceCatalog(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test SLA policy
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

		if not frappe.db.exists("NextHD SLA Policy", "Sedang"):
			self.sla_policy = frappe.get_doc({
				"doctype": "NextHD SLA Policy",
				"priority": "Sedang",
				"response_time_minutes": 240,
				"resolution_time_minutes": 480,
				"business_hours": self.business_hours.name
			})
			self.sla_policy.insert()
		else:
			self.sla_policy = frappe.get_doc("NextHD SLA Policy", "Sedang")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Service Catalog", {"service_name": ["like", "%Test%"]})

	def test_create_service_catalog(self):
		"""Test creating a basic service catalog"""
		sc = frappe.get_doc({
			"doctype": "NextHD Service Catalog",
			"service_name": "Test Service",
			"category": "Hardware"
		})
		sc.insert()
		self.assertEqual(sc.service_name, "Test Service")
		self.assertEqual(sc.category, "Hardware")
		self.assertTrue(sc.name.startswith("SVC-2026-"))

	def test_service_catalog_with_description(self):
		"""Test creating a service catalog with description"""
		sc = frappe.get_doc({
			"doctype": "NextHD Service Catalog",
			"service_name": "Test Service with Description",
			"category": "Software",
			"description": "This service provides software installation and support"
		})
		sc.insert()
		self.assertEqual(sc.description, "This service provides software installation and support")

	def test_service_catalog_with_default_sla(self):
		"""Test creating a service catalog with default SLA"""
		sc = frappe.get_doc({
			"doctype": "NextHD Service Catalog",
			"service_name": "Test Service with SLA",
			"category": "Network",
			"default_sla": self.sla_policy.name
		})
		sc.insert()
		self.assertEqual(sc.default_sla, self.sla_policy.name)

	def test_category_options(self):
		"""Test different category options"""
		categories = ["Hardware", "Software", "Network", "Access", "Email", "Printer", "Other"]
		for category in categories:
			sc = frappe.get_doc({
				"doctype": "NextHD Service Catalog",
				"service_name": f"Test {category} Service",
				"category": category
			})
			sc.insert()
			self.assertEqual(sc.category, category)
