function get_color_from_string_asset(str) {
    let colors = ["blue", "green", "red", "orange", "purple", "darkgrey", "yellow", "light-blue", "cyan", "pink"];
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    let index = Math.abs(hash) % colors.length;
    return colors[index];
}

frappe.listview_settings['NextHD Asset'] = {
    formatters: {
        status: function (value) {
            let color_map = {
                "Aktif": "green",
                "Rusak": "red",
                "Diperbaiki": "orange",
                "Dihapus": "grey"
            };
            let color = color_map[value] || "grey";
            return `<span class="indicator-pill ${color} filterable" data-filter="status,=,${value}">${__(value)}</span>`;
        },
        asset_category: function (value) {
            if (!value) return '';
            let color = get_color_from_string_asset(value);
            return `<span class="indicator-pill ${color} filterable" data-filter="asset_category,=,${value}">${__(value)}</span>`;
        }
    }
};
