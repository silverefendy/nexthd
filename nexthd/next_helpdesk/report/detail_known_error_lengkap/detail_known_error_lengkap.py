import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Known Error ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Known Error", "width": 150},
        {"label": "Judul", "fieldname": "title", "fieldtype": "Data", "width": 220},
        {"label": "Problem Terkait", "fieldname": "related_problem", "fieldtype": "Link", "options": "NextHD Problem", "width": 150},
        {"label": "Gejala", "fieldname": "symptom", "fieldtype": "Text", "width": 250},
        {"label": "Workaround", "fieldname": "workaround", "fieldtype": "Text", "width": 250},
        {"label": "Dibuat", "fieldname": "creation", "fieldtype": "Datetime", "width": 150},
    ]
    conditions = []
    values = {}
    if filters.get("related_problem"):
        conditions.append("related_problem = %(related_problem)s")
        values["related_problem"] = filters["related_problem"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = "SELECT name, title, related_problem, symptom, workaround, creation FROM `tabNextHD Known Error` " + where_clause + " ORDER BY creation DESC"
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
