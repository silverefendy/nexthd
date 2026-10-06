(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	var content = document.getElementById("nx-content");
	if (!main || !content) return;

	var options = null;
	var session = null;

	function loadForm() {
		NX.api.get("nexthd.next_helpdesk.api.portal.get_problem_options").then(function (opts) {
			options = opts;
			return NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info");
		}).then(function (sess) {
			session = sess;
			NX.ui.renderNav(session);

			// Check permission
			if (!session.can_create_problem) {
				NX.ui.empty(content, "Anda tidak memiliki izin untuk membuat Problem");
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

		// Title
		var titleField = createTextField("Title", "title", true, 140);
		form.appendChild(titleField);

		// Priority
		var priorityField = createSelectField("Priority", "priority", options.priority, true, "Pilih prioritas...");
		form.appendChild(priorityField);

		// Category
		var categoryField = createSelectField("Kategori", "category", options.categories, false, "-- Pilih --");
		form.appendChild(categoryField);

		// Related Asset
		var assetField = createSearchField("Aset Terkait", "related_asset", "", false, "asset");
		form.appendChild(assetField);

		// Root Cause
		var rootCauseField = createTextareaField("Root Cause", "root_cause", false, 20000);
		form.appendChild(rootCauseField);

		// Workaround
		var workaroundField = createTextareaField("Workaround", "workaround", false, 20000);
		form.appendChild(workaroundField);

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
		submitBtn.textContent = "Buat Problem";
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

	function createSelectField(label, name, options, required, defaultText) {
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
		defaultOpt.textContent = defaultText || "-- Pilih --";
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

	function createSearchField(label, name, defaultValue, required, type) {
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
		input.placeholder = "Cari...";
		input.autocomplete = "off";

		var resultsDiv = document.createElement("div");
		resultsDiv.className = "nx-search-results";
		resultsDiv.style.display = "none";
		resultsDiv.style.position = "absolute";
		resultsDiv.style.zIndex = "1000";
		resultsDiv.style.background = "#fff";
		resultsDiv.style.border = "1px solid #ccc";
		resultsDiv.style.maxHeight = "200px";
		resultsDiv.style.overflowY = "auto";

		var debounceTimer = null;

		input.addEventListener("input", function () {
			var query = input.value;
			if (query.length < 2) {
				resultsDiv.style.display = "none";
				return;
			}

			clearTimeout(debounceTimer);
			debounceTimer = setTimeout(function () {
				var endpoint = type === "asset" ? "nexthd.next_helpdesk.api.portal.search_assets" : "nexthd.next_helpdesk.api.portal.search_users";
				NX.api.get(endpoint, { query: query }).then(function (result) {
					resultsDiv.innerHTML = "";
					var items = type === "asset" ? result.assets : result.users;

					if (items && items.length > 0) {
						items.forEach(function (item) {
							var option = document.createElement("div");
							option.style.padding = "0.5rem";
							option.style.cursor = "pointer";
							option.textContent = type === "asset" ? (item.asset_name || item.name) : (item.full_name || item.name);
							option.addEventListener("click", function () {
								input.value = item.name;
								resultsDiv.style.display = "none";
							});
							resultsDiv.appendChild(option);
						});
						resultsDiv.style.display = "block";
					} else {
						resultsDiv.style.display = "none";
					}
				}).catch(function (err) {
					console.error("Search error:", err);
				});
			}, 300);
		});

		input.addEventListener("blur", function () {
			setTimeout(function () {
				resultsDiv.style.display = "none";
			}, 200);
		});

		div.appendChild(input);
		div.appendChild(resultsDiv);

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
		if (!data.title || !data.title.trim()) {
			showError(errorDiv, "Title wajib diisi");
			return;
		}

		if (!data.priority || !data.priority.trim()) {
			showError(errorDiv, "Priority wajib diisi");
			return;
		}

		// Disable button
		submitBtn.disabled = true;
		submitBtn.textContent = "Mengirim...";

		NX.api.post("nexthd.next_helpdesk.api.portal.buat_problem", { data: data }).then(function (result) {
			NX.ui.toast("Problem berhasil dibuat", "green");
			window.location.href = "/nexthd/problem?id=" + result.problem_name;
		}).catch(function (err) {
			showError(errorDiv, err.message);
			submitBtn.disabled = false;
			submitBtn.textContent = "Buat Problem";
		});
	}

	function showError(errorDiv, message) {
		errorDiv.textContent = message;
		errorDiv.style.display = "block";
		errorDiv.className = "nx-badge nx-badge--red";
	}

	loadForm();
})();
