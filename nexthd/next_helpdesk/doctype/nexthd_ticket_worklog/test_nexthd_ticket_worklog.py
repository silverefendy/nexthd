import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDTicketWorklog(FrappeTestCase):
	def test_worklog_row_can_be_added_and_saved(self):
		"""Baris worklog baru bisa ditambahkan ke tiket dan tersimpan."""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"subject": "Test Worklog - Komputer Mati",
			"ticket_type": "Insiden",
			"requested_by": frappe.session.user,
		}).insert()

		ticket.append("worklog", {
			"aktivitas": "Cek dan lepas HDD, tidak ada perubahan",
			"hasil": "Belum Berhasil",
			"durasi_menit": 15,
		})
		ticket.save()

		ticket.reload()
		self.assertEqual(len(ticket.worklog), 1)
		self.assertEqual(ticket.worklog[0].aktivitas, "Cek dan lepas HDD, tidak ada perubahan")
		self.assertEqual(ticket.worklog[0].hasil, "Belum Berhasil")

		# cleanup
		frappe.delete_doc("NextHD Ticket", ticket.name, force=True)

	def test_worklog_requires_aktivitas(self):
		"""Baris worklog tanpa field 'aktivitas' (wajib) harus ditolak saat save."""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"subject": "Test Worklog - Validasi Wajib",
			"ticket_type": "Insiden",
			"requested_by": frappe.session.user,
		}).insert()

		ticket.append("worklog", {
			"hasil": "Berhasil",
		})

		with self.assertRaises(frappe.MandatoryError):
			ticket.save()

		frappe.delete_doc("NextHD Ticket", ticket.name, force=True)

	def test_multiple_worklog_entries_preserve_order(self):
		"""Beberapa baris worklog tersimpan dan urut sesuai input."""
		ticket = frappe.get_doc({
			"doctype": "NextHD Ticket",
			"subject": "Test Worklog - Multi Entry",
			"ticket_type": "Insiden",
			"requested_by": frappe.session.user,
		}).insert()

		ticket.append("worklog", {"aktivitas": "Langkah 1: cek HDD", "hasil": "Belum Berhasil"})
		ticket.append("worklog", {"aktivitas": "Langkah 2: cek VGA", "hasil": "Berhasil"})
		ticket.save()

		ticket.reload()
		self.assertEqual(len(ticket.worklog), 2)
		self.assertEqual(ticket.worklog[0].aktivitas, "Langkah 1: cek HDD")
		self.assertEqual(ticket.worklog[1].aktivitas, "Langkah 2: cek VGA")

		frappe.delete_doc("NextHD Ticket", ticket.name, force=True)
