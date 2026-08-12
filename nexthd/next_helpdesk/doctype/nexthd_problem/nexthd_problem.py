import frappe
import re
from frappe.model.document import Document


class NextHDProblem(Document):
	def validate(self):
		pass

	def on_update(self):
		pass


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
