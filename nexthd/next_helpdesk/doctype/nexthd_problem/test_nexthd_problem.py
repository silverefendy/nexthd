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
