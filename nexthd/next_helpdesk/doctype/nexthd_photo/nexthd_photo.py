import frappe
from frappe.model.document import Document


class NextHDPhoto(Document):
	def before_insert(self):
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
		if not self.uploaded_on:
			self.uploaded_on = frappe.utils.now()


def get_dashboard_data(data):
	"""Tampilkan semua Ticket/Asset/Problem/Known Error yang memakai foto ini.
	Query balik lewat child table 'photos' (NextHD Photo Link) - bukan field tersimpan,
	jadi selalu akurat walau 1 foto dipakai di banyak dokumen."""
	return {
		"fieldname": "photo",
		"non_standard_fieldnames": {
			"NextHD Ticket": "photos",
			"NextHD Asset": "photos",
			"NextHD Problem": "photos",
			"NextHD Known Error": "photos",
		},
		"transactions": [
			{
				"label": "Dipakai Di",
				"items": ["NextHD Ticket", "NextHD Asset", "NextHD Problem", "NextHD Known Error"],
			}
		],
	}
