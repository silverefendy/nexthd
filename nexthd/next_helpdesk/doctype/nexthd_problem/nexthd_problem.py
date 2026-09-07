import frappe
from frappe.utils import now_datetime
import re
from frappe.model.document import Document
from nexthd.next_helpdesk.utils.activity_log import _add_activity_log_entry


class NextHDProblem(Document):
	def validate(self):
		for row in self.activity_log:
			if not row.timestamp:  # baris baru dari input manual di grid UI
				row.timestamp = frappe.utils.now()
				row.updated_by = frappe.session.user
				if not row.entry_type:
					row.entry_type = "Manual"
				if row.entry_type == "Manual" and not row.note:
					frappe.throw(_("Catatan wajib diisi untuk entry Manual di Riwayat Aktivitas"))

	def on_update(self):
		self.sync_meta_dates()
		if self.has_value_changed("status"):
			old_status = self.get_doc_before_save().status if self.get_doc_before_save() else None
			_add_activity_log_entry(
				doctype=self.doctype,
				docname=self.name,
				status_from=old_status,
				status_to=self.status,
				entry_type="Otomatis"
			)

	def sync_meta_dates(self):
		if not self.tanggal_dibuat:
			self.db_set("tanggal_dibuat", self.creation, update_modified=False)
		self.db_set("tanggal_diedit", now_datetime(), update_modified=False)


@frappe.whitelist()
def create_known_error(problem_name):
	problem = frappe.get_doc("NextHD Problem", problem_name)
	raw_text = re.sub(r'<[^>]+>', '', problem.root_cause or '').strip()
	if not raw_text:
		frappe.throw(frappe._("Akar masalah harus diisi sebelum membuat Known Error"))
	if problem.status != "Investigasi":
		frappe.throw(frappe._("Problem harus berstatus Investigasi untuk dikonversi ke Known Error"))
	known_error = frappe.get_doc({
		"doctype": "NextHD Known Error",
		"title": problem.title,
		"symptom": problem.root_cause,
		"workaround": problem.workaround,
		"related_problem": problem.name
	})
	known_error.insert()
	problem.db_set("known_error", known_error.name)
	problem.db_set("status", "Known Error")
	return known_error.name


@frappe.whitelist()
def create_change_request(problem_name):
	problem = frappe.get_doc("NextHD Problem", problem_name)
	raw_text = re.sub(r'<[^>]+>', '', problem.root_cause or '').strip()
	if not raw_text:
		frappe.throw(frappe._("Akar masalah harus diisi sebelum membuat Change Request"))
	
	allowed_statuses = ["Investigasi", "Known Error", "Selesai"]
	if problem.status not in allowed_statuses:
		frappe.throw(frappe._("Problem harus berstatus Investigasi, Known Error, atau Selesai untuk membuat Change Request"))
	
	if problem.change_request:
		frappe.throw(frappe._("Problem ini sudah memiliki Change Request terkait"))
	
	change_request = frappe.get_doc({
		"doctype": "NextHD Change Request",
		"title": f"CR untuk {problem.title}",
		"related_problem": problem.name,
		"implementation_plan": problem.workaround or "",
		"status": "Draft",
		"change_type": "Normal",
		"risk_level": "Sedang"
	})
	change_request.insert()
	problem.db_set("change_request", change_request.name)
	return change_request.name


@frappe.whitelist()
def get_open_related_tickets(problem_name):
	problem = frappe.get_doc("NextHD Problem", problem_name)
	open_tickets = []
	for row in problem.related_tickets:
		ticket_name = row.ticket
		if not ticket_name:
			continue
		status = frappe.db.get_value("NextHD Ticket", ticket_name, "status")
		if status not in ["Selesai", "Ditutup"]:
			open_tickets.append({"name": ticket_name, "status": status})
	return open_tickets
