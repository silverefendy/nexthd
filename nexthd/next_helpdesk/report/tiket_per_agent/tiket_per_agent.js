frappe.query_reports["Tiket per Agent"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "jumlah_ditugaskan" && value > 0) {
            const agent = data.agent;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            const team = frappe.query_report_filters.find(f => f.fieldname === "team")?.value;
            
            let url = `/app/nexthd-ticket?assigned_to=${agent}&creation=${from_date},${to_date}`;
            if (team) url += `&team=${team}`;
            
            value = `<a href="${url}">${value}</a>`;
        }
        
        if (column.fieldname === "jumlah_selesai" && value > 0) {
            const agent = data.agent;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            const team = frappe.query_report_filters.find(f => f.fieldname === "team")?.value;
            
            let url = `/app/nexthd-ticket?assigned_to=${agent}&status=Selesai&resolved_on=${from_date},${to_date}`;
            if (team) url += `&team=${team}`;
            
            value = `<a href="${url}">${value}</a>`;
        }
        
        if (column.fieldname === "jumlah_breach_sla" && value > 0) {
            const agent = data.agent;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            const team = frappe.query_report_filters.find(f => f.fieldname === "team")?.value;
            
            let url = `/app/nexthd-ticket?assigned_to=${agent}&sla_breach=1&creation=${from_date},${to_date}`;
            if (team) url += `&team=${team}`;
            
            value = `<a href="${url}">${value}</a>`;
        }
        
        return value;
    }
};
