// Copyright (c) 2026, nexthd and contributors
// For license information, please see license.txt

frappe.ui.form.on('NextHD Problem', {
	refresh: function(frm) {
		// Check if user has required role
		const user_roles = frappe.user_roles;
		const allowed_roles = ['Agent', 'Agent Manager', 'IT Manager'];
		const has_allowed_role = allowed_roles.some(role => user_roles.includes(role));

		// Check if status is "Investigasi"
		const is_investigasi = frm.doc.status === 'Investigasi';

		// root_cause adalah Text Editor (HTML), gunakan DOMParser untuk
		// mendeteksi apakah konten benar-benar kosong (bukan hanya <p></p>)
		function has_text_content(html) {
			if (!html) return false;
			const doc = new DOMParser().parseFromString(html, 'text/html');
			return (doc.body.textContent || '').trim().length > 0;
		}
		const has_root_cause = has_text_content(frm.doc.root_cause);

		// Show "Convert to Known Error" button only if all conditions are met
		if (has_allowed_role && is_investigasi && has_root_cause) {
			frm.add_custom_button(__('Convert to Known Error'), function() {
				// Show loading indicator
				frappe.show_alert(__('Membuat Known Error...'));

				// Call server method
				frappe.call({
					method: 'nexthd.next_helpdesk.doctype.nexthd_problem.nexthd_problem.create_known_error',
					args: {
						problem_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							// Refresh form before redirect
							frm.reload_doc().then(() => {
								// Redirect to new Known Error record
								frappe.set_route('Form', 'NextHD Known Error', r.message);
							});
						}
					},
					error: function(err) {
						frappe.msgprint(__('Gagal membuat Known Error: ') + (err.message || err));
					}
				});
			}, __('Actions'));
		}

		// Show "Buat Change Request" button if conditions are met
		const allowed_cr_statuses = ['Investigasi', 'Known Error', 'Selesai'];
		const is_allowed_cr_status = allowed_cr_statuses.includes(frm.doc.status);
		const has_no_change_request = !frm.doc.change_request;

		if (has_allowed_role && is_allowed_cr_status && has_no_change_request && has_root_cause) {
			frm.add_custom_button(__('Buat Change Request'), function() {
				// Show loading indicator
				frappe.show_alert(__('Membuat Change Request...'));

				// Call server method
				frappe.call({
					method: 'nexthd.next_helpdesk.doctype.nexthd_problem.nexthd_problem.create_change_request',
					args: {
						problem_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							// Refresh form before redirect
							frm.reload_doc().then(() => {
								// Redirect to new Change Request record
								frappe.set_route('Form', 'NextHD Change Request', r.message);
							});
						}
					},
					error: function(err) {
						frappe.msgprint(__('Gagal membuat Change Request: ') + (err.message || err));
					}
				});
			}, __('Actions'));
		}

		// Show "Lihat Tiket Terkait yang Belum Ditutup" button when Problem is closed
		const is_ditutup = frm.doc.status === 'Ditutup';
		if (has_allowed_role && is_ditutup) {
			frm.add_custom_button(__('Lihat Tiket Terkait yang Belum Ditutup'), function() {
				frappe.call({
					method: 'nexthd.next_helpdesk.doctype.nexthd_problem.nexthd_problem.get_open_related_tickets',
					args: { problem_name: frm.doc.name },
					callback: function(r) {
						if (r.message && r.message.length > 0) {
							const list_html = r.message.map(t => `<li><a href="/app/nexthd-ticket/${t.name}" target="_blank">${t.name}</a> — ${t.status}</li>`).join('');
							frappe.msgprint({
								title: __('Tiket Terkait yang Masih Terbuka'),
								message: `<ul>${list_html}</ul><p>${__('Silakan tinjau dan tutup masing-masing tiket secara manual dari Requester agar konfirmasi penutupan tetap tercatat.')}</p>`,
								indicator: 'orange'
							});
						} else {
							frappe.msgprint(__('Semua tiket terkait Problem ini sudah Selesai/Ditutup.'));
						}
					},
					error: function(err) {
						frappe.msgprint(__('Gagal mengambil daftar tiket: ') + (err.message || err));
					}
				});
			}, __('Actions'));
		}
	}
});
