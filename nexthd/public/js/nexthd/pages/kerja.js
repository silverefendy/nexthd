(function () {
	"use strict";

	var main = document.getElementById("nx-main");
	if (!main) return;

	NX.ui.setLoading(main, true);

	NX.api.get("nexthd.next_helpdesk.api.portal.get_session_info").then(function (session) {
		main.textContent = "";
		NX.ui.renderNav(session);

		var card = document.createElement("div");
		card.className = "nx-card";

		var h2 = document.createElement("h2");
		h2.textContent = "Halo, " + session.full_name;
		card.appendChild(h2);

		var roles = document.createElement("p");
		roles.className = "nx-mono";
		roles.textContent = "Peran: " + session.roles.join(", ");
		card.appendChild(roles);

		var message = document.createElement("p");
		message.textContent = "Antrian tiket menyusul di tahap berikutnya.";
		card.appendChild(message);

		main.appendChild(card);
	}).catch(function (err) {
		main.textContent = "";
		NX.ui.empty(main, "Gagal memuat: " + err.message);
	});
})();
