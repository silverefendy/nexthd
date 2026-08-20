// Client script for NextHD User Profile
frappe.ui.form.on('NextHD User Profile', {
	refresh: function(frm) {
		// Check if Telegram is already linked
		if (frm.doc.telegram_chat_id) {
			// Show linked status
			frm.dashboard.add_sidebar_item('Telegram Status', `
				<div style="padding: 10px; background-color: #d4edda; border-radius: 4px; color: #155724;">
					✅ <b>Terhubung</b><br>
					Akun Telegram Anda sudah terhubung dengan NextHD.
				</div>
			`);
		} else {
			// Add button to generate link code
			frm.add_custom_button('Link Telegram Account', function() {
				generate_telegram_link_code(frm);
			}, 'Actions');
		}
	}
});

function generate_telegram_link_code(frm) {
	frappe.call({
		method: 'nexthd.next_helpdesk.utils.telegram.generate_telegram_link_code',
		callback: function(r) {
			if (r.message && r.message.status === 'success') {
				const code = r.message.code;
				
				// Show dialog with the code
				const dialog = new frappe.ui.Dialog({
					title: 'Kode Verifikasi Telegram',
					fields: [
						{
							fieldname: 'verification_code',
							fieldtype: 'HTML',
							options: `
								<div style="text-align: center; padding: 20px;">
									<p style="font-size: 16px; margin-bottom: 15px;">
										Kirim kode ini ke <b>@cmlhelpdesk_bot</b> dalam 10 menit:
									</p>
									<div style="
										font-size: 32px; 
										font-weight: bold; 
										letter-spacing: 5px; 
										padding: 15px; 
										background-color: #f8f9fa; 
										border: 2px solid #dee2e6; 
										border-radius: 8px;
										margin: 10px 0;
										font-family: monospace;
									">
										${code}
									</div>
									<button 
										type="button" 
										class="btn btn-default btn-sm" 
										style="margin-top: 10px;"
										onclick="copyToClipboard('${code}')"
									>
										📋 Salin Kode
									</button>
								</div>
							`
						}
					],
					primary_action_label: 'Tutup',
					primary_action: function() {
						dialog.hide();
					}
				});
				
				dialog.show();
			} else if (r.message && r.message.status === 'error') {
				frappe.msgprint({
					title: 'Error',
					message: r.message.message || 'Gagal generate kode verifikasi',
					indicator: 'red'
				});
			}
		}
	});
}

function copyToClipboard(text) {
	navigator.clipboard.writeText(text).then(function() {
		frappe.msgprint('Kode berhasil disalin ke clipboard!');
	}, function(err) {
		frappe.msgprint('Gagal menyalin kode: ' + err);
	});
}
