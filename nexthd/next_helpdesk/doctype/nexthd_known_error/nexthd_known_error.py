import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document


class NextHDKnownError(Document):
	def validate(self):
		"""Validate known error before save"""
		pass

	def on_update(self):
		"""Handle updates to known error"""
		self.sync_meta_dates()

	def sync_meta_dates(self):
		if not self.tanggal_dibuat:
			self.db_set("tanggal_dibuat", self.creation, update_modified=False)
		self.db_set("tanggal_diedit", now_datetime(), update_modified=False)
