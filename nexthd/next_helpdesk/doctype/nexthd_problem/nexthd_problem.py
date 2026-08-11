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


@frappe.whitelist()
def create_known_error(problem_name):
	"""
	Membuat NextHD Known Error baru dari NextHD Problem, dan mengubah
	status Problem menjadi "Known Error".

	Args:
		problem_name (str): nama/ID record NextHD Problem

	Returns:
		str: nama record NextHD Known Error yang baru dibuat

	Raises:
		frappe.ValidationError: jika root_cause kosong atau status
			Problem bukan "Investigasi"
	"""
	# 1. Ambil doc Problem
	problem = frappe.get_doc("NextHD Problem", problem_name)

	# 2. Validasi root_cause tidak kosong (strip HTML/whitespace)
	if not problem.root_cause or not problem.root_cause.strip():
		frappe.throw(frappe._("Akar masalah harus diisi sebelum membuat Known Error"))

	# 3. Validasi status Problem == "Investigasi"
	if problem.status != "Investigasi":
		frappe.throw(frappe._("Problem harus berstatus Investigasi untuk dikonversi ke Known Error"))

	# 4. Buat record NextHD Known Error baru
	known_error = frappe.get_doc({
		"doctype": "NextHD Known Error",
		"title": problem.title,
		"symptom": problem.root_cause,
		"workaround": problem.workaround,
		"related_problem": problem.name
	})
	known_error.insert()

	# 5. Update Problem
	problem.known_error = known_error.name
	problem.status = "Known Error"
	problem.save()

	# 6. Return nama Known Error baru
	return known_error.name
