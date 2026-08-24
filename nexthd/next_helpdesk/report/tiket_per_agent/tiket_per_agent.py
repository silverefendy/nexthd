import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    
    # Apply role-based filtering for Agent role
    if frappe.has_role("Agent") and not frappe.has_role("Agent Manager") and not frappe.has_role("IT Manager"):
        filters.agent = frappe.session.user
    
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart_data(columns, data)
    return columns, data, None, chart

def get_columns(filters):
    return [
        {
            "fieldname": "agent",
            "label": _("Agent"),
            "fieldtype": "Link",
            "options": "User",
            "width": 200
        },
        {
            "fieldname": "jumlah_ditugaskan",
            "label": _("Jumlah Ditugaskan"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "jumlah_selesai",
            "label": _("Jumlah Selesai"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "rata_resolusi_jam",
            "label": _("Rata-rata Resolusi (jam)"),
            "fieldtype": "Float",
            "width": 180
        },
        {
            "fieldname": "jumlah_breach_sla",
            "label": _("Jumlah Breach SLA"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "persentase_compliance",
            "label": _("% Compliance"),
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    team = filters.get("team")
    agent = filters.get("agent")
    
    conditions = [
        "`tabNextHD Ticket`.creation >= %(from_date)s",
        "`tabNextHD Ticket`.creation <= %(to_date)s",
        "`tabNextHD Ticket`.assigned_to IS NOT NULL"
    ]
    params = {"from_date": from_date, "to_date": to_date}
    
    if team:
        conditions.append("`tabNextHD Ticket`.team = %(team)s")
        params["team"] = team
    
    if agent:
        conditions.append("`tabNextHD Ticket`.assigned_to = %(agent)s")
        params["agent"] = agent
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT
            `tabNextHD Ticket`.assigned_to AS agent,
            COUNT(`tabNextHD Ticket`.name) AS jumlah_ditugaskan,
            SUM(CASE WHEN `tabNextHD Ticket`.status = 'Selesai' THEN 1 ELSE 0 END) AS jumlah_selesai,
            ROUND(AVG(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                THEN TIMESTAMPDIFF(HOUR, `tabNextHD Ticket`.creation, `tabNextHD Ticket`.resolved_on) 
                ELSE NULL END), 2) AS rata_resolusi_jam,
            SUM(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                AND `tabNextHD Ticket`.sla_resolution_by IS NOT NULL 
                AND `tabNextHD Ticket`.resolved_on > `tabNextHD Ticket`.sla_resolution_by 
                THEN 1 ELSE 0 END) AS jumlah_breach_sla
        FROM
            `tabNextHD Ticket`
        WHERE
            {where_clause}
        GROUP BY
            `tabNextHD Ticket`.assigned_to
        ORDER BY
            jumlah_ditugaskan DESC
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    
    # Calculate compliance percentage
    for row in data:
        total_resolved = row.get("jumlah_selesai", 0)
        breach_count = row.get("jumlah_breach_sla", 0)
        
        if total_resolved > 0:
            compliance = ((total_resolved - breach_count) / total_resolved) * 100
            row["persentase_compliance"] = round(compliance, 2)
        else:
            row["persentase_compliance"] = 0
    
    return data

def get_chart_data(columns, data):
    if not data:
        return None
    
    agents = [row.get("agent") for row in data]
    jumlah_selesai = [row.get("jumlah_selesai", 0) for row in data]
    compliance = [row.get("persentase_compliance", 0) for row in data]
    
    return {
        "data": {
            "labels": agents,
            "datasets": [
                {
                    "name": _("Jumlah Selesai"),
                    "values": jumlah_selesai,
                    "chartType": "bar"
                },
                {
                    "name": _("% Compliance"),
                    "values": compliance,
                    "chartType": "line"
                }
            ]
        },
        "type": "bar",
        "colors": ["#4CAF50", "#2196F3"]
    }
