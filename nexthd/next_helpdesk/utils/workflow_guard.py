import frappe

NEXTHD_WORKFLOWS = {"NextHD Ticket", "NextHD Problem", "NextHD Change Request"}


	# Exception "skip saat in_migrate/in_install/in_import" DIHAPUS (30 Agustus 2026).
	# Root cause duplikasi Round 4 sudah diperbaiki secara struktural: fixture
	# "Workflow Transition" terpisah sudah dihapus dari hooks.py, sehingga tidak
	# ada lagi 2 channel fixture yang saling menambah child rows saat migrate.
	# Guard ini sekarang TETAP AKTIF bahkan saat migrate, supaya kalau ada
	# regresi (mis. seseorang menambah lagi fixture Workflow Transition terpisah
	# tanpa sadar), migrate akan langsung GAGAL dengan pesan jelas, bukan
	# didiamkan sampai ketahuan lewat verifikasi manual.
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
