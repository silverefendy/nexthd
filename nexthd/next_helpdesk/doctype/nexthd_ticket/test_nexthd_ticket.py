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

	def test_priority_matrix_tinggi_tinggi(self):
		"""Test priority matrix: impact=Tinggi, urgency=Tinggi -> Kritis"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Tinggi Tinggi",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Tinggi",
			"urgency": "Tinggi"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Kritis")

	def test_priority_matrix_tinggi_rendah(self):
		"""Test priority matrix: impact=Tinggi, urgency=Rendah -> Tinggi"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Tinggi Rendah",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Tinggi",
			"urgency": "Rendah"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Tinggi")

	def test_priority_matrix_rendah_tinggi(self):
		"""Test priority matrix: impact=Rendah, urgency=Tinggi -> Sedang"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Rendah Tinggi",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Rendah",
			"urgency": "Tinggi"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Sedang")

	def test_priority_matrix_rendah_rendah(self):
		"""Test priority matrix: impact=Rendah, urgency=Rendah -> Rendah"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Rendah Rendah",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Rendah",
			"urgency": "Rendah"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Rendah")

	def test_priority_matrix_both_blank(self):
		"""Test priority matrix: both impact and urgency blank -> priority remains default"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Both Blank",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Sedang")

	def test_priority_matrix_only_impact(self):
		"""Test priority matrix: only impact filled -> priority remains default"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Only Impact",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Tinggi"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Sedang")

	def test_priority_matrix_only_urgency(self):
		"""Test priority matrix: only urgency filled -> priority remains default"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Matrix Only Urgency",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"urgency": "Tinggi"
		})
		ticket.insert()
		self.assertEqual(ticket.priority, "Sedang")

	def test_priority_manual_override(self):
		"""Test that manual priority override is preserved"""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"ticket_type": "Insiden",
			"subject": "Test Priority Manual Override",
			"status": "Baru",
			"priority": "Sedang",
			"requested_by": self.requester.name,
			"impact": "Tinggi",
			"urgency": "Tinggi"
		})
		ticket.insert()
		# Initially should be Kritis from matrix
		self.assertEqual(ticket.priority, "Kritis")
		
		# Manually override priority (simulating permlevel-1 write)
		ticket.priority = "Rendah"
		ticket.priority_manually_set = 1
		ticket.save()
		
		# Reload and verify manual override is preserved
		ticket.reload()
		self.assertEqual(ticket.priority, "Rendah")
		
		# Change impact/urgency again - should NOT override manual setting
		ticket.impact = "Rendah"
		ticket.urgency = "Rendah"
		ticket.save()
		
		ticket.reload()
		self.assertEqual(ticket.priority, "Rendah")  # Should still be Rendah, not matrix result
