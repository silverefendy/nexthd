import frappe

NEXTHD_WORKFLOWS = {"NextHD Ticket", "NextHD Problem", "NextHD Change Request"}


def validate_no_duplicate_transitions(doc, method):
	# Guard di-skip saat proses migrate/install/import fixture Frappe sedang berjalan,
	# karena reimport bisa sesaat menggabungkan child rows dari 2 sumber fixture
	# (Workflow dan Workflow Transition) sebelum validate() dipanggil.
	if frappe.flags.in_migrate or frappe.flags.in_install or getattr(frappe.flags, "in_import", False):
		return
	if doc.name not in NEXTHD_WORKFLOWS:
		return
	seen = set()
	duplicates = []
	for row in doc.transitions:
		key = (row.state, row.action, row.next_state)
		if key in seen:
			duplicates.append(row.state + " -> [" + row.action + "] -> " + row.next_state)
		seen.add(key)
	if duplicates:
		frappe.throw(
			frappe._("Ditemukan Workflow Transition duplikat di '{0}', penyimpanan dibatalkan: {1}. Hapus baris duplikat sebelum menyimpan ulang.").format(doc.name, ", ".join(duplicates))
		)
