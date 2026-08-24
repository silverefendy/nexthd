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
            "fieldname": "bulan",
            "label": _("Bulan"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "tiket_baru",
            "label": _("Tiket Baru"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "tiket_selesai",
            "label": _("Tiket Selesai"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "tiket_ditutup",
            "label": _("Tiket Ditutup"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "sla_breach",
            "label": _("SLA Breach"),
            "fieldtype": "Int",
            "width": 120
        }
    ]

def get_data(filters):
    year = filters.get("year")
    agent = filters.get("agent")
    priority = filters.get("priority")
    team = filters.get("team")
    
    conditions = ["YEAR(`tabNextHD Ticket`.creation) = %(year)s"]
    params = {"year": year}
    
    if agent:
        conditions.append("`tabNextHD Ticket`.assigned_to = %(agent)s")
        params["agent"] = agent
    
    if priority:
        conditions.append("`tabNextHD Ticket`.priority = %(priority)s")
        params["priority"] = priority
    
    if team:
        conditions.append("`tabNextHD Ticket`.team = %(team)s")
        params["team"] = team
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT
            DATE_FORMAT(`tabNextHD Ticket`.creation, '%%Y-%%m') AS bulan,
            COUNT(`tabNextHD Ticket`.name) AS tiket_baru,
            SUM(CASE WHEN `tabNextHD Ticket`.status = 'Selesai' AND YEAR(`tabNextHD Ticket`.resolved_on) = %(year)s THEN 1 ELSE 0 END) AS tiket_selesai,
            SUM(CASE WHEN `tabNextHD Ticket`.status = 'Ditutup' AND YEAR(`tabNextHD Ticket`.closed_on) = %(year)s THEN 1 ELSE 0 END) AS tiket_ditutup,
            SUM(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                AND `tabNextHD Ticket`.sla_resolution_by IS NOT NULL 
                AND `tabNextHD Ticket`.resolved_on > `tabNextHD Ticket`.sla_resolution_by 
                THEN 1 ELSE 0 END) AS sla_breach
        FROM
            `tabNextHD Ticket`
        WHERE
            {where_clause}
        GROUP BY
            DATE_FORMAT(`tabNextHD Ticket`.creation, '%%Y-%%m')
        ORDER BY
            DATE_FORMAT(`tabNextHD Ticket`.creation, '%%Y-%%m')
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    return data

def get_chart_data(columns, data):
    if not data:
        return None
    
    months = [row.get("bulan") for row in data]
    tiket_baru = [row.get("tiket_baru", 0) for row in data]
    tiket_selesai = [row.get("tiket_selesai", 0) for row in data]
    
    return {
        "data": {
            "labels": months,
            "datasets": [
                {
                    "name": _("Tiket Baru"),
                    "values": tiket_baru,
                    "chartType": "bar"
                },
                {
                    "name": _("Tiket Selesai"),
                    "values": tiket_selesai,
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "colors": ["#4CAF50", "#2196F3"]
    }
