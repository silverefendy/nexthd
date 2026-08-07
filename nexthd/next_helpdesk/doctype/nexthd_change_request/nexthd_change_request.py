import frappe
from frappe.model.document import Document


class NextHDChangeRequest(Document):
	def validate(self):
		"""Validate change request before save"""
		self.validate_status_transition()
		self.validate_emergency_change()

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

	def validate_emergency_change(self):
		"""Validate emergency changes require additional approval"""
		if self.change_type == "Emergency" and self.status in ["Disetujui", "Implementasi"]:
			# Emergency changes may require special handling
			pass

	def on_update(self):
		"""Handle updates to change request"""
		# Telegram notification hooks will be added in Tahap 6
		pass
