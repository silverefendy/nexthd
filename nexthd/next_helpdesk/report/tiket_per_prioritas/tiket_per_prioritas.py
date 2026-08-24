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
            "fieldname": "prioritas",
            "label": _("Prioritas"),
            "fieldtype": "Select",
            "width": 150
        },
        {
            "fieldname": "jumlah_tiket",
            "label": _("Jumlah Tiket"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "rata_waktu_resolusi_jam",
            "label": _("Rata-rata waktu resolusi (jam)"),
            "fieldtype": "Float",
            "width": 200
        },
        {
            "fieldname": "jumlah_breach_sla",
            "label": _("Jumlah breach SLA"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "persentase_compliance",
            "label": _("% Compliance SLA"),
            "fieldtype": "Float",
            "width": 150
        }
    ]

def get_data(filters):
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    category = filters.get("category")
    team = filters.get("team")
    
    conditions = [
        "`tabNextHD Ticket`.creation >= %(from_date)s",
        "`tabNextHD Ticket`.creation <= %(to_date)s"
    ]
    params = {"from_date": from_date, "to_date": to_date}
    
    if category:
        conditions.append("`tabNextHD Ticket`.category = %(category)s")
        params["category"] = category
    
    if team:
        conditions.append("`tabNextHD Ticket`.team = %(team)s")
        params["team"] = team
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT
            `tabNextHD Ticket`.priority AS prioritas,
            COUNT(`tabNextHD Ticket`.name) AS jumlah_tiket,
            ROUND(AVG(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                THEN TIMESTAMPDIFF(HOUR, `tabNextHD Ticket`.creation, `tabNextHD Ticket`.resolved_on) 
                ELSE NULL END), 2) AS rata_waktu_resolusi_jam,
            SUM(CASE WHEN `tabNextHD Ticket`.resolved_on IS NOT NULL 
                AND `tabNextHD Ticket`.sla_resolution_by IS NOT NULL 
                AND `tabNextHD Ticket`.resolved_on > `tabNextHD Ticket`.sla_resolution_by 
                THEN 1 ELSE 0 END) AS jumlah_breach_sla
        FROM
            `tabNextHD Ticket`
        WHERE
            {where_clause}
        GROUP BY
            `tabNextHD Ticket`.priority
        ORDER BY
            FIELD(`tabNextHD Ticket`.priority, 'Kritis', 'Tinggi', 'Sedang', 'Rendah')
    """
    
    data = frappe.db.sql(query, params, as_dict=True)
    
    # Calculate compliance percentage
    for row in data:
        total_resolved = row.get("jumlah_tiket", 0)
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
    
    priorities = [row.get("prioritas") for row in data]
    compliance = [row.get("persentase_compliance", 0) for row in data]
    
    return {
        "data": {
            "labels": priorities,
            "datasets": [
                {
                    "name": _("% Compliance SLA"),
                    "values": compliance,
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "colors": ["#9C27B0"]
    }
