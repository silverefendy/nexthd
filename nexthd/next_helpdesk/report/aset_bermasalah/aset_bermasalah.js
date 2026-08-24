frappe.query_reports["Aset Bermasalah"] = {
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Make numeric columns clickable for drill-down
        if (column.fieldname === "jumlah_tiket_terkait" && value > 0) {
            const asset = data.aset;
            
            value = `<a href="/app/nexthd-ticket?affected_asset=${asset}">${value}</a>`;
        }
        
        if (column.fieldname === "jumlah_problem_terkait" && value > 0) {
            const asset = data.aset;
            
            value = `<a href="/app/nexthd-ticket?affected_asset=${asset}&related_problem_is_set=1">${value}</a>`;
        }
        
        if (column.fieldname === "tanggal_tiket_terakhir" && value) {
            const asset = data.aset;
            
            value = `<a href="/app/nexthd-ticket?affected_asset=${asset}">${value}</a>`;
        }
        
        return value;
    }
};
