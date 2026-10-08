// eslint-disable-next-line
frappe.ui.form.on("NextHD Ticket", {
	refresh: function(frm) {
		// Tambah tombol "Tampilkan semua aset" di form
		if (!frm.custom_buttons) {
			frm.custom_buttons = {};
		}

		frm.add_custom_button(__("Tampilkan semua aset"), function() {
			frm.tampilkan_semua_aset = !frm.tampilkan_semua_aset;
			frm.refresh_field("affected_asset");
		}, __("Affected Asset"));

		// Set flag awal
		if (frm.tampilkan_semua_aset === undefined) {
			frm.tampilkan_semua_aset = false;
		}
	},

	requested_by: function(frm) {
		// Saat requested_by berubah, query dipasang ulang
		frm.refresh_field("affected_asset");
	},

	onload: function(frm) {
		// Set query untuk affected_asset
		frm.set_query("affected_asset", function() {
			return {
				query: "nexthd.next_helpdesk.utils.aset_filter.get_asset_list_for_ticket",
				filters: {
					requested_by: frm.doc.requested_by,
					semua: frm.tampilkan_semua_aset ? 1 : 0
				}
			};
		});
	}
});
