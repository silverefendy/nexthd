import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Problem ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Problem", "width": 130},
        {"label": "Judul", "fieldname": "title", "fieldtype": "Data", "width": 200},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Prioritas", "fieldname": "priority", "fieldtype": "Data", "width": 90},
        {"label": "Kategori", "fieldname": "category", "fieldtype": "Link", "options": "NextHD Category", "width": 130},
        {"label": "Aset Terkait", "fieldname": "related_asset", "fieldtype": "Link", "options": "NextHD Asset", "width": 130},
        {"label": "Known Error", "fieldname": "known_error", "fieldtype": "Link", "options": "NextHD Known Error", "width": 140},
        {"label": "Change Request", "fieldname": "change_request", "fieldtype": "Link", "options": "NextHD Change Request", "width": 150},
        {"label": "Root Cause", "fieldname": "root_cause", "fieldtype": "Text", "width": 220},
        {"label": "Workaround", "fieldname": "workaround", "fieldtype": "Text", "width": 220},
        {"label": "Dibuat", "fieldname": "creation", "fieldtype": "Datetime", "width": 150},
    ]
    conditions = []
    values = {}
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]
    if filters.get("priority"):
        conditions.append("priority = %(priority)s")
        values["priority"] = filters["priority"]
    if filters.get("category"):
        conditions.append("category = %(category)s")
        values["category"] = filters["category"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = "SELECT name, title, status, priority, category, related_asset, known_error, change_request, root_cause, workaround, creation FROM `tabNextHD Problem` " + where_clause + " ORDER BY creation DESC"
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
