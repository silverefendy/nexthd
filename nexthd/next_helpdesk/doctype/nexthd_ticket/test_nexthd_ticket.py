import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import datetime


class TestNextHDTicket(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create test users
		if not frappe.db.exists("User", "test_requester@example.com"):
			self.requester = frappe.get_doc({
				"doctype": "User",
				"email": "test_requester@example.com",
				"first_name": "Test",
				"last_name": "Requester",
				"username": "testrequester"
			})
			self.requester.insert()
		else:
			self.requester = frappe.get_doc("User", "test_requester@example.com")

		if not frappe.db.exists("User", "test_agent@example.com"):
			self.agent = frappe.get_doc({
				"doctype": "User",
				"email": "test_agent@example.com",
				"first_name": "Test",
				"last_name": "Agent",
				"username": "testagent"
			})
			self.agent.insert()
		else:
			self.agent = frappe.get_doc("User", "test_agent@example.com")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Ticket", {"subject": ["like", "%Test%"]})

	def test_create_ticket(self):
		"""Test creating a basic ticket"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Ticket",
			"description": "This is a test ticket",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name
		})
		ticket.insert()
		self.assertEqual(ticket.subject, "Test Ticket")
		self.assertEqual(ticket.status, "Baru")
		self.assertTrue(ticket.name.startswith("TKT-2026-"))

	def test_ticket_assignment(self):
		"""Test assigning a ticket to an agent"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Assignment Ticket",
			"status": "Baru",
			"priority": "Tinggi",
			"requested_by": self.requester.name,
			"assigned_to": self.agent.name
		})
		ticket.insert()
		self.assertEqual(ticket.assigned_to, self.agent.name)

	def test_status_change_to_resolved(self):
		"""Test status change to resolved updates timestamp"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Status Ticket",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name
		})
		ticket.insert()
		
		ticket.status = "Selesai"
		ticket.save()
		self.assertIsNotNone(ticket.resolved_on)

	def test_status_change_to_closed(self):
		"""Test status change to closed updates timestamp"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Close Ticket",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name
		})
		ticket.insert()
		
		ticket.status = "Ditutup"
		ticket.save()
		self.assertIsNotNone(ticket.closed_on)

	def test_invalid_assigned_user(self):
		"""Test that invalid assigned user raises error"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Invalid User Ticket",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"assigned_to": "nonexistent_user"
		})
		with self.assertRaises(frappe.ValidationError):
			ticket.insert()

	def test_ticket_type_options(self):
		"""Test ticket type options"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Permintaan Layanan",
			"subject": "Test Service Request",
			"status": "Baru",
			"priority": "Rendah",
			"requested_by": self.requester.name
		})
		ticket.insert()
		self.assertEqual(ticket.ticket_type, "Permintaan Layanan")
