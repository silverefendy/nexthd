(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	function loadDashboard() {
		NX.ui.setLoading(content, true);

		NX.api.get("nexthd.next_helpdesk.api.portal.get_dashboard_counts").then(function (result) {
			content.textContent = "";
			renderDashboard(result);
		}).catch(function (err) {
			content.textContent = "";
			NX.ui.empty(content, "Gagal memuat: " + err.message);
			var retryBtn = document.createElement("button");
			retryBtn.className = "nx-btn";
			retryBtn.textContent = "Coba lagi";
			retryBtn.addEventListener("click", loadDashboard);
			content.appendChild(retryBtn);
		});
	}

	function renderDashboard(data) {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		// Tiket section
		var tiketSection = document.createElement("section");
		tiketSection.className = "nx-dashboard-section";
		var tiketHeader = document.createElement("h2");
		tiketHeader.textContent = "Tiket";
		tiketSection.appendChild(tiketHeader);

		var tiketGrid = document.createElement("div");
		tiketGrid.className = "nx-dashboard-grid";

		var tiketCards = [
			{ label: "Baru", key: "baru", href: "/nexthd/kerja?status=Baru" },
			{ label: "Sedang Dikerjakan", key: "sedang_dikerjakan", href: "/nexthd/kerja?status=Sedang%20Dikerjakan" },
			{ label: "Menunggu User", key: "menunggu_user", href: "/nexthd/kerja?status=Menunggu%20User" },
			{ label: "Lewat SLA", key: "lewat_sla", href: "/nexthd/kerja?view=overdue", highlight: true },
			{ label: "Belum ditugaskan", key: "belum_ditugaskan", href: "/nexthd/kerja?view=unassigned" }
		];

		tiketCards.forEach(function (card) {
			var cardEl = createCard(card.label, data.tiket[card.key], card.href, card.highlight);
			tiketGrid.appendChild(cardEl);
		});

		tiketSection.appendChild(tiketGrid);
		wrap.appendChild(tiketSection);

		// Problem section
		var problemSection = document.createElement("section");
		problemSection.className = "nx-dashboard-section";
		var problemHeader = document.createElement("h2");
		problemHeader.textContent = "Problem";
		problemSection.appendChild(problemHeader);

		var problemGrid = document.createElement("div");
		problemGrid.className = "nx-dashboard-grid";

		var problemCards = [
			{ label: "Terbuka", key: "terbuka", href: "/nexthd/problem?status=Terbuka" },
			{ label: "Investigasi", key: "investigasi", href: "/nexthd/problem?status=Investigasi" },
			{ label: "Known Error", key: "known_error", href: "/nexthd/problem?status=Known%20Error" }
		];

		problemCards.forEach(function (card) {
			var cardEl = createCard(card.label, data.problem[card.key], card.href);
			problemGrid.appendChild(cardEl);
		});

		problemSection.appendChild(problemGrid);
		wrap.appendChild(problemSection);

		// Ringkasan section (bukan tautan)
		var summarySection = document.createElement("section");
		summarySection.className = "nx-dashboard-section";
		var summaryHeader = document.createElement("h2");
		summaryHeader.textContent = "Ringkasan";
		summarySection.appendChild(summaryHeader);

		var summaryGrid = document.createElement("div");
		summaryGrid.className = "nx-dashboard-grid";

		var summaryCards = [
			{ label: "Total Tiket", value: data.tiket.total },
			{ label: "Total Problem", value: data.problem.total },
			{ label: "Known Error", value: data.known_error_total },
			{ label: "Aset", value: data.aset_total }
		];

		summaryCards.forEach(function (card) {
			var cardEl = createSummaryCard(card.label, card.value);
			summaryGrid.appendChild(cardEl);
		});

		summarySection.appendChild(summaryGrid);
		wrap.appendChild(summarySection);

		content.appendChild(wrap);
	}

	function createCard(label, value, href, highlight) {
		var card = document.createElement("a");
		card.className = "nx-dashboard-card";
		if (highlight && value > 0) {
			card.className += " nx-dashboard-card--alert";
		}
		card.href = href;

		var number = document.createElement("div");
		number.className = "nx-dashboard-card__number";
		number.textContent = value !== null ? value : "-";
		card.appendChild(number);

		var labelEl = document.createElement("div");
		labelEl.className = "nx-dashboard-card__label";
		labelEl.textContent = label;
		card.appendChild(labelEl);

		return card;
	}

	function createSummaryCard(label, value) {
		var card = document.createElement("div");
		card.className = "nx-dashboard-card nx-dashboard-card--summary";

		var number = document.createElement("div");
		number.className = "nx-dashboard-card__number";
		number.textContent = value !== null ? value : "-";
		card.appendChild(number);

		var labelEl = document.createElement("div");
		labelEl.className = "nx-dashboard-card__label";
		labelEl.textContent = label;
		card.appendChild(labelEl);

		return card;
	}

	// Load session dan dashboard
	NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info").then(function (session) {
		NX.ui.renderNav(session);
		loadDashboard();
	}).catch(function (err) {
		content.textContent = "";
		NX.ui.empty(content, "Gagal memuat: " + err.message);
	});
})();
