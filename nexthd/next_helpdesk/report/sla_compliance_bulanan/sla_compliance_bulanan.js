frappe.query_reports["SLA Compliance Bulanan"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "total_tiket" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?creation=${from_date},${to_date}">${value}</a>`;
        }
        
        if (column.fieldname === "breach_response" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?sla_response_breach=1&creation=${from_date},${to_date}">${value}</a>`;
        }
        
        if (column.fieldname === "breach_resolution" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?sla_resolution_breach=1&creation=${from_date},${to_date}">${value}</a>`;
        }
        
        return value;
    }
};
