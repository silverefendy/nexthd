function get_color_from_string(str) {
    let colors = ["blue", "green", "red", "orange", "purple", "darkgrey", "yellow", "light-blue", "cyan", "pink"];
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    let index = Math.abs(hash) % colors.length;
    return colors[index];
}

frappe.listview_settings['NextHD Photo'] = {
    formatters: {
        category: function (value) {
            if (!value) return '';
            let color = get_color_from_string(value);
            return `<span class="indicator-pill ${color} filterable" data-filter="category,=,${value}">${__(value)}</span>`;
        }
    }
};
