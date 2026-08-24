frappe.query_reports["Tiket per Bulan"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "tiket_baru" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?creation=${from_date},${to_date}">${value}</a>`;
        }
        
        if (column.fieldname === "tiket_selesai" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?status=Selesai&resolved_on=${from_date},${to_date}">${value}</a>`;
        }
        
        if (column.fieldname === "sla_breach" && value > 0) {
            const month = data.bulan;
            const year = month.split("-")[0];
            const month_num = month.split("-")[1];
            const from_date = `${year}-${month_num}-01`;
            const to_date = `${year}-${month_num}-31`;
            
            value = `<a href="/app/nexthd-ticket?sla_breach=1&creation=${from_date},${to_date}">${value}</a>`;
        }
        
        return value;
    }
};
