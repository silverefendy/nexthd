import frappe
from frappe.model.document import Document


class NextHDServiceCatalog(Document):
	def validate(self):
		"""Validate service catalog before save"""
		pass

	def on_update(self):
		"""Handle updates to service catalog"""
		pass
