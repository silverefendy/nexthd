import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDChangeRequest(FrappeTestCase):
	def setUp(self):
		super().setUp()

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Change Request", {"title": ["like", "%Test%"]})

	def test_create_change_request(self):
		"""Test creating a basic change request"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Change Request",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.insert()
		self.assertEqual(cr.title, "Test Change Request")
		self.assertEqual(cr.status, "Draft")
		self.assertTrue(cr.name.startswith("CHG-2026-"))

	def test_change_request_with_plans(self):
		"""Test creating a change request with implementation and rollback plans"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Change Request with Plans",
			"status": "Draft",
			"change_type": "Standard",
			"risk_level": "Rendah",
			"implementation_plan": "Step 1: Backup\nStep 2: Apply patch\nStep 3: Verify",
			"rollback_plan": "Step 1: Restore backup\nStep 2: Revert changes"
		})
		cr.insert()
		self.assertIsNotNone(cr.implementation_plan)
		self.assertIsNotNone(cr.rollback_plan)

	def test_emergency_change(self):
		"""Test creating an emergency change request"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Emergency Change Request",
			"status": "Draft",
			"change_type": "Emergency",
			"risk_level": "Tinggi"
		})
		cr.insert()
		self.assertEqual(cr.change_type, "Emergency")
		self.assertEqual(cr.risk_level, "Tinggi")

	def test_status_transition(self):
		"""Test status change from Draft to Diajukan"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Status Change Request",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.insert()
		
		cr.status = "Diajukan"
		cr.save()
		self.assertEqual(cr.status, "Diajukan")

	def test_change_type_options(self):
		"""Test different change types"""
		change_types = ["Standard", "Normal", "Emergency"]
		for change_type in change_types:
			cr = frappe.get_doc({
				"doctype": "NextHD Change Request",
				"title": f"Test {change_type} Change",
				"status": "Draft",
				"change_type": change_type,
				"risk_level": "Sedang"
			})
			cr.insert()
			self.assertEqual(cr.change_type, change_type)

	def test_risk_level_options(self):
		"""Test different risk levels"""
		risk_levels = ["Rendah", "Sedang", "Tinggi"]
		for risk_level in risk_levels:
			cr = frappe.get_doc({
				"doctype": "NextHD Change Request",
				"title": f"Test {risk_level} Risk Change",
				"status": "Draft",
				"change_type": "Normal",
				"risk_level": risk_level
			})
			cr.insert()
			self.assertEqual(cr.risk_level, risk_level)
