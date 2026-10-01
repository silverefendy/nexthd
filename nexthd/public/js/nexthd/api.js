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
						var value = params[key];
						// Only JSON-encode objects/arrays, send primitives as-is
						var encodedValue = (typeof value === 'object' && value !== null)
							? encodeURIComponent(JSON.stringify(value))
							: encodeURIComponent(value);
						return encodeURIComponent(key) + "=" + encodedValue;
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
				if (response.status === 401) {
					var currentPath = window.location.pathname;
					if (currentPath !== "/login") {
						window.location.href = "/login?redirect-to=" + encodeURIComponent(currentPath);
					}
					return Promise.reject(new Error("Sesi tidak valid"));
				}
				if (response.status === 403) {
					// User is logged in but not authorized - show toast, don't redirect to login
					return Promise.reject(new Error("Anda tidak memiliki izin untuk aksi ini"));
				}
				return response.json();
			}).then(function (data) {
				if (data._server_messages) {
					try {
						// _server_messages is double-encoded: JSON string of array of JSON strings
						var messages = JSON.parse(data._server_messages);
						if (messages && messages.length > 0) {
							var msgObj = JSON.parse(messages[0]);
							var errorMsg = msgObj.message || "Terjadi kesalahan";
							// For ValidationError, show business message to user
							if (data.exc_type === "ValidationError") {
								return Promise.reject(new Error(errorMsg));
							}
							return Promise.reject(new Error(errorMsg));
						}
					} catch (e) {
						// Failed to parse, fall through to exception check
					}
				}
				if (data.exception) {
					return Promise.reject(new Error("Terjadi kesalahan"));
				}
				return data.message;
			}).catch(function (error) {
				if (error.message === "Sesi tidak valid" || error.message === "Anda tidak memiliki izin untuk aksi ini") {
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
				if (response.status === 401) {
					var currentPath = window.location.pathname;
					if (currentPath !== "/login") {
						window.location.href = "/login?redirect-to=" + encodeURIComponent(currentPath);
					}
					return Promise.reject(new Error("Sesi tidak valid"));
				}
				if (response.status === 403) {
					// User is logged in but not authorized - show toast, don't redirect to login
					return Promise.reject(new Error("Anda tidak memiliki izin untuk aksi ini"));
				}
				return response.json();
			}).then(function (data) {
				if (data._server_messages) {
					try {
						// _server_messages is double-encoded: JSON string of array of JSON strings
						var messages = JSON.parse(data._server_messages);
						if (messages && messages.length > 0) {
							var msgObj = JSON.parse(messages[0]);
							var errorMsg = msgObj.message || "Terjadi kesalahan";
							// For ValidationError, show business message to user
							if (data.exc_type === "ValidationError") {
								return Promise.reject(new Error(errorMsg));
							}
							return Promise.reject(new Error(errorMsg));
						}
					} catch (e) {
						// Failed to parse, fall through to exception check
					}
				}
				if (data.exception) {
					return Promise.reject(new Error("Terjadi kesalahan"));
				}
				return data.message;
			}).catch(function (error) {
				if (error.message === "Sesi tidak valid" || error.message === "Anda tidak memiliki izin untuk aksi ini") {
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
