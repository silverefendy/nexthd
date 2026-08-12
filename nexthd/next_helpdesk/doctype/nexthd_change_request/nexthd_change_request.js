// Copyright (c) 2026, nexthd and contributors
// For license information, please see license.txt

frappe.ui.form.on('NextHD Change Request', {
	refresh: function(frm) {
		// CATATAN PENTING (fix 2026-08-12):
		// Perubahan status via tombol Workflow TIDAK memicu event field
		// `status: function(frm) {...}` karena Frappe mengubah status lewat
		// apply_workflow() -> frappe.model.sync() -> frm.refresh(), bukan lewat
		// frm.set_value('status', ...). Jadi logika prompt WAJIB ditaruh di
		// refresh, dan kita bandingkan manual status sekarang vs status
		// terakhir yang kita lihat (disimpan di objek `frm`, bukan `frm.doc`,
		// karena `frm.doc` di-replace setiap kali frappe.model.sync jalan,
		// sedangkan objek `frm` sendiri persist antar refresh).

		if (frm.__last_seen_status === undefined) {
			// Form baru dibuka / doc baru dimuat pertama kali di sesi ini.
			// Jangan langsung prompt, cuma catat baseline-nya.
			frm.__last_seen_status = frm.doc.status;
			return;
		}

		if (frm.__last_seen_status !== frm.doc.status) {
			const previous_status = frm.__last_seen_status;
			frm.__last_seen_status = frm.doc.status;
			handle_status_change(frm, previous_status);
		}
	}
});

function handle_status_change(frm, previous_status) {
	// Handler untuk status "Selesai" - prompt update status Aset
	if (frm.doc.status === 'Selesai' && frm.doc.related_asset) {
		frappe.confirm(
			__('Change Request ini terkait Aset {0}. Apakah status Aset perlu diupdate?', [frm.doc.related_asset]),
			function() {
				// Yes - tampilkan pilihan status baru
				frappe.prompt([
					{
						fieldname: 'new_asset_status',
						label: __('Status Aset Baru'),
						fieldtype: 'Select',
						options: 'Aktif\nRusak\nDiperbaiki\nDihapus',
						default: 'Aktif',
						reqd: 1
					}
				], function(values) {
					frappe.call({
						method: 'nexthd.next_helpdesk.doctype.nexthd_change_request.nexthd_change_request.update_asset_status',
						args: {
							change_request_name: frm.doc.name,
							asset_name: frm.doc.related_asset,
							new_status: values.new_asset_status
						},
						callback: function(r) {
							if (r.message) {
								frappe.show_alert(__('Status Aset berhasil diupdate menjadi {0}', [values.new_asset_status]));
							}
						},
						error: function(err) {
							frappe.msgprint(__('Gagal mengupdate status Aset: ') + (err.message || err));
						}
					});
				}, __('Update Status Aset'), __('Simpan'));
			}
			// No - tidak lakukan apa-apa
		);
	}

	// Handler untuk status "Ditutup" - prompt buka Problem terkait
	if (frm.doc.status === 'Ditutup' && frm.doc.related_problem) {
		frappe.call({
			method: 'nexthd.next_helpdesk.doctype.nexthd_change_request.nexthd_change_request.get_problem_status',
			args: { problem_name: frm.doc.related_problem },
			callback: function(r) {
				if (r.message && !['Selesai', 'Ditutup'].includes(r.message)) {
					frappe.confirm(
						__('Change Request ini sudah ditutup. Problem terkait ({0}) masih berstatus "{1}". Buka Problem sekarang untuk ditinjau?', [frm.doc.related_problem, r.message]),
						function() {
							frappe.set_route('Form', 'NextHD Problem', frm.doc.related_problem);
						}
					);
				}
			}
		});
	}
}
