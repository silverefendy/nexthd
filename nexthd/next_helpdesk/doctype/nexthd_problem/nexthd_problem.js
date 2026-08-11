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

		// Show button only if all conditions are met
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
	}
});
