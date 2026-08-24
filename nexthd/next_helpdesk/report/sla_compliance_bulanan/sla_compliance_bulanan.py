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
            "fieldname": "total_tiket",
            "label": _("Total Tiket"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "breach_response",
            "label": _("Breach Response"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "breach_resolution",
            "label": _("Breach Resolution"),
            "fieldtype": "Int",
            "width": 130
        },
        {
            "fieldname": "persentase_compliance",
            "label": _("% Compliance"),
            "fieldtype": "Float",
            "width": 120
        }
    ]

def get_data(filters):
    year = filters.get("year")
    
    query = """
        SELECT
            DATE_FORMAT(creation, '%%Y-%%m') AS bulan,
            COUNT(name) AS total_tiket,
            SUM(CASE WHEN responded_on IS NOT NULL 
                AND sla_response_by IS NOT NULL 
                AND responded_on > sla_response_by 
                THEN 1 ELSE 0 END) AS breach_response,
            SUM(CASE WHEN resolved_on IS NOT NULL 
                AND sla_resolution_by IS NOT NULL 
                AND resolved_on > sla_resolution_by 
                THEN 1 ELSE 0 END) AS breach_resolution
        FROM
            `tabNextHD Ticket`
        WHERE
            YEAR(creation) = %s
        GROUP BY
            DATE_FORMAT(creation, '%%Y-%%m')
        ORDER BY
            DATE_FORMAT(creation, '%%Y-%%m')
    """
    
    data = frappe.db.sql(query, year, as_dict=True)
    
    # Calculate compliance percentage
    for row in data:
        total = row.get("total_tiket", 0)
        breach_response = row.get("breach_response", 0)
        breach_resolution = row.get("breach_resolution", 0)
        
        if total > 0:
            # Compliance = 100 - ((breach_response + breach_resolution) / total * 100)
            total_breach = breach_response + breach_resolution
            compliance = 100 - ((total_breach / total) * 100)
            row["persentase_compliance"] = round(compliance, 2)
        else:
            row["persentase_compliance"] = 0
    
    return data

def get_chart_data(columns, data):
    if not data:
        return None
    
    months = [row.get("bulan") for row in data]
    compliance = [row.get("persentase_compliance", 0) for row in data]
    
    return {
        "data": {
            "labels": months,
            "datasets": [
                {
                    "name": _("% Compliance"),
                    "values": compliance,
                    "chartType": "line"
                }
            ]
        },
        "type": "line",
        "colors": ["#4CAF50"]
    }
