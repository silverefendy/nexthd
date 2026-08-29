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
            "fieldname": "aset",
            "label": _("Aset"),
            "fieldtype": "Link",
            "options": "NextHD Asset",
            "width": 200
        },
        {
            "fieldname": "lokasi",
            "label": _("Lokasi"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "jumlah_tiket_terkait",
            "label": _("Jumlah Tiket Terkait"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "jumlah_problem_terkait",
            "label": _("Jumlah Problem Terkait"),
            "fieldtype": "Int",
            "width": 150
        },
        {
            "fieldname": "tanggal_tiket_terakhir",
            "label": _("Tanggal Tiket Terakhir"),
            "fieldtype": "Date",
            "width": 150
        }
    ]

def get_data(filters):
    asset_category = filters.get("asset_category")

    conditions = []
    params = {}

    if asset_category:
        conditions.append("asset.asset_category = %(asset_category)s")
        params["asset_category"] = asset_category

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    query = f"""
        SELECT
            asset.name AS aset,
            asset.asset_name AS lokasi,
            COALESCE(ticket_count.ticket_count, 0) AS jumlah_tiket_terkait,
            COALESCE(problem_count.problem_count, 0) AS jumlah_problem_terkait,
            COALESCE(last_ticket.last_ticket_date, NULL) AS tanggal_tiket_terakhir
        FROM
            `tabNextHD Asset` asset
        LEFT JOIN (
            SELECT
                affected_asset,
                COUNT(name) AS ticket_count
            FROM
                `tabNextHD Ticket`
            WHERE
                affected_asset IS NOT NULL
            GROUP BY
                affected_asset
        ) ticket_count ON asset.name = ticket_count.affected_asset
        LEFT JOIN (
            SELECT
                t1.affected_asset,
                COUNT(DISTINCT t1.related_problem) AS problem_count
            FROM
                `tabNextHD Ticket` t1
            WHERE
                t1.affected_asset IS NOT NULL
                AND t1.related_problem IS NOT NULL
            GROUP BY
                t1.affected_asset
        ) problem_count ON asset.name = problem_count.affected_asset
        LEFT JOIN (
            SELECT
                affected_asset,
                MAX(creation) AS last_ticket_date
            FROM
                `tabNextHD Ticket`
            WHERE
                affected_asset IS NOT NULL
            GROUP BY
                affected_asset
        ) last_ticket ON asset.name = last_ticket.affected_asset
        WHERE
            {where_clause}
            AND (ticket_count.ticket_count > 0 OR problem_count.problem_count > 0)
        ORDER BY
            ticket_count.ticket_count DESC,
            problem_count.problem_count DESC
    """

    data = frappe.db.sql(query, params, as_dict=True)
    return data

def get_chart_data(columns, data):
    if not data:
        return None

    assets = [row.get("aset") for row in data]
    jumlah_tiket = [row.get("jumlah_tiket_terkait", 0) for row in data]
    jumlah_problem = [row.get("jumlah_problem_terkait", 0) for row in data]

    return {
        "data": {
            "labels": assets,
            "datasets": [
                {
                    "name": _("Jumlah Tiket Terkait"),
                    "values": jumlah_tiket,
                    "chartType": "bar"
                },
                {
                    "name": _("Jumlah Problem Terkait"),
                    "values": jumlah_problem,
                    "chartType": "bar"
                }
            ]
        },
        "type": "bar",
        "colors": ["#F44336", "#FF9800"]
    }
