import frappe
from frappe.model.document import Document


class NextHDAsset(Document):
	def validate(self):
		"""Validate asset before save"""
		self.validate_warranty_dates()

	def validate_warranty_dates(self):
		"""Validate warranty dates"""
		if self.purchase_date and self.warranty_until:
			if self.warranty_until < self.purchase_date:
				frappe.throw("Warranty Until date cannot be before Purchase Date")

	def on_update(self):
		"""Handle updates to asset"""
		pass
