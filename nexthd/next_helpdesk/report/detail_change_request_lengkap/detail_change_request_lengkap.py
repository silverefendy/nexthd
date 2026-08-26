import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "CR ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Change Request", "width": 130},
        {"label": "Judul", "fieldname": "title", "fieldtype": "Data", "width": 200},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Tipe Perubahan", "fieldname": "change_type", "fieldtype": "Data", "width": 130},
        {"label": "Level Risiko", "fieldname": "risk_level", "fieldtype": "Data", "width": 100},
        {"label": "Aset Terkait", "fieldname": "related_asset", "fieldtype": "Link", "options": "NextHD Asset", "width": 130},
        {"label": "Problem Terkait", "fieldname": "related_problem", "fieldtype": "Link", "options": "NextHD Problem", "width": 140},
        {"label": "Rencana Implementasi", "fieldname": "implementation_plan", "fieldtype": "Text", "width": 220},
        {"label": "Rencana Rollback", "fieldname": "rollback_plan", "fieldtype": "Text", "width": 220},
        {"label": "Dibuat", "fieldname": "creation", "fieldtype": "Datetime", "width": 150},
    ]
    conditions = []
    values = {}
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]
    if filters.get("risk_level"):
        conditions.append("risk_level = %(risk_level)s")
        values["risk_level"] = filters["risk_level"]
    if filters.get("change_type"):
        conditions.append("change_type = %(change_type)s")
        values["change_type"] = filters["change_type"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = "SELECT name, title, status, change_type, risk_level, related_asset, related_problem, implementation_plan, rollback_plan, creation FROM `tabNextHD Change Request` " + where_clause + " ORDER BY creation DESC"
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
