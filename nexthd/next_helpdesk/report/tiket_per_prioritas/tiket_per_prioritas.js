frappe.query_reports["Tiket per Prioritas"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "jumlah_tiket" && value > 0) {
            const priority = data.prioritas;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            const category = frappe.query_report_filters.find(f => f.fieldname === "category")?.value;
            const team = frappe.query_report_filters.find(f => f.fieldname === "team")?.value;
            
            let url = `/app/nexthd-ticket?priority=${priority}&creation=${from_date},${to_date}`;
            if (category) url += `&category=${category}`;
            if (team) url += `&team=${team}`;
            
            value = `<a href="${url}">${value}</a>`;
        }
        
        if (column.fieldname === "jumlah_breach_sla" && value > 0) {
            const priority = data.prioritas;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            const category = frappe.query_report_filters.find(f => f.fieldname === "category")?.value;
            const team = frappe.query_report_filters.find(f => f.fieldname === "team")?.value;
            
            let url = `/app/nexthd-ticket?priority=${priority}&sla_breach=1&creation=${from_date},${to_date}`;
            if (category) url += `&category=${category}`;
            if (team) url += `&team=${team}`;
            
            value = `<a href="${url}">${value}</a>`;
        }
        
        return value;
    }
};
