frappe.query_reports["Tiket per Prioritas"] = {
    onload: function(report) {
        report.set_breadcrumbs = function() {
            frappe.breadcrumbs.add({ type: "Custom", label: "NextHD", route: "/app/nexthd" });
            frappe.breadcrumbs.add({ type: "Custom", label: "Tiket per Prioritas", route: window.location.pathname });
        };
        report.set_breadcrumbs();
    }
};
