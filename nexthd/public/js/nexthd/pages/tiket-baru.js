(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	var options = null;
	var session = null;

	function loadForm() {
		NX.api.get("nexthd.next_helpdesk.api.portal.get_ticket_options").then(function (opts) {
			options = opts;
			return NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info");
		}).then(function (sess) {
			session = sess;
			NX.ui.renderNav(session);

			// Check permission
			if (!session.can_create) {
				NX.ui.empty(content, "Anda tidak memiliki izin untuk membuat tiket");
				return;
			}

			renderForm();
		}).catch(function (err) {
			content.textContent = "";
			NX.ui.empty(content, "Gagal memuat: " + err.message);
		});
	}

	function renderForm() {
		var wrap = document.createElement("div");
		wrap.className = "nx-wrap";

		var form = document.createElement("form");
		form.className = "nx-card";
		form.noValidate = true;

		// Tipe Tiket
		var typeField = createSelectField("Tipe Tiket", "ticket_type", options.ticket_type, true);
		form.appendChild(typeField);

		// Subjek
		var subjectField = createTextField("Subjek", "subject", true, 140);
		form.appendChild(subjectField);

		// Deskripsi
		var descField = createTextareaField("Deskripsi", "description", false, 20000);
		form.appendChild(descField);

		// Kategori
		var categoryField = createSelectField("Kategori", "category", options.categories, options.required.includes("category"));
		form.appendChild(categoryField);

		// Impact
		var impactField = createSelectField("Impact", "impact", options.impact, options.required.includes("impact"));
		form.appendChild(impactField);

		// Urgency
		var urgencyField = createSelectField("Urgency", "urgency", options.urgency, options.required.includes("urgency"));
		form.appendChild(urgencyField);

		// Pelapor
		var requestedByField = createLinkField("Pelapor", "requested_by", session.user, true, "User");
		form.appendChild(requestedByField);

		// Aset Terkait
		var assetField = createLinkField("Aset Terkait", "affected_asset", "", false, "NextHD Asset");
		form.appendChild(assetField);

		// Tim
		var teamField = createLinkField("Tim", "team", "", false, "NextHD Team");
		form.appendChild(teamField);

		// Ditugaskan ke
		var assignedToField = createLinkField("Ditugaskan ke", "assigned_to", "", false, "User");
		form.appendChild(assignedToField);

		// Note about priority
		var note = document.createElement("p");
		note.className = "nx-mono";
		note.style.fontSize = "0.9rem";
		note.style.color = "#666";
		note.textContent = "Prioritas dihitung otomatis dari Impact dan Urgency.";
		form.appendChild(note);

		// Error message container
		var errorDiv = document.createElement("div");
		errorDiv.id = "nx-form-error";
		errorDiv.className = "nx-badge";
		errorDiv.style.display = "none";
		errorDiv.style.marginBottom = "1rem";
		form.appendChild(errorDiv);

		// Submit button
		var submitBtn = document.createElement("button");
		submitBtn.type = "submit";
		submitBtn.className = "nx-btn";
		submitBtn.textContent = "Buat Tiket";
		form.appendChild(submitBtn);

		form.addEventListener("submit", function (e) {
			e.preventDefault();
			submitForm(form, submitBtn, errorDiv);
		});

		wrap.appendChild(form);
		content.appendChild(wrap);
	}

	function createTextField(label, name, required, maxLength) {
		var div = document.createElement("div");
		div.className = "nx-field";

		var labelEl = document.createElement("label");
		labelEl.textContent = label + (required ? " *" : "");
		div.appendChild(labelEl);

		var input = document.createElement("input");
		input.type = "text";
		input.name = name;
		input.required = required;
		if (maxLength) {
			input.maxLength = maxLength;
		}
		div.appendChild(input);

		return div;
	}

	function createTextareaField(label, name, required, maxLength) {
		var div = document.createElement("div");
		div.className = "nx-field";

		var labelEl = document.createElement("label");
		labelEl.textContent = label + (required ? " *" : "");
		div.appendChild(labelEl);

		var textarea = document.createElement("textarea");
		textarea.name = name;
		textarea.required = required;
		if (maxLength) {
			textarea.maxLength = maxLength;
		}
		textarea.rows = 5;
		div.appendChild(textarea);

		return div;
	}

	function createSelectField(label, name, options, required) {
		var div = document.createElement("div");
		div.className = "nx-field";

		var labelEl = document.createElement("label");
		labelEl.textContent = label + (required ? " *" : "");
		div.appendChild(labelEl);

		var select = document.createElement("select");
		select.name = name;
		select.required = required;

		var defaultOpt = document.createElement("option");
		defaultOpt.value = "";
		defaultOpt.textContent = "-- Pilih --";
		select.appendChild(defaultOpt);

		if (options) {
			options.forEach(function (opt) {
				var option = document.createElement("option");
				option.value = opt;
				option.textContent = opt;
				select.appendChild(option);
			});
		}

		div.appendChild(select);
		return div;
	}

	function createLinkField(label, name, defaultValue, required, doctype) {
		var div = document.createElement("div");
		div.className = "nx-field";

		var labelEl = document.createElement("label");
		labelEl.textContent = label + (required ? " *" : "");
		div.appendChild(labelEl);

		var input = document.createElement("input");
		input.type = "text";
		input.name = name;
		input.value = defaultValue;
		input.required = required;
		input.placeholder = "Cari " + doctype + "...";
		div.appendChild(input);

		return div;
	}

	function submitForm(form, submitBtn, errorDiv) {
		var formData = new FormData(form);
		var data = {};
		var isValid = true;

		for (var pair of formData.entries()) {
			data[pair[0]] = pair[1];
		}

		// Client-side validation
		if (!data.subject || !data.subject.trim()) {
			showError(errorDiv, "Subjek wajib diisi");
			return;
		}
		if (!data.ticket_type) {
			showError(errorDiv, "Tipe tiket wajib dipilih");
			return;
		}

		// Disable button
		submitBtn.disabled = true;
		submitBtn.textContent = "Mengirim...";

		NX.api.post("nexthd.next_helpdesk.api.portal.create_ticket", { data: data }).then(function (result) {
			NX.ui.toast("Tiket berhasil dibuat", "green");
			window.location.href = "/nexthd/tiket?id=" + result.name;
		}).catch(function (err) {
			showError(errorDiv, err.message);
			submitBtn.disabled = false;
			submitBtn.textContent = "Buat Tiket";
		});
	}

	function showError(errorDiv, message) {
		errorDiv.textContent = message;
		errorDiv.style.display = "block";
		errorDiv.className = "nx-badge nx-badge--red";
	}

	loadForm();
})();
