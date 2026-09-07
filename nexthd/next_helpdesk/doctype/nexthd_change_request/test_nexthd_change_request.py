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

	def test_activity_log_auto_status_change(self):
		"""Test auto-logging of status changes"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Activity Log Status",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.insert()
		
		# Change status to trigger auto-log
		cr.status = "Diajukan"
		cr.save()
		
		# Reload to get activity_log from DB
		cr.reload()
		self.assertEqual(len(cr.activity_log), 1)
		self.assertEqual(cr.activity_log[0].entry_type, "Otomatis")
		self.assertEqual(cr.activity_log[0].status_from, "Draft")
		self.assertEqual(cr.activity_log[0].status_to, "Diajukan")
		self.assertIn("Status berubah dari Draft ke Diajukan", cr.activity_log[0].note)

	def test_activity_log_manual_entry(self):
		"""Test manual activity log entry"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Manual Activity Log",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.append("activity_log", {
			"note": "Catatan manual dari agent"
		})
		cr.insert()
		
		cr.reload()
		self.assertEqual(len(cr.activity_log), 1)
		self.assertEqual(cr.activity_log[0].entry_type, "Manual")
		self.assertEqual(cr.activity_log[0].note, "Catatan manual dari agent")
		self.assertIsNotNone(cr.activity_log[0].timestamp)
		self.assertIsNotNone(cr.activity_log[0].updated_by)

	def test_activity_log_manual_requires_note(self):
		"""Test that manual entry requires note"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test Manual No Note",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.append("activity_log", {
			"entry_type": "Manual"
		})
		
		with self.assertRaises(frappe.ValidationError):
			cr.insert()

	def test_activity_log_no_infinite_recursion(self):
		"""Test that status change doesn't cause infinite recursion"""
		cr = frappe.get_doc({
			"doctype": "NextHD Change Request",
			"title": "Test No Recursion",
			"status": "Draft",
			"change_type": "Normal",
			"risk_level": "Sedang"
		})
		cr.insert()
		
		# Change status multiple times
		cr.status = "Diajukan"
		cr.save()
		cr.reload()
		
		cr.status = "Direview"
		cr.save()
		cr.reload()
		
		# Should have exactly 2 log entries (one for each status change)
		self.assertEqual(len(cr.activity_log), 2)
