import frappe
from frappe.model.document import Document


class NextHDProblem(Document):
	def validate(self):
		"""Validate problem before save"""
		self.validate_status_transition()

	def validate_status_transition(self):
		"""Validate that status transition is allowed according to workflow"""
		if not self.status:
			return
		
		# Get previous status if document exists
		if self.docstatus == 0 and not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.status != self.status:
				self._check_workflow_permission(old_doc.status, self.status)

	def _check_workflow_permission(self, old_status, new_status):
		"""
		Validate status transition based on workflow rules.
		
		Workflow: Terbuka → Investigasi → Known Error → Selesai → Ditutup
		          ↓
		      Selesai (langsung, jika root cause ditemukan tanpa perlu status Known Error)
		
		- Agent Manager/IT Manager: Full override
		- Agent: Can progress through workflow
		- IT Auditor: Read-only
		"""
		user = frappe.session.user
		user_roles = frappe.get_roles(user)
		
		# Agent Manager and IT Manager can override all transitions
		if "Agent Manager" in user_roles or "IT Manager" in user_roles:
			return
		
		# IT Auditor can only read
		if "IT Auditor" in user_roles:
			frappe.throw("IT Auditor hanya memiliki izin baca. Tidak dapat mengubah status.")
		
		# Define allowed transitions
		allowed_transitions = {
			"Terbuka": ["Investigasi", "Selesai"],
			"Investigasi": ["Known Error", "Selesai"],
			"Known Error": ["Selesai"],
			"Selesai": ["Ditutup"],
			"Ditutup": []
		}
		
		# Check if transition is allowed
		if new_status not in allowed_transitions.get(old_status, []):
			frappe.throw(
				f"Transisi status dari '{old_status}' ke '{new_status}' tidak diizinkan. "
				f"Silakan hubungi Agent Manager untuk perubahan ini."
			)

	def on_update(self):
		"""Handle updates to problem"""
		# Telegram notification hooks will be added in Tahap 6
		pass
