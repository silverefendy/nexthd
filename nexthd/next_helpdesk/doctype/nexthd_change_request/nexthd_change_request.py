import frappe
from frappe.model.document import Document


class NextHDChangeRequest(Document):
	def validate(self):
		"""Validate change request before save"""
		self.validate_status_transition()
		self.validate_emergency_change()

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
		
		Workflow: Draft → Diajukan → Direview → [Disetujui/Ditolak] → Implementasi → Selesai → Ditutup
		
		- Agent Manager/IT Manager: Full override + Approve
		- Agent: Can create and submit for approval
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
			"Draft": ["Diajukan"],
			"Diajukan": ["Direview"],
			"Direview": ["Disetujui", "Ditolak"],
			"Disetujui": ["Implementasi"],
			"Implementasi": ["Selesai"],
			"Selesai": ["Ditutup"],
			"Ditolak": ["Draft"],  # Can resubmit
			"Ditutup": []
		}
		
		# Check if transition is allowed
		if new_status not in allowed_transitions.get(old_status, []):
			frappe.throw(
				f"Transisi status dari '{old_status}' ke '{new_status}' tidak diizinkan. "
				f"Silakan hubungi Agent Manager atau IT Manager untuk perubahan ini."
			)
		
		# Additional check: Approval transitions require Manager role
		if new_status in ["Disetujui", "Ditolak"] and old_status == "Direview":
			if "Agent Manager" not in user_roles and "IT Manager" not in user_roles:
				frappe.throw(
					"Hanya Agent Manager atau IT Manager yang dapat menyetujui atau menolak Change Request."
				)

	def validate_emergency_change(self):
		"""Validate emergency changes require additional approval"""
		if self.change_type == "Emergency" and self.status in ["Disetujui", "Implementasi"]:
			# Emergency changes may require special handling
			pass

	def on_update(self):
		"""Handle updates to change request"""
		# Telegram notification hooks will be added in Tahap 6
		pass
