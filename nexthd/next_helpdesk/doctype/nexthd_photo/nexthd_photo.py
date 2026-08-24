import frappe
from frappe.model.document import Document


class NextHDPhoto(Document):
	def before_insert(self):
		if not self.uploaded_by:
			self.uploaded_by = frappe.session.user
		if not self.uploaded_on:
			self.uploaded_on = frappe.utils.now()
