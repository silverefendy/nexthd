(function () {
	"use strict";

	var NX = window.NX || {};

	NX.api = {
		get: function (method, params) {
			var url = "/api/method/" + method;
			var queryString = "";
			if (params) {
				queryString = Object.keys(params)
					.map(function (key) {
						return encodeURIComponent(key) + "=" + encodeURIComponent(JSON.stringify(params[key]));
					})
					.join("&");
			}
			if (queryString) {
				url += "?" + queryString;
			}

			return fetch(url, {
				method: "GET",
				credentials: "same-origin",
				headers: {
					"X-Frappe-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content")
				}
			}).then(function (response) {
				if (response.status === 401 || response.status === 403) {
					var currentPath = window.location.pathname;
					if (currentPath !== "/login") {
						window.location.href = "/login?redirect-to=" + encodeURIComponent(currentPath);
					}
					return Promise.reject(new Error("Sesi tidak valid"));
				}
				return response.json();
			}).then(function (data) {
				if (data.exc_type === "PermissionError") {
					window.location.href = "/login?redirect-to=" + encodeURIComponent(window.location.pathname);
					return Promise.reject(new Error("Izin tidak cukup"));
				}
				if (data._server_messages) {
					try {
						var messages = JSON.parse(data._server_messages);
						if (messages && messages.length > 0) {
							return Promise.reject(new Error(messages[0].message || "Terjadi kesalahan"));
						}
					} catch (e) {
						// Failed to parse, try direct access
					}
				}
				if (data.exception) {
					return Promise.reject(new Error("Terjadi kesalahan"));
				}
				return data.message;
			}).catch(function (error) {
				if (error.message === "Sesi tidak valid" || error.message === "Izin tidak cukup") {
					throw error;
				}
				if (error.message === "Failed to fetch") {
					throw new Error("Tidak dapat terhubung ke server");
				}
				throw error;
			});
		},

		post: function (method, data) {
			var url = "/api/method/" + method;
			return fetch(url, {
				method: "POST",
				credentials: "same-origin",
				headers: {
					"Content-Type": "application/json",
					"X-Frappe-CSRF-Token": document.querySelector('meta[name="csrf-token"]').getAttribute("content")
				},
				body: JSON.stringify(data)
			}).then(function (response) {
				if (response.status === 401 || response.status === 403) {
					var currentPath = window.location.pathname;
					if (currentPath !== "/login") {
						window.location.href = "/login?redirect-to=" + encodeURIComponent(currentPath);
					}
					return Promise.reject(new Error("Sesi tidak valid"));
				}
				return response.json();
			}).then(function (data) {
				if (data.exc_type === "PermissionError") {
					window.location.href = "/login?redirect-to=" + encodeURIComponent(window.location.pathname);
					return Promise.reject(new Error("Izin tidak cukup"));
				}
				if (data._server_messages) {
					try {
						var messages = JSON.parse(data._server_messages);
						if (messages && messages.length > 0) {
							return Promise.reject(new Error(messages[0].message || "Terjadi kesalahan"));
						}
					} catch (e) {
						// Failed to parse, try direct access
					}
				}
				if (data.exception) {
					return Promise.reject(new Error("Terjadi kesalahan"));
				}
				return data.message;
			}).catch(function (error) {
				if (error.message === "Sesi tidak valid" || error.message === "Izin tidak cukup") {
					throw error;
				}
				if (error.message === "Failed to fetch") {
					throw new Error("Tidak dapat terhubung ke server");
				}
				throw error;
			});
		}
	};

	window.NX = NX;
})();
