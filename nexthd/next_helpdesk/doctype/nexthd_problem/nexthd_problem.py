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
