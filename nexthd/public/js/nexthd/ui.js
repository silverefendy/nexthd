(function () {
	"use strict";

	var NX = window.NX || {};

	NX.ui = {
		FEATURES: {
			newTicket: true
		},

		esc: function (text) {
			var div = document.createElement("div");
			div.textContent = text;
			return div.innerHTML;
		},

		el: function (tag, attrs, children) {
			var el = document.createElement(tag);
			if (attrs) {
				for (var key in attrs) {
					if (key === "className") {
						el.className = attrs[key];
					} else if (key === "textContent") {
						el.textContent = attrs[key];
					} else {
						el.setAttribute(key, attrs[key]);
					}
				}
			}
			if (children) {
				if (typeof children === "string") {
					el.textContent = children;
				} else if (Array.isArray(children)) {
					children.forEach(function (child) {
						if (typeof child === "string") {
							el.appendChild(document.createTextNode(child));
						} else if (child instanceof HTMLElement) {
							el.appendChild(child);
						}
					});
				} else if (children instanceof HTMLElement) {
					el.appendChild(children);
				}
			}
			return el;
		},

		toast: function (msg, type) {
			var existing = document.querySelector(".nx-toast");
			if (existing) {
				existing.remove();
			}

			var toast = document.createElement("div");
			toast.className = "nx-toast";
			if (type) {
				toast.className += " nx-toast--" + type;
			}
			toast.textContent = msg;
			document.body.appendChild(toast);

			setTimeout(function () {
				toast.remove();
			}, 3000);
		},

		fmtDateTime: function (str) {
			if (!str) return "";
			var parts = str.split(" ");
			if (parts.length < 2) return str;
			var dateParts = parts[0].split("-");
			if (dateParts.length < 3) return str;
			var year = dateParts[0];
			var month = dateParts[1];
			var day = dateParts[2];
			var time = parts[1].split(".")[0];

			var months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
			var monthName = months[parseInt(month, 10) - 1] || month;

			return day + " " + monthName + " " + year + " " + time;
		},

		badge: function (text, color) {
			var span = document.createElement("span");
			span.className = "nx-badge";
			if (color) {
				span.className += " nx-badge--" + color;
			}
			span.textContent = text;
			return span;
		},

		renderNav: function (session) {
			var nav = document.getElementById("nx-nav");
			if (!nav) return;

			var wrap = document.createElement("div");
			wrap.className = "nx-wrap";

			var brand = document.createElement("b");
			brand.textContent = "NEXTHD//";
			wrap.appendChild(brand);

			var menu = document.createElement("div");
			var links = [
				{ href: "/nexthd", text: "Beranda" },
				{ href: "/nexthd/kerja", text: "Kerja" },
				{ href: "/nexthd/problem", text: "Problem" }
			];

			if (session.can_create && NX.ui.FEATURES.newTicket) {
				links.push({ href: "/nexthd/tiket-baru", text: "Tiket Baru" });
			}

			links.push({ href: "/desk/nexthd", text: "Desk" });

			links.forEach(function (link) {
				var a = document.createElement("a");
				a.href = link.href;
				a.textContent = link.text;
				menu.appendChild(a);
			});

			var logoutBtn = document.createElement("a");
			logoutBtn.href = "#";
			logoutBtn.textContent = "Keluar";
			logoutBtn.addEventListener("click", function (e) {
				e.preventDefault();
				NX.api.post("logout", {}).then(function () {
					window.location.href = "/login";
				}).catch(function (err) {
					NX.ui.toast("Gagal keluar: " + err.message);
				});
			});
			menu.appendChild(logoutBtn);

			wrap.appendChild(menu);
			nav.className = "nx-nav";
			nav.appendChild(wrap);
		},

		setLoading: function (node, isLoading) {
			if (!node) return;
			node.textContent = "";
			if (isLoading) {
				var div = document.createElement("div");
				div.className = "nx-loading";
				div.textContent = "Memuat";
				node.appendChild(div);
			}
		},

		empty: function (node, text) {
			if (!node) return;
			node.textContent = "";
			var div = document.createElement("div");
			div.className = "nx-empty";
			div.textContent = text || "Tidak ada data";
			node.appendChild(div);
		},

		renderTable: function (columns, rows) {
			var tableWrap = document.createElement("div");
			tableWrap.className = "nx-table-wrap";

			var table = document.createElement("table");
			table.className = "nx-table";

			var thead = document.createElement("thead");
			var headerRow = document.createElement("tr");
			columns.forEach(function (col) {
				var th = document.createElement("th");
				th.textContent = col;
				headerRow.appendChild(th);
			});
			thead.appendChild(headerRow);
			table.appendChild(thead);

			var tbody = document.createElement("tbody");
			rows.forEach(function (row) {
				var tr = document.createElement("tr");
				row.forEach(function (cell) {
					var td = document.createElement("td");
					if (typeof cell === "string") {
						td.textContent = cell;
					} else if (cell instanceof HTMLElement) {
						td.appendChild(cell);
					}
					tr.appendChild(td);
				});
				tbody.appendChild(tr);
			});
			table.appendChild(tbody);

			tableWrap.appendChild(table);
			return tableWrap;
		},

		renderPager: function (total, page, page_size, onPageChange) {
			var pager = document.createElement("div");
			pager.className = "nx-pager";

			var start = (page - 1) * page_size + 1;
			var end = Math.min(page * page_size, total);
			var info = document.createElement("span");
			info.textContent = start + "-" + end + " dari " + total;
			pager.appendChild(info);

			if (page > 1) {
				var prevBtn = document.createElement("button");
				prevBtn.className = "nx-btn";
				prevBtn.textContent = "Sebelumnya";
				prevBtn.addEventListener("click", function () {
					onPageChange(page - 1);
				});
				pager.appendChild(prevBtn);
			}

			if (end < total) {
				var nextBtn = document.createElement("button");
				nextBtn.className = "nx-btn";
				nextBtn.textContent = "Berikutnya";
				nextBtn.addEventListener("click", function () {
					onPageChange(page + 1);
				});
				pager.appendChild(nextBtn);
			}

			return pager;
		}
	};

	window.NX = NX;
})();
