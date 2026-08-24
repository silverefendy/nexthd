frappe.query_reports["Tiket per Kategori"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "jumlah_tiket" && value > 0) {
            const category = data.kategori;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            
            if (category) {
                value = `<a href="/app/nexthd-ticket?category=${category}&creation=${from_date},${to_date}">${value}</a>`;
            }
        }
        
        if (column.fieldname === "jumlah_selesai" && value > 0) {
            const category = data.kategori;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            
            if (category) {
                value = `<a href="/app/nexthd-ticket?category=${category}&status=Selesai&resolved_on=${from_date},${to_date}">${value}</a>`;
            }
        }
        
        if (column.fieldname === "jumlah_masih_terbuka" && value > 0) {
            const category = data.kategori;
            const from_date = frappe.query_report_filters.find(f => f.fieldname === "from_date")?.value;
            const to_date = frappe.query_report_filters.find(f => f.fieldname === "to_date")?.value;
            
            if (category) {
                value = `<a href="/app/nexthd-ticket?category=${category}&status=Baru,Sedang Dikerjakan,Menunggu User&creation=${from_date},${to_date}">${value}</a>`;
            }
        }
        
        return value;
    }
};
