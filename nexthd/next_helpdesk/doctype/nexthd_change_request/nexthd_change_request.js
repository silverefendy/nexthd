// Copyright (c) 2026, nexthd and contributors
// For license information, please see license.txt

frappe.ui.form.on('NextHD Change Request', {
	refresh: function(frm) {
		// Initialize flags for preventing duplicate prompts
		if (!frm.doc.__asset_prompt_shown) {
			frm.doc.__asset_prompt_shown = false;
		}
		if (!frm.doc.__problem_prompt_shown) {
			frm.doc.__problem_prompt_shown = false;
		}
	},
	status: function(frm) {
		// Handler untuk status "Selesai" - prompt update status Aset
		if (frm.doc.status === 'Selesai' && frm.doc.related_asset && !frm.doc.__asset_prompt_shown) {
			frm.doc.__asset_prompt_shown = true;

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
		if (frm.doc.status === 'Ditutup' && frm.doc.related_problem && !frm.doc.__problem_prompt_shown) {
			frm.doc.__problem_prompt_shown = true;

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
});
