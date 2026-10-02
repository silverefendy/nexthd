(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	// Get ticket ID from query string
	var urlParams = new URLSearchParams(window.location.search);
	var ticketId = urlParams.get("id");

	if (!ticketId) {
		NX.ui.empty(content, "ID tiket tidak ditemukan");
		return;
	}

	var currentTicket = null;
	var actions = null;
	var itUsers = [];
	var session = null;

	function loadTicket() {
		NX.ui.setLoading(content, true);

		NX.api.get("nexthd.next_helpdesk.api.portal.get_ticket", { name: ticketId }).then(function (ticket) {
			currentTicket = ticket;
			content.textContent = "";
			renderTicket(ticket);
			loadActions();
		}).catch(function (err) {
			content.textContent = "";
			if (err.message === "Anda tidak memiliki izin untuk aksi ini" || err.message.includes("tidak ditemukan")) {
				NX.ui.empty(content, err.message);
			} else {
				NX.ui.empty(content, "Gagal memuat: " + err.message);
			}
			var backBtn = document.createElement("button");
			backBtn.className = "nx-btn";
			backBtn.textContent = "Kembali ke antrian";
			backBtn.addEventListener("click", function () {
				window.location.href = "/nexthd/kerja";
			});
			content.appendChild(backBtn);
		});
	}

	function loadActions() {
		NX.api.get("nexthd.next_helpdesk.api.portal.get_ticket_actions", { name: ticketId }).then(function (result) {
			actions = result;
			if (result.can_assign_other) {
				loadItUsers().then(function () {
					renderActions();
				});
			} else {
				renderActions();
			}
		}).catch(function (err) {
			console.error("Gagal memuat aksi:", err);
		});
	}

	function loadItUsers() {
		return NX.api.get("nexthd.next_helpdesk.api.portal.list_it_users").then(function (result) {
			itUsers = result.users;
		}).catch(function (err) {
			console.error("Gagal memuat user IT:", err);
		});
	}

	function renderTicket(ticket) {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		// Header
		var header = document.createElement("div");
		header.className = "nx-page-head";
		var h1 = document.createElement("h1");
		h1.textContent = ticket.subject;
		header.appendChild(h1);

		var meta = document.createElement("div");
		meta.className = "nx-card";
		meta.style.marginBottom = "1rem";

		var idSpan = document.createElement("span");
		idSpan.textContent = ticket.name;
		meta.appendChild(document.createTextNode("ID: "));
		meta.appendChild(idSpan);
		meta.appendChild(document.createTextNode(" | "));

		var statusBadge = NX.ui.badge(ticket.status, getStatusColor(ticket.status));
		meta.appendChild(statusBadge);
		meta.appendChild(document.createTextNode(" "));

		var priorityBadge = NX.ui.badge(ticket.priority, getPriorityColor(ticket.priority));
		meta.appendChild(priorityBadge);
		meta.appendChild(document.createTextNode(" "));

		var typeBadge = NX.ui.badge(ticket.ticket_type, ticket.ticket_type === "Insiden" ? "red" : "blue");
		meta.appendChild(typeBadge);

		header.appendChild(meta);
		wrap.appendChild(header);

		// Info block
		var infoCard = document.createElement("div");
		infoCard.className = "nx-card";
		infoCard.innerHTML = "<h3>Informasi</h3>";

		var infoTable = document.createElement("table");
		infoTable.className = "nx-table";

		var infoFields = [
			{ label: "Pelapor", value: ticket.requested_by },
			{ label: "Ditugaskan ke", value: ticket.assigned_to || "-" },
			{ label: "Tim", value: ticket.team || "-" },
			{ label: "Kategori", value: ticket.category || "-" },
			{ label: "Impact", value: ticket.impact || "-" },
			{ label: "Urgency", value: ticket.urgency || "-" },
			{ label: "Aset Terkait", value: ticket.affected_asset || "-" },
			{ label: "Problem Terkait", value: ticket.related_problem || "-" }
		];

		infoFields.forEach(function (field) {
			var tr = document.createElement("tr");
			var th = document.createElement("th");
			th.textContent = field.label;
			var td = document.createElement("td");
			td.textContent = field.value;
			tr.appendChild(th);
			tr.appendChild(td);
			infoTable.appendChild(tr);
		});

		infoCard.appendChild(infoTable);
		wrap.appendChild(infoCard);

		// SLA block
		var slaCard = document.createElement("div");
		slaCard.className = "nx-card";
		slaCard.innerHTML = "<h3>SLA</h3>";

		var slaTable = document.createElement("table");
		slaTable.className = "nx-table";

		var slaFields = [
			{ label: "SLA Respon", value: ticket.sla_response_by ? NX.ui.fmtDateTime(ticket.sla_response_by) : "-" },
			{ label: "SLA Resolusi", value: (ticket.status !== "Selesai" && ticket.status !== "Ditutup") ? (ticket.sla_resolution_by ? NX.ui.fmtDateTime(ticket.sla_resolution_by) : "-") : "-" },
			{ label: "Direspon Pada", value: ticket.responded_on ? NX.ui.fmtDateTime(ticket.responded_on) : "-" },
			{ label: "Selesai Pada", value: ticket.resolved_on ? NX.ui.fmtDateTime(ticket.resolved_on) : "-" },
			{ label: "Ditutup Pada", value: ticket.closed_on ? NX.ui.fmtDateTime(ticket.closed_on) : "-" }
		];

		slaFields.forEach(function (field) {
			var tr = document.createElement("tr");
			var th = document.createElement("th");
			th.textContent = field.label;
			var td = document.createElement("td");
			td.textContent = field.value;
			tr.appendChild(th);
			tr.appendChild(td);
			slaTable.appendChild(tr);
		});

		slaCard.appendChild(slaTable);
		wrap.appendChild(slaCard);

		// Description
		if (ticket.description) {
			var descCard = document.createElement("div");
			descCard.className = "nx-card";
			descCard.innerHTML = "<h3>Deskripsi</h3>";
			var descDiv = document.createElement("div");
			descDiv.id = "nx-description";
			// Safe: description already sanitized by server
			descDiv.innerHTML = ticket.description;
			descCard.appendChild(descDiv);
			wrap.appendChild(descCard);
		}

		// Worklog
		if (ticket.worklog && ticket.worklog.length > 0) {
			var worklogCard = document.createElement("div");
			worklogCard.className = "nx-card";
			worklogCard.innerHTML = "<h3>Riwayat Progress</h3>";

			var worklogTable = document.createElement("table");
			worklogTable.className = "nx-table nx-table--log";
			var worklogThead = document.createElement("thead");
			var worklogHeaderRow = document.createElement("tr");
			["Waktu", "Teknisi", "Aktivitas", "Hasil", "Durasi (menit)"].forEach(function (col) {
				var th = document.createElement("th");
				th.textContent = col;
				worklogHeaderRow.appendChild(th);
			});
			worklogThead.appendChild(worklogHeaderRow);
			worklogTable.appendChild(worklogThead);

			var worklogTbody = document.createElement("tbody");
			ticket.worklog.forEach(function (row) {
				var tr = document.createElement("tr");
				[NX.ui.fmtDateTime(row.waktu), row.teknisi, row.aktivitas, row.hasil, row.durasi_menit].forEach(function (cell) {
					var td = document.createElement("td");
					td.textContent = cell || "-";
					tr.appendChild(td);
				});
				worklogTbody.appendChild(tr);
			});
			worklogTable.appendChild(worklogTbody);
			var worklogWrap = document.createElement("div");
			worklogWrap.className = "nx-table-wrap";
			worklogWrap.appendChild(worklogTable);
			worklogCard.appendChild(worklogWrap);
			wrap.appendChild(worklogCard);
		}

		// Waiting Log
		if (ticket.waiting_log && ticket.waiting_log.length > 0) {
			var waitingCard = document.createElement("div");
			waitingCard.className = "nx-card";
			waitingCard.innerHTML = "<h3>Riwayat Menunggu User</h3>";

			var waitingTable = document.createElement("table");
			waitingTable.className = "nx-table nx-table--log";
			var waitingThead = document.createElement("thead");
			var waitingHeaderRow = document.createElement("tr");
			["Ditanyakan Pada", "Ditanyakan Oleh", "Alasan", "Dibalas Pada", "Balasan"].forEach(function (col) {
				var th = document.createElement("th");
				th.textContent = col;
				waitingHeaderRow.appendChild(th);
			});
			waitingThead.appendChild(waitingHeaderRow);
			waitingTable.appendChild(waitingThead);

			var waitingTbody = document.createElement("tbody");
			ticket.waiting_log.forEach(function (row) {
				var tr = document.createElement("tr");
				[NX.ui.fmtDateTime(row.asked_on), row.asked_by, row.question, NX.ui.fmtDateTime(row.replied_on), row.reply].forEach(function (cell) {
					var td = document.createElement("td");
					td.textContent = cell || "-";
					tr.appendChild(td);
				});
				waitingTbody.appendChild(tr);
			});
			waitingTable.appendChild(waitingTbody);
			var waitingWrap = document.createElement("div");
			waitingWrap.className = "nx-table-wrap";
			waitingWrap.appendChild(waitingTable);
			waitingCard.appendChild(waitingWrap);
			wrap.appendChild(waitingCard);
		}

		// Actions container
		var actionsContainer = document.createElement("div");
		actionsContainer.id = "nx-actions";
		wrap.appendChild(actionsContainer);

		// Worklog form container
		var worklogContainer = document.createElement("div");
		worklogContainer.id = "nx-worklog-form";
		wrap.appendChild(worklogContainer);

		// Back button
		var backBtn = document.createElement("button");
		backBtn.className = "nx-btn";
		backBtn.textContent = "Kembali ke antrian";
		backBtn.addEventListener("click", function () {
			window.location.href = "/nexthd/kerja";
		});
		wrap.appendChild(backBtn);

		content.appendChild(wrap);
	}

	function renderActions() {
		if (!actions) return;

		var actionsContainer = document.getElementById("nx-actions");
		if (!actionsContainer) return;

		// If not writer, don't show actions
		if (actions.actions.length === 0 && !actions.can_assign_self && !actions.can_assign_other && !actions.can_worklog) {
			return;
		}

		var actionsCard = document.createElement("div");
		actionsCard.className = "nx-card";
		actionsCard.innerHTML = "<h3>Aksi</h3>";

		// Workflow actions
		if (actions.actions.length > 0) {
			actions.actions.forEach(function (actionItem) {
				var btn = document.createElement("button");
				btn.className = "nx-btn";
				btn.textContent = actionItem.action;
				btn.addEventListener("click", function () {
					doAction(actionItem.action);
				});
				actionsCard.appendChild(btn);
			});
		}

		// Assign buttons
		if (actions.can_assign_self && (!currentTicket.assigned_to || (currentTicket.assigned_to !== session.user && actions.can_assign_other))) {
			var assignSelfBtn = document.createElement("button");
			assignSelfBtn.className = "nx-btn";
			assignSelfBtn.textContent = "Ambil untuk saya";
			assignSelfBtn.addEventListener("click", function () {
				assignTicket(null);
			});
			actionsCard.appendChild(assignSelfBtn);
		}

		if (actions.can_assign_other && itUsers.length > 0) {
			var assignSelect = document.createElement("select");
			assignSelect.className = "nx-field";
			var defaultOpt = document.createElement("option");
			defaultOpt.value = "";
			defaultOpt.textContent = "-- Pilih penerima --";
			assignSelect.appendChild(defaultOpt);

			itUsers.forEach(function (user) {
				var option = document.createElement("option");
				option.value = user.name;
				option.textContent = user.full_name;
				assignSelect.appendChild(option);
			});

			var assignBtn = document.createElement("button");
			assignBtn.className = "nx-btn";
			assignBtn.textContent = "Tugaskan";
			assignBtn.addEventListener("click", function () {
				if (assignSelect.value) {
					assignTicket(assignSelect.value);
				}
			});

			actionsCard.appendChild(assignSelect);
			actionsCard.appendChild(assignBtn);
		}

		actionsContainer.appendChild(actionsCard);

		// Worklog form
		if (actions.can_worklog) {
			renderWorklogForm();
		}
	}

	function renderWorklogForm() {
		var worklogContainer = document.getElementById("nx-worklog-form");
		if (!worklogContainer) return;

		var worklogCard = document.createElement("div");
		worklogCard.className = "nx-card";
		worklogCard.innerHTML = "<h3>Tambah Catatan</h3>";

		var form = document.createElement("form");
		form.noValidate = true;

		// Aktivitas
		var aktivitasDiv = document.createElement("div");
		aktivitasDiv.className = "nx-field";
		var aktivitasLabel = document.createElement("label");
		aktivitasLabel.textContent = "Aktivitas *";
		aktivitasDiv.appendChild(aktivitasLabel);
		var aktivitasInput = document.createElement("textarea");
		aktivitasInput.name = "aktivitas";
		aktivitasInput.required = true;
		aktivitasInput.maxLength = 1000;
		aktivitasInput.rows = 3;
		aktivitasDiv.appendChild(aktivitasInput);
		form.appendChild(aktivitasDiv);

		// Hasil
		var hasilDiv = document.createElement("div");
		hasilDiv.className = "nx-field";
		var hasilLabel = document.createElement("label");
		hasilLabel.textContent = "Hasil";
		hasilDiv.appendChild(hasilLabel);
		var hasilSelect = document.createElement("select");
		hasilSelect.name = "hasil";
		var hasilDefault = document.createElement("option");
		hasilDefault.value = "";
		hasilDefault.textContent = "-- Pilih --";
		hasilSelect.appendChild(hasilDefault);
		["Berhasil", "Belum Berhasil", "Perlu Eskalasi", "Menunggu Sparepart"].forEach(function (opt) {
			var option = document.createElement("option");
			option.value = opt;
			option.textContent = opt;
			hasilSelect.appendChild(option);
		});
		hasilDiv.appendChild(hasilSelect);
		form.appendChild(hasilDiv);

		// Durasi
		var durasiDiv = document.createElement("div");
		durasiDiv.className = "nx-field";
		var durasiLabel = document.createElement("label");
		durasiLabel.textContent = "Durasi (menit)";
		durasiDiv.appendChild(durasiLabel);
		var durasiInput = document.createElement("input");
		durasiInput.type = "number";
		durasiInput.name = "durasi_menit";
		durasiInput.min = 0;
		durasiInput.max = 1440;
		durasiDiv.appendChild(durasiInput);
		form.appendChild(durasiDiv);

		// Submit button
		var submitBtn = document.createElement("button");
		submitBtn.type = "submit";
		submitBtn.className = "nx-btn";
		submitBtn.textContent = "Simpan";
		form.appendChild(submitBtn);

		form.addEventListener("submit", function (e) {
			e.preventDefault();
			addWorklog(form, submitBtn);
		});

		worklogCard.appendChild(form);
		worklogContainer.appendChild(worklogCard);
	}

	function doAction(action) {
		if (action === "Tunggu User") {
			showQuestionDialog(action);
		} else {
			if (confirm("Apakah Anda yakin ingin melakukan aksi: " + action + "?")) {
				executeAction(action);
			}
		}
	}

	function showQuestionDialog(action) {
		var actionsContainer = document.getElementById("nx-actions");
		if (!actionsContainer) return;

		// Create dialog overlay
		var overlay = document.createElement("div");
		overlay.style.position = "fixed";
		overlay.style.top = "0";
		overlay.style.left = "0";
		overlay.style.right = "0";
		overlay.style.bottom = "0";
		overlay.style.background = "rgba(0,0,0,0.5)";
		overlay.style.zIndex = "2000";
		overlay.style.display = "flex";
		overlay.style.alignItems = "center";
		overlay.style.justifyContent = "center";

		// Create dialog
		var dialog = document.createElement("div");
		dialog.className = "nx-card";
		dialog.style.maxWidth = "500px";
		dialog.style.width = "90%";
		dialog.style.padding = "1.5rem";

		var title = document.createElement("h3");
		title.textContent = "Pertanyaan untuk User";
		dialog.appendChild(title);

		var label = document.createElement("label");
		label.textContent = "Pertanyaan *";
		label.style.display = "block";
		label.style.marginBottom = "0.5rem";
		dialog.appendChild(label);

		var textarea = document.createElement("textarea");
		textarea.rows = 4;
		textarea.maxLength = 500;
		textarea.style.width = "100%";
		textarea.style.marginBottom = "1rem";
		dialog.appendChild(textarea);

		var charCount = document.createElement("small");
		charCount.textContent = "0/500";
		charCount.style.display = "block";
		charCount.style.marginBottom = "1rem";
		dialog.appendChild(charCount);

		textarea.addEventListener("input", function () {
			charCount.textContent = textarea.value.length + "/500";
		});

		var buttonRow = document.createElement("div");
		buttonRow.style.display = "flex";
		buttonRow.style.gap = "0.5rem";

		var cancelBtn = document.createElement("button");
		cancelBtn.className = "nx-btn";
		cancelBtn.textContent = "Batal";
		cancelBtn.addEventListener("click", function () {
			document.body.removeChild(overlay);
		});

		var submitBtn = document.createElement("button");
		submitBtn.className = "nx-btn";
		submitBtn.textContent = "Kirim";
		submitBtn.addEventListener("click", function () {
			var question = textarea.value.trim();
			if (!question) {
				NX.ui.toast("Pertanyaan wajib diisi", "red");
				return;
			}
			document.body.removeChild(overlay);
			executeAction(action, question);
		});

		buttonRow.appendChild(cancelBtn);
		buttonRow.appendChild(submitBtn);
		dialog.appendChild(buttonRow);

		overlay.appendChild(dialog);
		document.body.appendChild(overlay);

		// Focus textarea
		setTimeout(function () {
			textarea.focus();
		}, 100);
	}

	function executeAction(action, question) {
		var data = { name: ticketId, action: action };
		if (question) {
			data.question = question;
		}

		// Disable all action buttons
		var actionsContainer = document.getElementById("nx-actions");
		var buttons = actionsContainer ? actionsContainer.querySelectorAll("button") : [];
		buttons.forEach(function (btn) {
			btn.disabled = true;
		});

		NX.api.post("nexthd.next_helpdesk.api.portal.do_ticket_action", data).then(function (result) {
			NX.ui.toast("Aksi berhasil", "green");
			loadTicket();
		}).catch(function (err) {
			NX.ui.toast("Gagal: " + err.message, "red");
			// Re-enable buttons on error
			buttons.forEach(function (btn) {
				btn.disabled = false;
			});
		});
	}

	function assignTicket(user) {
		var data = { name: ticketId };
		if (user) {
			data.user = user;
		}

		// Disable assign buttons
		var actionsContainer = document.getElementById("nx-actions");
		var assignBtns = actionsContainer ? actionsContainer.querySelectorAll("button") : [];
		assignBtns.forEach(function (btn) {
			if (btn.textContent === "Ambil untuk saya" || btn.textContent === "Tugaskan") {
				btn.disabled = true;
			}
		});

		NX.api.post("nexthd.next_helpdesk.api.portal.assign_ticket", data).then(function (result) {
			NX.ui.toast("Penugasan berhasil", "green");
			loadTicket();
		}).catch(function (err) {
			NX.ui.toast("Gagal: " + err.message, "red");
			// Re-enable buttons on error
			assignBtns.forEach(function (btn) {
				btn.disabled = false;
			});
		});
	}

	function addWorklog(form, submitBtn) {
		var formData = new FormData(form);
		var data = {
			name: ticketId,
			aktivitas: formData.get("aktivitas")
		};

		var hasil = formData.get("hasil");
		if (hasil && hasil.trim()) {
			data.hasil = hasil;
		}

		var durasi = formData.get("durasi_menit");
		if (durasi && durasi.trim()) {
			data.durasi_menit = parseInt(durasi);
		}

		if (!data.aktivitas || !data.aktivitas.trim()) {
			NX.ui.toast("Aktivitas wajib diisi", "red");
			return;
		}

		submitBtn.disabled = true;
		submitBtn.textContent = "Menyimpan...";

		NX.api.post("nexthd.next_helpdesk.api.portal.add_worklog", data).then(function (result) {
			NX.ui.toast("Catatan berhasil ditambahkan", "green");
			form.reset();
			submitBtn.disabled = false;
			submitBtn.textContent = "Simpan";
			loadTicket();
		}).catch(function (err) {
			NX.ui.toast("Gagal: " + err.message, "red");
			submitBtn.disabled = false;
			submitBtn.textContent = "Simpan";
		});
	}

	function getStatusColor(status) {
		switch (status) {
			case "Baru": return "blue";
			case "Sedang Dikerjakan": return "orange";
			case "Menunggu User": return "yellow";
			case "Selesai": return "green";
			case "Ditutup": return "grey";
			default: return "";
		}
	}

	function getPriorityColor(priority) {
		switch (priority) {
			case "Kritis": return "red";
			case "Tinggi": return "orange";
			case "Sedang": return "yellow";
			case "Rendah": return "grey";
			default: return "";
		}
	}

	// Load session first
	NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info").then(function (sessionData) {
		session = sessionData;
		NX.ui.renderNav(session);
		loadTicket();
	}).catch(function (err) {
		content.textContent = "";
		NX.ui.empty(content, "Gagal memuat: " + err.message);
	});
})();
