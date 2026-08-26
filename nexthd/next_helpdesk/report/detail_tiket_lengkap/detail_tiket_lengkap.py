import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Ticket ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Ticket", "width": 130},
        {"label": "Subjek", "fieldname": "subject", "fieldtype": "Data", "width": 220},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 110},
        {"label": "Prioritas", "fieldname": "priority", "fieldtype": "Data", "width": 90},
        {"label": "Urgency", "fieldname": "urgency", "fieldtype": "Data", "width": 90},
        {"label": "Impact", "fieldname": "impact", "fieldtype": "Data", "width": 90},
        {"label": "Tipe Tiket", "fieldname": "ticket_type", "fieldtype": "Data", "width": 110},
        {"label": "Kategori", "fieldname": "category", "fieldtype": "Link", "options": "NextHD Category", "width": 130},
        {"label": "Tim", "fieldname": "team", "fieldtype": "Link", "options": "NextHD Team", "width": 130},
        {"label": "Dilaporkan Oleh", "fieldname": "requested_by", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Ditugaskan Ke", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Problem Terkait", "fieldname": "related_problem", "fieldtype": "Link", "options": "NextHD Problem", "width": 130},
        {"label": "Aset Terdampak", "fieldname": "affected_asset", "fieldtype": "Link", "options": "NextHD Asset", "width": 130},
        {"label": "Dibuat", "fieldname": "creation", "fieldtype": "Datetime", "width": 150},
        {"label": "SLA Response By", "fieldname": "sla_response_by", "fieldtype": "Datetime", "width": 150},
        {"label": "Direspon Pada", "fieldname": "responded_on", "fieldtype": "Datetime", "width": 150},
        {"label": "SLA Resolution By", "fieldname": "sla_resolution_by", "fieldtype": "Datetime", "width": 150},
        {"label": "Diselesaikan Pada", "fieldname": "resolved_on", "fieldtype": "Datetime", "width": 150},
        {"label": "Ditutup Pada", "fieldname": "closed_on", "fieldtype": "Datetime", "width": 150},
    ]
    conditions = []
    values = {}
    if filters.get("from_date"):
        conditions.append("creation >= %(from_date)s")
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions.append("creation <= %(to_date)s")
        values["to_date"] = filters["to_date"]
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]
    if filters.get("priority"):
        conditions.append("priority = %(priority)s")
        values["priority"] = filters["priority"]
    if filters.get("team"):
        conditions.append("team = %(team)s")
        values["team"] = filters["team"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = "SELECT name, subject, status, priority, urgency, impact, ticket_type, category, team, requested_by, assigned_to, related_problem, affected_asset, creation, sla_response_by, responded_on, sla_resolution_by, resolved_on, closed_on FROM `tabNextHD Ticket` " + where_clause + " ORDER BY creation DESC"
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
