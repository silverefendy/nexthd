import frappe
from frappe.utils import now_datetime
from frappe.model.document import Document


class NextHDAsset(Document):
	def validate(self):
		"""Validate asset before save"""
		self.validate_warranty_dates()
		self.isi_info_pengguna()

	def validate_warranty_dates(self):
		"""Validate warranty dates"""
		if self.purchase_date and self.warranty_until:
			if self.warranty_until < self.purchase_date:
				frappe.throw("Warranty Until date cannot be before Purchase Date")

	def isi_info_pengguna(self):
		"""Isi bagian dan kontak tiap Pengguna Aset dari NextHD User Profile"""
		for row in self.get("asset_users") or []:
			prof = None
			if row.user:
				prof = frappe.db.get_value("NextHD User Profile", {"user": row.user}, ["department", "phone_internal"], as_dict=True)
			row.bagian = prof.department if prof else None
			row.kontak = prof.phone_internal if prof else None

	def on_update(self):
		"""Handle updates to asset"""
		self.sync_meta_dates()

	def sync_meta_dates(self):
		if not self.tanggal_dibuat:
			self.db_set("tanggal_dibuat", self.creation, update_modified=False)
		self.db_set("tanggal_diedit", now_datetime(), update_modified=False)
