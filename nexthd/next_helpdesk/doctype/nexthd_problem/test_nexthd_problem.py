import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDProblem(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test ticket
		if not frappe.db.exists("User", "test_problem_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_problem_user@example.com",
				"first_name": "Test",
				"last_name": "Problem User",
				"username": "testproblemuser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_problem_user@example.com")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Problem", {"title": ["like", "%Test%"]})
		frappe.db.delete("NextHD Ticket", {"subject": ["like", "%Problem%"]})

	def test_create_problem(self):
		"""Test creating a basic problem"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Problem",
			"status": "Terbuka"
		})
		problem.insert()
		self.assertEqual(problem.title, "Test Problem")
		self.assertEqual(problem.status, "Terbuka")
		self.assertTrue(problem.name.startswith("PRB-2026-"))

	def test_problem_with_root_cause(self):
		"""Test creating a problem with root cause"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Problem with Root Cause",
			"status": "Selesai",
			"root_cause": "This is the root cause of the problem"
		})
		problem.insert()
		self.assertEqual(problem.root_cause, "This is the root cause of the problem")

	def test_problem_with_related_tickets(self):
		"""Test creating a problem with related tickets"""
		# Create a test ticket first
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Problem Test Ticket",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.test_user.name
		})
		ticket.insert()

		# Create problem with related ticket
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Problem with Tickets",
			"status": "Investigasi"
		})
		problem.append("related_tickets", {
			"ticket": ticket.name
		})
		problem.insert()
		self.assertEqual(len(problem.related_tickets), 1)
		self.assertEqual(problem.related_tickets[0].ticket, ticket.name)

	def test_status_transition(self):
		"""Test status change"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Status Problem",
			"status": "Terbuka"
		})
		problem.insert()
		
		problem.status = "Investigasi"
		problem.save()
		self.assertEqual(problem.status, "Investigasi")

	def test_known_error_status(self):
		"""Test Known Error status"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Known Error",
			"status": "Known Error"
		})
		problem.insert()
		self.assertEqual(problem.status, "Known Error")

	def test_activity_log_auto_status_change(self):
		"""Test auto-logging of status changes"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Activity Log Status",
			"status": "Terbuka"
		})
		problem.insert()
		
		# Change status to trigger auto-log
		problem.status = "Investigasi"
		problem.save()
		
		# Reload to get activity_log from DB
		problem.reload()
		self.assertEqual(len(problem.activity_log), 1)
		self.assertEqual(problem.activity_log[0].entry_type, "Otomatis")
		self.assertEqual(problem.activity_log[0].status_from, "Terbuka")
		self.assertEqual(problem.activity_log[0].status_to, "Investigasi")
		self.assertIn("Status berubah dari Terbuka ke Investigasi", problem.activity_log[0].note)

	def test_activity_log_manual_entry(self):
		"""Test manual activity log entry"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Manual Activity Log",
			"status": "Terbuka"
		})
		problem.append("activity_log", {
			"note": "Catatan manual dari agent"
		})
		problem.insert()
		
		problem.reload()
		self.assertEqual(len(problem.activity_log), 1)
		self.assertEqual(problem.activity_log[0].entry_type, "Manual")
		self.assertEqual(problem.activity_log[0].note, "Catatan manual dari agent")
		self.assertIsNotNone(problem.activity_log[0].timestamp)
		self.assertIsNotNone(problem.activity_log[0].updated_by)

	def test_activity_log_manual_requires_note(self):
		"""Test that manual entry requires note"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Manual No Note",
			"status": "Terbuka"
		})
		problem.append("activity_log", {
			"entry_type": "Manual"
		})
		
		with self.assertRaises(frappe.ValidationError):
			problem.insert()

	def test_activity_log_no_infinite_recursion(self):
		"""Test that status change doesn't cause infinite recursion"""
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test No Recursion",
			"status": "Terbuka"
		})
		problem.insert()
		
		# Change status multiple times
		problem.status = "Investigasi"
		problem.save()
		problem.reload()
		
		problem.status = "Selesai"
		problem.save()
		problem.reload()
		
		# Should have exactly 2 log entries (one for each status change)
		self.assertEqual(len(problem.activity_log), 2)
