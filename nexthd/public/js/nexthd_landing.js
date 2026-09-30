(function () {
	"use strict";
	var items = document.querySelectorAll(".reveal");
	if ("IntersectionObserver" in window) {
		var io = new IntersectionObserver(function (entries) {
			entries.forEach(function (e) {
				if (e.isIntersecting) {
					e.target.classList.add("in");
					io.unobserve(e.target);
				}
			});
		}, { threshold: 0.12 });
		items.forEach(function (el) { io.observe(el); });
	} else {
		items.forEach(function (el) { el.classList.add("in"); });
	}
	var links = document.querySelectorAll("nav a[href^='#']");
	var map = {};
	links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
	if ("IntersectionObserver" in window) {
		var so = new IntersectionObserver(function (entries) {
			entries.forEach(function (e) {
				if (e.isIntersecting && map[e.target.id]) {
					links.forEach(function (a) { a.classList.remove("active"); });
					map[e.target.id].classList.add("active");
				}
			});
		}, { rootMargin: "-40% 0px -55% 0px" });
		Object.keys(map).forEach(function (id) {
			var s = document.getElementById(id);
			if (s) { so.observe(s); }
		});
	}
})();
