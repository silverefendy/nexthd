import frappe

NEXTHD_WORKFLOWS = {"NextHD Ticket", "NextHD Problem", "NextHD Change Request"}


def validate_no_duplicate_transitions(doc, method):
	"""Cegah Workflow Transition duplikat tersimpan untuk 3 workflow NextHD.

	Duplikat didefinisikan sebagai baris dengan kombinasi
	(state, action, next_state) yang sama persis dalam satu Workflow.
	Guard ini HANYA berlaku untuk Workflow yang namanya ada di NEXTHD_WORKFLOWS —
	Workflow lain (bawaan Frappe atau app lain) tidak disentuh sama sekali.
	"""
	if doc.name not in NEXTHD_WORKFLOWS:
		return

	seen = set()
	duplicates = []
	for row in doc.transitions:
		key = (row.state, row.action, row.next_state)
		if key in seen:
			duplicates.append(f"{row.state} -> [{row.action}] -> {row.next_state}")
		seen.add(key)

	if duplicates:
		frappe.throw(
			frappe._(
				"Ditemukan Workflow Transition duplikat di '{0}', penyimpanan dibatalkan: {1}. "
				"Hapus baris duplikat sebelum menyimpan ulang."
			).format(doc.name, ", ".join(duplicates))
		)
