import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document
from nexthd.next_helpdesk.utils.activity_log import _add_activity_log_entry


class NextHDKnownError(Document):
	def validate(self):
		"""Validate known error before save"""
		for row in self.activity_log:
			if not row.timestamp:  # baris baru dari input manual di grid UI
				row.timestamp = frappe.utils.now()
				row.updated_by = frappe.session.user
				if not row.entry_type:
					row.entry_type = "Manual"
				if row.entry_type == "Manual" and not row.note:
					frappe.throw(_("Catatan wajib diisi untuk entry Manual di Riwayat Aktivitas"))

	def on_update(self):
		"""Handle updates to known error"""
		self.sync_meta_dates()
		# Known Error doesn't have status field, so no auto-log for status changes

	def sync_meta_dates(self):
		if not self.tanggal_dibuat:
			self.db_set("tanggal_dibuat", self.creation, update_modified=False)
		self.db_set("tanggal_diedit", now_datetime(), update_modified=False)
