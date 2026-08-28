frappe.pages["nexthd-reset-data"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: "Reset Data Demo NextHD",
		single_column: true,
	});

	$(page.body).html(`
		<div style="max-width: 600px; margin: 30px auto; padding: 20px; border: 1px solid #ffb3b3; border-radius: 8px; background: #fff5f5;">
			<h4 style="color: #c0392b;">Peringatan: Aksi Tidak Bisa Dibatalkan</h4>
			<p>Tombol ini akan menghapus <b>SEMUA</b> data berikut secara permanen:</p>
			<ul>
				<li>NextHD Ticket</li>
				<li>NextHD Problem</li>
				<li>NextHD Change Request</li>
				<li>NextHD Known Error</li>
				<li>NextHD Asset</li>
				<li>NextHD Photo</li>
			</ul>
			<p>Data master (Category, Team, SLA Policy) <b>tidak</b> akan dihapus. Backup otomatis akan dibuat sebelum penghapusan.</p>
			<button class="btn btn-danger" id="btn-reset-nexthd">Reset Semua Data Transaksi</button>
		</div>
	`);

	$("#btn-reset-nexthd").on("click", function () {
		frappe.confirm(
			"Apakah Anda YAKIN ingin menghapus semua data transaksi NextHD? Tindakan ini permanen.",
			function () {
				// Konfirmasi kedua: wajib ketik RESET persis
				frappe.prompt(
					{
						fieldname: "confirm_text",
						fieldtype: "Data",
						label: "Ketik RESET untuk melanjutkan",
						reqd: 1,
					},
					function (values) {
						if (values.confirm_text !== "RESET") {
							frappe.msgprint("Teks konfirmasi tidak sesuai. Proses dibatalkan.");
							return;
						}
						frappe.dom.freeze("Membuat backup dan menghapus data, mohon tunggu...");
						frappe.call({
							method: "nexthd.api.reset_demo_data",
							args: { confirm_text: values.confirm_text },
							callback: function (r) {
								frappe.dom.unfreeze();
								if (r.message) {
									frappe.msgprint({
										title: "Reset Berhasil",
										message: "Data terhapus: " + JSON.stringify(r.message),
										indicator: "green",
									});
								}
							},
							error: function () {
								frappe.dom.unfreeze();
							},
						});
					},
					"Konfirmasi Kedua",
					"Ya, Hapus Sekarang"
				);
			}
		);
	});
};
