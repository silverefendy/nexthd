import frappe
from frappe.model.document import Document


class NextHDProblem(Document):
	def validate(self):
		"""Validate problem before save"""
		self.validate_status_transition()

	def validate_status_transition(self):
		"""Validate that status transition is allowed"""
		if not self.status:
			return
		
		# Get previous status if document exists
		if self.docstatus == 0 and not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.status != self.status:
				# Add workflow validation logic here
				# This will be enhanced with workflow implementation
				pass

	def on_update(self):
		"""Handle updates to problem"""
		# Telegram notification hooks will be added in Tahap 6
		pass
