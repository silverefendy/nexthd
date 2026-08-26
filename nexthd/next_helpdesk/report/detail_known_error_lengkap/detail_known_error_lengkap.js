frappe.query_reports["Detail Known Error Lengkap"] = {
    onload: function(report) {
        report.set_breadcrumbs = function() {
            frappe.breadcrumbs.add({ type: "Custom", label: "NextHD", route: "/app/nexthd" });
            frappe.breadcrumbs.add({ type: "Custom", label: "Detail Known Error Lengkap", route: window.location.pathname });
        };
        report.set_breadcrumbs();
    }
};
