frappe.listview_settings['NextHD Ticket'] = {
    get_indicator: function(doc) {
        var status_colors = {
            "Baru": "red",
            "Sedang Dikerjakan": "blue",
            "Menunggu User": "yellow",
            "Selesai": "green",
            "Ditutup": "gray"
        };
        var color = status_colors[doc.status] || "gray";
        return [__(doc.status), color, "status,=," + doc.status];
    },
    formatters: {
        priority: function (value) {
            let color_map = {
                "Kritis": "red",
                "Tinggi": "orange",
                "Sedang": "yellow",
                "Rendah": "grey"
            };
            let color = color_map[value] || "grey";
            return `<span class="indicator-pill ${color} filterable" data-filter="priority,=,${value}">${__(value)}</span>`;
        },
        ticket_type: function (value) {
            let color_map = {
                "Insiden": "red",
                "Permintaan Layanan": "blue"
            };
            let color = color_map[value] || "grey";
            return `<span class="indicator-pill ${color} filterable" data-filter="ticket_type,=,${value}">${__(value)}</span>`;
        }
    }
};
