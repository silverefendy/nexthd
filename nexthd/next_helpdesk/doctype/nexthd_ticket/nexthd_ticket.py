import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime
from nexthd.next_helpdesk.utils.business_hours import add_working_time


class NextHDTicket(Document):
	def validate(self):
		self.validate_assigned_user()
		if self.is_new():
			self.calculate_sla()

	def validate_assigned_user(self):
		if self.assigned_to:
			if not frappe.db.exists("User", self.assigned_to):
				frappe.throw(f"User {self.assigned_to} tidak ditemukan")

	def on_update(self):
		self.update_timestamps()

	def update_timestamps(self):
		if self.status == "Selesai" and not self.resolved_on:
			self.db_set("resolved_on", now_datetime())
		if self.status == "Ditutup" and not self.closed_on:
			self.db_set("closed_on", now_datetime())

	def calculate_sla(self):
		if not self.priority:
			return
		sla_policy_name = frappe.db.get_value(
			"NextHD SLA Policy", {"priority": self.priority}, "name"
		)
		if not sla_policy_name:
			frappe.log_error(f"No SLA Policy found for priority: {self.priority}")
			return
		sla_policy = frappe.get_doc("NextHD SLA Policy", sla_policy_name)
		is_24x7 = getattr(sla_policy, "is_24x7", 0)
		now = now_datetime()
		if sla_policy.response_time_minutes:
			self.sla_response_by = add_working_time(
				now, sla_policy.response_time_minutes, is_24x7=is_24x7
			)
		if sla_policy.resolution_time_minutes:
			self.sla_resolution_by = add_working_time(
				now, sla_policy.resolution_time_minutes, is_24x7=is_24x7
			)

	def get_user_profile(self, user):
		profile_name = frappe.db.get_value("NextHD User Profile", {"user": user}, "name")
		if profile_name:
			return frappe.get_doc("NextHD User Profile", profile_name)
		return None
