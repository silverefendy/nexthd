frappe.query_reports["SLA Compliance Bulanan"] = {
    onload: function(report) {
        report.set_breadcrumbs = function() {
            frappe.breadcrumbs.add({ type: "Custom", label: "NextHD", route: "/app/nexthd" });
            frappe.breadcrumbs.add({ type: "Custom", label: "SLA Compliance Bulanan", route: window.location.pathname });
        };
        report.set_breadcrumbs();
    }
};
