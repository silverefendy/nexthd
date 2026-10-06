(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	var currentPage = 1;
	var currentView = "all";
	var currentFilters = {
		status: "",
		priority: "",
		ticket_type: "",
		category: ""
	};
	var currentSearch = "";
	var currentOrderBy = "modified desc";
	var options = null;
	var debounceTimer = null;

	function loadTickets() {
		NX.ui.setLoading(content, true);

		var params = {
			view: currentView,
			order_by: currentOrderBy,
			page: currentPage,
			page_size: 20
		};

		if (currentFilters.status) params.status = currentFilters.status;
		if (currentFilters.priority) params.priority = currentFilters.priority;
		if (currentFilters.ticket_type) params.ticket_type = currentFilters.ticket_type;
		if (currentFilters.category) params.category = currentFilters.category;
		if (currentSearch) params.search = currentSearch;

		NX.api.get("nexthd.next_helpdesk.api.portal.list_tickets", params).then(function (result) {
			content.textContent = "";
			renderQueue(result);
		}).catch(function (err) {
			content.textContent = "";
			NX.ui.empty(content, "Gagal memuat: " + err.message);
			var retryBtn = document.createElement("button");
			retryBtn.className = "nx-btn";
			retryBtn.textContent = "Coba lagi";
			retryBtn.addEventListener("click", loadTickets);
			content.appendChild(retryBtn);
		});
	}

	function renderQueue(result) {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		// Tab tampilan
		var tabs = document.createElement("div");
		tabs.className = "nx-card";
		var viewTabs = [
			{ value: "all", label: "Semua" },
			{ value: "mine", label: "Ditugaskan ke saya" },
			{ value: "unassigned", label: "Belum ditugaskan" },
			{ value: "overdue", label: "Lewat SLA" }
		];
		viewTabs.forEach(function (vt) {
			var btn = document.createElement("button");
			btn.className = "nx-btn";
			if (currentView === vt.value) {
				btn.className += " nx-btn--alt";
			}
			btn.textContent = vt.label;
			btn.addEventListener("click", function () {
				currentView = vt.value;
				currentPage = 1;
				loadTickets();
			});
			tabs.appendChild(btn);
		});
		wrap.appendChild(tabs);

		// Filter dan cari
		var filterRow = document.createElement("div");
		filterRow.className = "nx-card";

		var searchInput = document.createElement("input");
		searchInput.type = "text";
		searchInput.placeholder = "Cari tiket...";
		searchInput.value = currentSearch;
		searchInput.addEventListener("input", function () {
			currentSearch = searchInput.value;
			clearTimeout(debounceTimer);
			debounceTimer = setTimeout(function () {
				currentPage = 1;
				loadTickets();
			}, 300);
		});
		filterRow.appendChild(searchInput);

		// Filter dropdowns
		if (options) {
			var fieldLabels = {
				"status": "Status",
				"priority": "Prioritas",
				"ticket_type": "Jenis Tiket",
				"category": "Kategori"
			};

			["status", "priority", "ticket_type", "category"].forEach(function (field) {
				var select = document.createElement("select");
				select.className = "nx-field";
				var defaultOpt = document.createElement("option");
				defaultOpt.value = "";
				defaultOpt.textContent = fieldLabels[field] || field;
				select.appendChild(defaultOpt);

				var opts = field === "category" ? options.categories : options[field];
				if (opts) {
					opts.forEach(function (opt) {
						var option = document.createElement("option");
						option.value = opt;
						option.textContent = opt;
						if (currentFilters[field] === opt) {
							option.selected = true;
						}
						select.appendChild(option);
					});
				}

				select.addEventListener("change", function () {
					currentFilters[field] = select.value;
					currentPage = 1;
					loadTickets();
				});
				filterRow.appendChild(select);
			});
		}

		// Order by
		var orderSelect = document.createElement("select");
		orderSelect.className = "nx-field";
		var orderOptions = [
			{ value: "modified desc", label: "Terakhir diubah" },
			{ value: "creation desc", label: "Terbaru dibuat" },
			{ value: "sla_resolution_by asc", label: "SLA terdekat" }
		];
		orderOptions.forEach(function (oo) {
			var option = document.createElement("option");
			option.value = oo.value;
			option.textContent = oo.label;
			if (currentOrderBy === oo.value) {
				option.selected = true;
			}
			orderSelect.appendChild(option);
		});
		orderSelect.addEventListener("change", function () {
			currentOrderBy = orderSelect.value;
			currentPage = 1;
			loadTickets();
		});
		filterRow.appendChild(orderSelect);

		wrap.appendChild(filterRow);

		// Tabel
		if (!result.rows || result.rows.length === 0) {
			var emptyMsg = document.createElement("p");
			emptyMsg.textContent = "Tidak ada tiket";
			emptyMsg.style.padding = "1rem";
			wrap.appendChild(emptyMsg);
		} else {
			var columns = ["ID", "Subjek", "Status", "Prioritas", "Kategori", "Ditugaskan ke", "SLA Resolusi", "Diubah"];
			var rows = result.rows.map(function (ticket) {
				var idLink = document.createElement("a");
				idLink.href = "/nexthd/tiket?id=" + ticket.name;
				idLink.textContent = ticket.name;

				var statusBadge = NX.ui.badge(ticket.status, getStatusColor(ticket.status));
				var priorityBadge = NX.ui.badge(ticket.priority, getPriorityColor(ticket.priority));

				var slaText = "-";
				if (ticket.sla_resolution_by && ticket.status !== "Selesai" && ticket.status !== "Ditutup") {
					slaText = fmtDateTimeShort(ticket.sla_resolution_by);
					var isOverdue = ticket.sla_resolution_by < result.server_now;
					if (isOverdue) {
						var slaSpan = document.createElement("span");
						slaSpan.textContent = slaText;
						slaSpan.style.color = "red";
						slaSpan.style.fontWeight = "bold";
						slaText = slaSpan;
					}
				}

				return [
					idLink,
					ticket.subject,
					statusBadge,
					priorityBadge,
					ticket.category || "-",
					ticket.assigned_to ? ticket.assigned_to.split("@")[0] : "-",
					slaText,
					fmtDateTimeShort(ticket.modified)
				];
			});

			var table = NX.ui.renderTable(columns, rows);
			wrap.appendChild(table);

			// Pager
			var pager = NX.ui.renderPager(result.total, result.page, result.page_size, function (newPage) {
				currentPage = newPage;
				loadTickets();
			});
			wrap.appendChild(pager);
		}

		content.appendChild(wrap);
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

	function fmtDateTimeShort(str) {
		if (!str) return "";
		var parts = str.split(" ");
		if (parts.length < 2) return str;
		var dateParts = parts[0].split("-");
		if (dateParts.length < 3) return str;
		var year = dateParts[0];
		var month = dateParts[1];
		var day = dateParts[2];
		var timeParts = parts[1].split(":");
		if (timeParts.length < 2) return str;
		var hour = timeParts[0];
		var minute = timeParts[1];

		var months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
		var monthName = months[parseInt(month, 10) - 1] || month;

		return day + " " + monthName + " " + year + ", " + hour + ":" + minute;
	}

	// Read URL parameters after options are loaded
	function readUrlParams() {
		var urlParams = new URLSearchParams(window.location.search);

		// Read view parameter (only allowed values)
		var viewParam = urlParams.get("view");
		var allowedViews = ["all", "mine", "unassigned", "overdue"];
		if (viewParam && allowedViews.indexOf(viewParam) !== -1) {
			currentView = viewParam;
		}

		// Read filter parameters (only if they exist in options)
		var filterFields = ["status", "priority", "ticket_type", "category"];
		filterFields.forEach(function (field) {
			var paramValue = urlParams.get(field);
			if (paramValue) {
				var opts = field === "category" ? options.categories : options[field];
				if (opts && opts.indexOf(paramValue) !== -1) {
					currentFilters[field] = paramValue;
				}
			}
		});

		// Read search parameter (max 100 characters)
		var searchParam = urlParams.get("search");
		if (searchParam) {
			currentSearch = searchParam.substring(0, 100);
		}
	}

	// Load options dan session
	NX.api.get("nexthd.next_helpdesk.api.portal.get_ticket_options").then(function (opts) {
		options = opts;
		readUrlParams();
		return NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info");
	}).then(function (session) {
		NX.ui.renderNav(session);
		loadTickets();
	}).catch(function (err) {
		content.textContent = "";
		NX.ui.empty(content, "Gagal memuat: " + err.message);
	});
})();
