import frappe
from frappe.model.document import Document
from datetime import datetime


class NextHDTicket(Document):
	def validate(self):
		"""Validate ticket before save"""
		self.validate_status_transition()
		self.validate_assigned_user()
		
		# Calculate SLA on new ticket creation
		if self.is_new():
			self.calculate_sla()

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
		
		Workflow: Baru → Sedang Dikerjakan → [Menunggu User ⇄ Sedang Dikerjakan] → Selesai → Ditutup
		- Agent: Baru → Sedang Dikerjakan, → Menunggu User, → Selesai
		- Requester: Selesai → Ditutup (konfirmasi) ATAU Selesai → Baru (buka kembali)
		- Agent Manager/IT Manager: Full override
		"""
		user = frappe.session.user
		user_roles = frappe.get_roles(user)
		
		# Agent Manager and IT Manager can override all transitions
		if "Agent Manager" in user_roles or "IT Manager" in user_roles:
			return
		
		# Define allowed transitions
		allowed_transitions = {
			"Baru": ["Sedang Dikerjakan"],
			"Sedang Dikerjakan": ["Menunggu User", "Selesai"],
			"Menunggu User": ["Sedang Dikerjakan", "Selesai"],
			"Selesai": ["Ditutup", "Baru"],
			"Ditutup": []
		}
		
		# Check if transition is allowed
		if new_status not in allowed_transitions.get(old_status, []):
			# Special handling for Requester role
			if "Requester" in user_roles or "Agent" not in user_roles:
				# Requester can only: Selesai → Ditutup OR Selesai → Baru
				if old_status == "Selesai" and new_status in ["Ditutup", "Baru"]:
					return
				else:
					frappe.throw(
						f"Anda tidak memiliki izin untuk mengubah status dari '{old_status}' ke '{new_status}'. "
						f"Sebagai Requester, Anda hanya dapat menutup atau membuka kembali tiket yang sudah selesai."
					)
			else:
				# Agent role
				frappe.throw(
					f"Transisi status dari '{old_status}' ke '{new_status}' tidak diizinkan. "
					f"Silakan hubungi Agent Manager untuk perubahan ini."
				)

	def validate_assigned_user(self):
		"""Validate assigned user if set"""
		if self.assigned_to:
			if not frappe.db.exists("User", self.assigned_to):
				frappe.throw(f"User {self.assigned_to} does not exist")

	def on_update(self):
		"""Handle updates to ticket"""
		self.update_timestamps()
		# Telegram notification hooks will be added in Tahap 6

	def update_timestamps(self):
		"""Update resolved_on and closed_on based on status"""
		if self.status == "Selesai" and not self.resolved_on:
			self.resolved_on = datetime.now()
			self.db_set("resolved_on", self.resolved_on)
		
		if self.status == "Ditutup" and not self.closed_on:
			self.closed_on = datetime.now()
			self.db_set("closed_on", self.closed_on)

	def calculate_sla(self):
		"""Calculate SLA based on priority and SLA Policy"""
		if not self.priority:
			return
		
		# Get SLA policy for this priority
		sla_policy_name = frappe.db.get_value("NextHD SLA Policy", {"priority": self.priority}, "name")
		if not sla_policy_name:
			frappe.log_error(f"No SLA Policy found for priority: {self.priority}")
			return
		
		sla_policy = frappe.get_doc("NextHD SLA Policy", sla_policy_name)
		
		# Calculate response SLA
		if sla_policy.response_time_minutes:
			self.sla_response_by = self._calculate_sla_datetime(sla_policy.response_time_minutes, sla_policy.business_hours)
		
		# Calculate resolution SLA
		if sla_policy.resolution_time_minutes:
			self.sla_resolution_by = self._calculate_sla_datetime(sla_policy.resolution_time_minutes, sla_policy.business_hours)

	def _calculate_sla_datetime(self, minutes: int, business_hours_name: str):
		"""
		Calculate SLA datetime considering business hours.
		
		Args:
			minutes: SLA time in minutes
			business_hours_name: Name of Business Hours configuration
			
		Returns:
			Datetime object for SLA deadline
		"""
		from datetime import timedelta
		
		# Simple implementation: add minutes to current time
		# In production, this should consider business hours properly
		now = datetime.now()
		sla_deadline = now + timedelta(minutes=minutes)
		
		return sla_deadline

	def get_user_profile(self, user):
		"""Get NextHD User Profile for a user"""
		profile = frappe.db.get_value("NextHD User Profile", {"user": user}, "name")
		if profile:
			return frappe.get_doc("NextHD User Profile", profile)
		return None
