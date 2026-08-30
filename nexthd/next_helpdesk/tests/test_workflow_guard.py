import frappe
from frappe.tests.utils import FrappeTestCase


class TestWorkflowGuard(FrappeTestCase):
	def test_valid_workflow_save_succeeds(self):
		"""Workflow tanpa duplikat harus tetap bisa disimpan normal."""
		wf = frappe.get_doc("Workflow", "NextHD Ticket")
		# Save ulang tanpa perubahan apapun — harus sukses, tidak boleh throw
		wf.save()

	def test_duplicate_transition_is_rejected(self):
		"""Menambahkan transisi duplikat harus ditolak dengan ValidationError."""
		wf = frappe.get_doc("Workflow", "NextHD Ticket")
		if not wf.transitions:
			self.skipTest("NextHD Ticket tidak punya transitions, skip test ini")

		existing = wf.transitions[0]
		wf.append("transitions", {
			"state": existing.state,
			"action": existing.action,
			"next_state": existing.next_state,
			"allowed": existing.allowed,
		})

		with self.assertRaises(frappe.ValidationError):
			wf.save()

	def test_other_workflow_not_affected(self):
		"""Workflow di luar 3 nama NextHD tidak boleh divalidasi guard ini."""
		from nexthd.next_helpdesk.utils.workflow_guard import validate_no_duplicate_transitions

		class DummyDoc:
			name = "Some Other Workflow"
			transitions = []

		# Tidak boleh raise apapun untuk Workflow di luar cakupan
		validate_no_duplicate_transitions(DummyDoc(), "validate")
