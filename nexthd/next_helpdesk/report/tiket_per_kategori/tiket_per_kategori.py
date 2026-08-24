import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(columns, data)
    return columns, data, None, chart

def get_columns(filters):
    return [
        {
            "fieldname": "kategori",
            "label": _("Kategori"),
            "fieldtype": "Link",
            "options": "NextHD Category",
            "width": 200
        },
        {
            "fieldname": "jumlah_tiket",
            "label": _("Jumlah Tiket"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "jumlah_selesai",
            "label": _("Jumlah Selesai"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "jumlah_masih_terbuka",
            "label": _("Jumlah Masih Terbuka"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "rata_resolusi_jam",
            "label": _("Rata-rata Resolusi (jam)"),
            "fieldtype": "Float",
            "width": 180
        }
    ]

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    ticket_type = filters.get("ticket_type")
    team = filters.get("team")
    
    conditions = [
        "`tabNextHD Ticket`.creation >= %(from_date)s",
        "`tabNextHD Ticket`.creation <= %(to_date)s"
    ]
    params = {"from_date": from_date, "to_date": to_date}
    
    if ticket_type:
        conditions.append("`tabNextHD Ticket`.ticket_type = %(ticket_type)s")
        params["ticket_type"] = ticket_type
    
    if team:
        conditions.append("`tabNextHD Ticket`.team = %(team)s")
        params["team"] = team
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT
            `tabNextHD Ticket`.category AS kategori,
            COUNT(`tabNextHD Ticket`.name) AS jumlah_tiket,
            SUM(CASE WHEN `tabNextHD Ticket`.status = 'Selesai' THEN 1 ELSE 0 END) AS jumlah_selesai,
            SUM(CASE WHEN `tabNextHD Ticket`.status IN ('Baru', 'Sedang Dikerjakan', 'Menunggu User') THEN 1 ELSE 0 END) AS jumlah_masih_terbuka,
            ROUND(AVG(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                THEN TIMESTAMPDIFF(HOUR, `tabNextHD Ticket`.creation, `tabNextHD Ticket`.resolved_on) 
                ELSE NULL END), 2) AS rata_resolusi_jam
        FROM
            `tabNextHD Ticket`
        WHERE
            {where_clause}
        GROUP BY
            `tabNextHD Ticket`.category
        ORDER BY
            `tabNextHD Ticket`.category
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data

def get_chart_data(columns, data):
    if not data:
        return None
    
    categories = [row.get("kategori") or _("Uncategorized") for row in data]
    jumlah_tiket = [row.get("jumlah_tiket", 0) for row in data]
    
    return {
        "data": {
            "labels": categories,
            "datasets": [
                {
                    "name": _("Jumlah Tiket"),
                    "values": jumlah_tiket,
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "colors": ["#FF9800"]
    }
