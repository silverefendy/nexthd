(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	// Get problem ID from query string
	var urlParams = new URLSearchParams(window.location.search);
	var problemId = urlParams.get("id");

	var listState = { status: "", priority: "", page: 1 };
	function listParams() {
		var p = { page: listState.page };
		if (listState.status) { p.status = listState.status; }
		if (listState.priority) { p.priority = listState.priority; }
		return p;
	}

	// Read URL parameters for list mode
	function readUrlParams() {
		var urlParams = new URLSearchParams(window.location.search);

		// Read status parameter (only allowed values)
		var statusParam = urlParams.get("status");
		var allowedStatuses = ["Terbuka", "Investigasi", "Known Error", "Selesai", "Ditutup"];
		if (statusParam && allowedStatuses.indexOf(statusParam) !== -1) {
			listState.status = statusParam;
		}

		// Read priority parameter (only allowed values)
		var priorityParam = urlParams.get("priority");
		var allowedPriorities = ["Kritis", "Tinggi", "Sedang", "Rendah"];
		if (priorityParam && allowedPriorities.indexOf(priorityParam) !== -1) {
			listState.priority = priorityParam;
		}

		// Read page parameter (must be integer >= 1)
		var pageParam = urlParams.get("page");
		if (pageParam) {
			var pageNum = parseInt(pageParam, 10);
			if (!isNaN(pageNum) && pageNum >= 1) {
				listState.page = pageNum;
			}
		}
	}

	if (!problemId) {
		// Show list of problems
		readUrlParams();
		loadProblemList();
	} else {
		// Show problem detail
		loadProblemDetail(problemId);
	}

	function loadProblemList() {
		NX.ui.setLoading(content, true);

		NX.api.get("nexthd.next_helpdesk.api.portal.list_problems", listParams()).then(function (result) {
			content.textContent = "";
			renderProblemList(result);
		}).catch(function (err) {
			content.textContent = "";
			NX.ui.empty(content, "Gagal memuat: " + err.message);
		});
	}

	function renderProblemList(data) {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		// Header
		var header = document.createElement("div");
		header.className = "nx-page-head";
		var h1 = document.createElement("h1");
		h1.textContent = "Daftar Problem";
		// Judul halaman sudah ada di template (problem.html)
		wrap.appendChild(header);

		// Filter form
		var filterCard = document.createElement("div");
		filterCard.className = "nx-card";
		filterCard.innerHTML = "<h3>Filter</h3>";

		var filterForm = document.createElement("form");
		filterForm.noValidate = true;

		// Status filter
		var statusDiv = document.createElement("div");
		statusDiv.className = "nx-field";
		var statusLabel = document.createElement("label");
		statusLabel.textContent = "Status";
		statusDiv.appendChild(statusLabel);
		var statusSelect = document.createElement("select");
		statusSelect.name = "status";
		statusSelect.className = "nx-field";
		var statusDefault = document.createElement("option");
		statusDefault.value = "";
		statusDefault.textContent = "-- Semua --";
		statusSelect.appendChild(statusDefault);
		["Terbuka", "Investigasi", "Known Error", "Selesai", "Ditutup"].forEach(function (opt) {
			var option = document.createElement("option");
			option.value = opt;
			option.textContent = opt;
			statusSelect.appendChild(option);
		});
		statusDiv.appendChild(statusSelect);
		filterForm.appendChild(statusDiv);

		// Priority filter
		var priorityDiv = document.createElement("div");
		priorityDiv.className = "nx-field";
		var priorityLabel = document.createElement("label");
		priorityLabel.textContent = "Prioritas";
		priorityDiv.appendChild(priorityLabel);
		var prioritySelect = document.createElement("select");
		prioritySelect.name = "priority";
		prioritySelect.className = "nx-field";
		var priorityDefault = document.createElement("option");
		priorityDefault.value = "";
		priorityDefault.textContent = "-- Semua --";
		prioritySelect.appendChild(priorityDefault);
		["Kritis", "Tinggi", "Sedang", "Rendah"].forEach(function (opt) {
			var option = document.createElement("option");
			option.value = opt;
			option.textContent = opt;
			prioritySelect.appendChild(option);
		});
		priorityDiv.appendChild(prioritySelect);
		filterForm.appendChild(priorityDiv);
		statusSelect.value = listState.status;
		prioritySelect.value = listState.priority;

		// Submit button
		var submitBtn = document.createElement("button");
		submitBtn.type = "submit";
		submitBtn.className = "nx-btn";
		submitBtn.textContent = "Terapkan Filter";
		filterForm.appendChild(submitBtn);

		filterForm.addEventListener("submit", function (e) {
			e.preventDefault();
			var status = statusSelect.value;
			var priority = prioritySelect.value;
			listState.status = status;
			listState.priority = priority;
			listState.page = 1;
			loadProblemList();
		});

		filterCard.appendChild(filterForm);
		wrap.appendChild(filterCard);

		// Results table
		var tableCard = document.createElement("div");
		tableCard.className = "nx-card";
		tableCard.innerHTML = "<h3>Hasil</h3>";

		var tableWrap = document.createElement("div");
		tableWrap.className = "nx-table-wrap";

		var table = document.createElement("table");
		table.className = "nx-table";

		var thead = document.createElement("thead");
		var headerRow = document.createElement("tr");
		["ID", "Judul", "Status", "Prioritas", "Kategori", "Aset"].forEach(function (col) {
			var th = document.createElement("th");
			th.textContent = col;
			headerRow.appendChild(th);
		});
		thead.appendChild(headerRow);
		table.appendChild(thead);

		var tbody = document.createElement("tbody");
		if (data.rows && data.rows.length > 0) {
			data.rows.forEach(function (row) {
				var tr = document.createElement("tr");
				var tdId = document.createElement("td");
				var link = document.createElement("a");
				link.href = "/nexthd/problem?id=" + encodeURIComponent(row.name);
				link.textContent = row.name;
				tdId.appendChild(link);
				tr.appendChild(tdId);

				[row.title, row.status, row.priority, row.category || "-", row.related_asset || "-"].forEach(function (cell) {
					var td = document.createElement("td");
					td.textContent = cell;
					tr.appendChild(td);
				});
				tbody.appendChild(tr);
			});
		} else {
			var tr = document.createElement("tr");
			var td = document.createElement("td");
			td.colSpan = 6;
			td.textContent = "Tidak ada data";
			tr.appendChild(td);
			tbody.appendChild(tr);
		}
		table.appendChild(tbody);
		tableWrap.appendChild(table);
		tableCard.appendChild(tableWrap);

		var totalPages = Math.max(1, Math.ceil((data.total || 0) / (data.page_size || 20)));
		var pager = document.createElement("div");
		pager.style.marginTop = "0.75rem";
		var pagerInfo = document.createElement("span");
		pagerInfo.textContent = "Halaman " + listState.page + " dari " + totalPages + " (" + (data.total || 0) + " problem) ";
		pager.appendChild(pagerInfo);
		var prevBtn = document.createElement("button");
		prevBtn.type = "button";
		prevBtn.className = "nx-btn";
		prevBtn.textContent = "Sebelumnya";
		prevBtn.disabled = listState.page <= 1;
		prevBtn.addEventListener("click", function () { listState.page -= 1; loadProblemList(); });
		pager.appendChild(prevBtn);
		pager.appendChild(document.createTextNode(" "));
		var nextBtn = document.createElement("button");
		nextBtn.type = "button";
		nextBtn.className = "nx-btn";
		nextBtn.textContent = "Berikutnya";
		nextBtn.disabled = listState.page >= totalPages;
		nextBtn.addEventListener("click", function () { listState.page += 1; loadProblemList(); });
		pager.appendChild(nextBtn);
		tableCard.appendChild(pager);
		wrap.appendChild(tableCard);

		content.appendChild(wrap);
	}

	function applyFilter(status, priority) {
		NX.ui.setLoading(content, true);

		var params = {};
		if (status) {
			params.status = status;
		}
		if (priority) {
			params.priority = priority;
		}

		NX.api.get("nexthd.next_helpdesk.api.portal.list_problems", params).then(function (result) {
			content.textContent = "";
			renderProblemList(result);
		}).catch(function (err) {
			content.textContent = "";
			NX.ui.empty(content, "Gagal memuat: " + err.message);
		});
	}

	function loadProblemDetail(problemId) {
		NX.ui.setLoading(content, true);

		NX.api.get("nexthd.next_helpdesk.api.portal.get_problem", { name: problemId }).then(function (problem) {
			content.textContent = "";
			renderProblemDetail(problem);
		}).catch(function (err) {
			content.textContent = "";
			if (err.message === "Anda tidak memiliki izin untuk aksi ini" || err.message.includes("tidak ditemukan")) {
				NX.ui.empty(content, err.message);
			} else {
				NX.ui.empty(content, "Gagal memuat: " + err.message);
			}
			var backBtn = document.createElement("button");
			backBtn.className = "nx-btn";
			backBtn.textContent = "Kembali ke daftar";
			backBtn.addEventListener("click", function () {
				window.location.href = "/nexthd/problem";
			});
			content.appendChild(backBtn);
		});
	}

	function renderProblemDetail(problem) {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		// Header
		var header = document.createElement("div");
		header.className = "nx-page-head";
		var h1 = document.createElement("h1");
		h1.textContent = problem.title;
		header.appendChild(h1);

		var meta = document.createElement("div");
		meta.className = "nx-card";
		meta.style.marginBottom = "1rem";

		var idSpan = document.createElement("span");
		idSpan.textContent = problem.name;
		meta.appendChild(document.createTextNode("ID: "));
		meta.appendChild(idSpan);
		meta.appendChild(document.createTextNode(" | "));

		var statusBadge = NX.ui.badge(problem.status, getStatusColor(problem.status));
		meta.appendChild(statusBadge);
		meta.appendChild(document.createTextNode(" "));

		var priorityBadge = NX.ui.badge(problem.priority, getPriorityColor(problem.priority));
		meta.appendChild(priorityBadge);

		header.appendChild(meta);
		wrap.appendChild(header);

		// Info block
		var infoCard = document.createElement("div");
		infoCard.className = "nx-card";
		infoCard.innerHTML = "<h3>Informasi</h3>";

		var infoTable = document.createElement("table");
		infoTable.className = "nx-table";

		var infoFields = [
			{ label: "Kategori", value: problem.category || "-" },
			{ label: "Aset Terkait", value: problem.related_asset || "-" },
			{ label: "Known Error", value: problem.known_error || "-" },
			{ label: "Change Request", value: problem.change_request || "-" }
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

		// Root Cause
		if (problem.root_cause) {
			var rootCauseCard = document.createElement("div");
			rootCauseCard.className = "nx-card";
			rootCauseCard.innerHTML = "<h3>Root Cause</h3>";
			var rootCauseDiv = document.createElement("div");
			rootCauseDiv.innerHTML = problem.root_cause;
			rootCauseCard.appendChild(rootCauseDiv);
			wrap.appendChild(rootCauseCard);
		}

		// Workaround
		if (problem.workaround) {
			var workaroundCard = document.createElement("div");
			workaroundCard.className = "nx-card";
			workaroundCard.innerHTML = "<h3>Workaround</h3>";
			var workaroundDiv = document.createElement("div");
			workaroundDiv.innerHTML = problem.workaround;
			workaroundCard.appendChild(workaroundDiv);
			wrap.appendChild(workaroundCard);
		}

		// Related Tickets
		if (problem.related_tickets && problem.related_tickets.length > 0) {
			var ticketsCard = document.createElement("div");
			ticketsCard.className = "nx-card";
			ticketsCard.innerHTML = "<h3>Tiket Terkait</h3>";

			var ticketsTable = document.createElement("table");
			ticketsTable.className = "nx-table";

			var ticketsThead = document.createElement("thead");
			var ticketsHeaderRow = document.createElement("tr");
			["ID", "Subjek", "Status"].forEach(function (col) {
				var th = document.createElement("th");
				th.textContent = col;
				ticketsHeaderRow.appendChild(th);
			});
			ticketsThead.appendChild(ticketsHeaderRow);
			ticketsTable.appendChild(ticketsThead);

			var ticketsTbody = document.createElement("tbody");
			problem.related_tickets.forEach(function (ticket) {
				var tr = document.createElement("tr");
				var tdId = document.createElement("td");
				var link = document.createElement("a");
				link.href = "/nexthd/tiket?id=" + encodeURIComponent(ticket.ticket);
				link.textContent = ticket.ticket;
				tdId.appendChild(link);
				tr.appendChild(tdId);

				[ticket.subject || "-", ticket.status || "-"].forEach(function (cell) {
					var td = document.createElement("td");
					td.textContent = cell;
					tr.appendChild(td);
				});
				ticketsTbody.appendChild(tr);
			});
			ticketsTable.appendChild(ticketsTbody);
			var ticketsWrap = document.createElement("div");
			ticketsWrap.className = "nx-table-wrap";
			ticketsWrap.appendChild(ticketsTable);
			ticketsCard.appendChild(ticketsWrap);
			wrap.appendChild(ticketsCard);
		}

		// Photos
		if (problem.photos && problem.photos.length > 0) {
			var photosCard = document.createElement("div");
			photosCard.className = "nx-card";
			photosCard.innerHTML = "<h3>Foto/Gambar</h3>";

			var photosGrid = document.createElement("div");
			photosGrid.style.display = "grid";
			photosGrid.style.gridTemplateColumns = "repeat(auto-fill, minmax(200px, 1fr))";
			photosGrid.style.gap = "1rem";

			problem.photos.forEach(function (photo) {
				var photoDiv = document.createElement("div");
				photoDiv.style.border = "1px solid var(--border)";
				photoDiv.style.padding = "0.5rem";

				var img = document.createElement("img");
				img.src = photo.photo_preview;
				img.alt = photo.caption || "Foto";
				img.style.width = "100%";
				img.style.height = "auto";
				photoDiv.appendChild(img);

				if (photo.caption) {
					var caption = document.createElement("small");
					caption.textContent = photo.caption;
					caption.style.display = "block";
					caption.style.marginTop = "0.5rem";
					photoDiv.appendChild(caption);
				}

				photosGrid.appendChild(photoDiv);
			});

			photosCard.appendChild(photosGrid);
			wrap.appendChild(photosCard);
		}

		// Actions container
		var actionsContainer = document.createElement("div");
		actionsContainer.id = "nx-actions";
		wrap.appendChild(actionsContainer);

		// Back button
		var backBtn = document.createElement("button");
		backBtn.className = "nx-btn";
		backBtn.textContent = "Kembali ke daftar";
		backBtn.addEventListener("click", function () {
			window.location.href = "/nexthd/problem";
		});
		wrap.appendChild(backBtn);

		content.appendChild(wrap);

		// Load actions
		loadProblemActions(problemId);
	}

	function loadProblemActions(problemId) {
		NX.api.get("nexthd.next_helpdesk.api.portal.get_problem_actions", { name: problemId }).then(function (result) {
			renderProblemActions(result);
		}).catch(function (err) {
			console.error("Gagal memuat aksi:", err);
		});
	}

	function renderProblemActions(actions) {
		if (!actions) return;

		var actionsContainer = document.getElementById("nx-actions");
		if (!actionsContainer) return;

		if (actions.actions.length === 0) {
			return;
		}

		var actionsCard = document.createElement("div");
		actionsCard.className = "nx-card";
		actionsCard.innerHTML = "<h3>Aksi</h3>";

		actions.actions.forEach(function (actionItem) {
			var btn = document.createElement("button");
			btn.className = "nx-btn";
			btn.textContent = actionItem.action;
			btn.addEventListener("click", function () {
				doProblemAction(actionItem.action);
			});
			actionsCard.appendChild(btn);
		});

		actionsContainer.appendChild(actionsCard);
	}

	function doProblemAction(action) {
		var urlParams = new URLSearchParams(window.location.search);
		var problemId = urlParams.get("id");

		if (confirm("Apakah Anda yakin ingin melakukan aksi: " + action + "?")) {
			NX.api.post("nexthd.next_helpdesk.api.portal.do_problem_action", { name: problemId, action: action }).then(function (result) {
				NX.ui.toast("Aksi berhasil", "green");
				loadProblemDetail(problemId);
			}).catch(function (err) {
				NX.ui.toast("Gagal: " + err.message, "red");
			});
		}
	}

	function getStatusColor(status) {
		switch (status) {
			case "Terbuka": return "blue";
			case "Investigasi": return "orange";
			case "Known Error": return "yellow";
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
	NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info").then(function (session) {
		NX.ui.renderNav(session);
	}).catch(function (err) {
		content.textContent = "";
		NX.ui.empty(content, "Gagal memuat: " + err.message);
	});
})();
