frappe.query_reports["Detail Change Request Lengkap"] = {
    onload: function(report) {
        report.set_breadcrumbs = function() {
            frappe.breadcrumbs.add({ type: "Custom", label: "NextHD", route: "/app/nexthd" });
            frappe.breadcrumbs.add({ type: "Custom", label: "Detail Change Request Lengkap", route: window.location.pathname });
        };
        report.set_breadcrumbs();
    }
};
