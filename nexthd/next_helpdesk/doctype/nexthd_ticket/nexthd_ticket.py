import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, add_to_date, get_datetime
from nexthd.next_helpdesk.utils.business_hours import add_working_time


class NextHDTicket(Document):
	def validate(self):
		self._priority_set_by_matrix_this_save = False
		self.set_priority_from_matrix()
		self.validate_assigned_user()
		if self.is_new():
			self.calculate_sla()
		# Auto-fill requested_by from session user for web form submissions
		if not self.requested_by:
			self.requested_by = frappe.session.user

	def validate_assigned_user(self):
		if self.assigned_to:
			if not frappe.db.exists("User", self.assigned_to):
				frappe.throw(f"User {self.assigned_to} tidak ditemukan")

	def set_priority_from_matrix(self):
		# Check if priority was manually set by a manager (permlevel-1 write)
		if not self.is_new() and self.has_value_changed("priority") and not self._priority_set_by_matrix_this_save:
			self.priority_manually_set = 1
		
		# If manually set, skip auto-calculation
		if self.priority_manually_set:
			return
		
		# Only calculate if both impact and urgency are set
		if not self.impact or not self.urgency:
			return
		
		# Priority matrix
		matrix = {
			("Tinggi", "Tinggi"): "Kritis",
			("Tinggi", "Rendah"): "Tinggi",
			("Rendah", "Tinggi"): "Sedang",
			("Rendah", "Rendah"): "Rendah"
		}
		
		matrix_priority = matrix.get((self.impact, self.urgency))
		if matrix_priority:
			self.priority = matrix_priority
			self._priority_set_by_matrix_this_save = True

	def on_update(self):
		self.update_timestamps()
		self.handle_workflow_sla_transitions()

	def update_timestamps(self):
		if self.status == "Selesai" and not self.resolved_on:
			self.db_set("resolved_on", now_datetime())
		if self.status == "Ditutup" and not self.closed_on:
			self.db_set("closed_on", now_datetime())

	def _get_sla_policy_for_priority(self, priority):
		"""Helper method to get SLA policy for a given priority"""
		if not priority:
			return None
		sla_policy_name = frappe.db.get_value(
			"NextHD SLA Policy", {"priority": priority}, "name"
		)
		if not sla_policy_name:
			frappe.log_error(f"No SLA Policy found for priority: {priority}")
			return None
		return frappe.get_doc("NextHD SLA Policy", sla_policy_name)

	def handle_workflow_sla_transitions(self):
		"""Handle SLA-related workflow state transitions"""
		if not self.has_value_changed("status"):
			return
		
		doc_before_save = self.get_doc_before_save()
		if not doc_before_save:
			return
		
		old_status = doc_before_save.status
		new_status = self.status
		
		# Baru -> Sedang Dikerjakan: recalculate sla_resolution_by and set responded_on
		if old_status == "Baru" and new_status == "Sedang Dikerjakan":
			self._recalculate_sla_resolution_on_start()
		
		# Sedang Dikerjakan -> Menunggu User: create waiting_log entry
		elif old_status == "Sedang Dikerjakan" and new_status == "Menunggu User":
			self._create_waiting_log_entry()
		
		# Menunggu User -> Sedang Dikerjakan: close waiting_log and extend sla_resolution_by
		elif old_status == "Menunggu User" and new_status == "Sedang Dikerjakan":
			self._close_waiting_log_and_extend_sla()
		
		# Menunggu User -> Selesai: close waiting_log without extending sla_resolution_by
		elif old_status == "Menunggu User" and new_status == "Selesai":
			self._close_waiting_log_on_resolve()

	def _recalculate_sla_resolution_on_start(self):
		"""Recalculate sla_resolution_by when ticket starts being worked on"""
		sla_policy = self._get_sla_policy_for_priority(self.priority)
		if not sla_policy:
			return
		
		is_24x7 = getattr(sla_policy, "is_24x7", 0)
		now = now_datetime()
		
		if sla_policy.resolution_time_minutes:
			new_sla_resolution_by = add_working_time(
				now, sla_policy.resolution_time_minutes, is_24x7=is_24x7
			)
			self.db_set("sla_resolution_by", new_sla_resolution_by)
		
		# Set responded_on
		self.db_set("responded_on", now)

	def _create_waiting_log_entry(self):
		"""Create a new waiting_log entry when waiting for user.
		Uses frappe.db.sql instead of frappe.new_doc().insert() to avoid
		Frappe child-table sync wiping this row on the next save() call.
		"""
		now = now_datetime()
		max_idx = frappe.db.get_value(
			"NextHD Ticket Waiting Log",
			{"parent": self.name},
			"idx",
			order_by="idx desc"
		) or 0

		frappe.db.sql("""
			INSERT INTO `tabNextHD Ticket Waiting Log`
				(name, parent, parenttype, parentfield, idx,
				 asked_on, asked_by, question,
				 creation, modified, owner, modified_by)
			VALUES
				(%s, %s, 'NextHD Ticket', 'waiting_log', %s,
				 %s, %s, %s,
				 %s, %s, %s, %s)
		""", (
			frappe.generate_hash(length=10),
			self.name,
			max_idx + 1,
			now,
			frappe.session.user,
			"Menunggu respons dari user",
			now,
			now,
			frappe.session.user,
			frappe.session.user,
		))
		# Refresh in-memory child table so subsequent save() calls on this
		# same document instance do not wipe the row we just inserted via SQL.
		self.load_from_db()


	def _close_waiting_log_and_extend_sla(self):
		"""Close the latest waiting_log entry and extend sla_resolution_by"""
		# Find the latest open waiting_log row (replied_on is null)
		open_log = frappe.db.sql("""
			SELECT name, asked_on
			FROM `tabNextHD Ticket Waiting Log`
			WHERE parent = %s AND replied_on IS NULL
			ORDER BY idx DESC
			LIMIT 1
		""", (self.name,), as_dict=True)
		
		if not open_log:
			return
		
		open_log = open_log[0]
		replied_on = now_datetime()
		
		# Update the waiting_log row
		frappe.db.set_value("NextHD Ticket Waiting Log", open_log.name, "replied_on", replied_on)
		
		# Calculate pause duration in minutes (rounded up)
		asked_on = get_datetime(open_log.asked_on)
		pause_seconds = (replied_on - asked_on).total_seconds()
		pause_minutes = int((pause_seconds + 59) // 60)  # Round up to nearest minute
		
		# Extend sla_resolution_by by pause_minutes (straight time addition, not working time)
		current_sla_resolution_by = self.sla_resolution_by
		if current_sla_resolution_by:
			new_sla_resolution_by = add_to_date(
				current_sla_resolution_by, minutes=pause_minutes, as_datetime=True
			)
			self.db_set("sla_resolution_by", new_sla_resolution_by)

	def _close_waiting_log_on_resolve(self):
		"""Close open waiting_log entry when ticket is resolved from Menunggu User"""
		# Find the latest open waiting_log row (replied_on is null)
		open_log = frappe.db.sql("""
			SELECT name
			FROM `tabNextHD Ticket Waiting Log`
			WHERE parent = %s AND replied_on IS NULL
			ORDER BY idx DESC
			LIMIT 1
		""", (self.name,), as_dict=True)
		
		if open_log:
			# Close the log entry without extending sla_resolution_by
			frappe.db.set_value("NextHD Ticket Waiting Log", open_log[0].name, "replied_on", now_datetime())

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
