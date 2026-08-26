import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Asset ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Asset", "width": 130},
        {"label": "Nama Aset", "fieldname": "asset_name", "fieldtype": "Data", "width": 180},
        {"label": "Tipe", "fieldname": "asset_type", "fieldtype": "Data", "width": 110},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Data", "width": 110},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 110},
        {"label": "Serial Number", "fieldname": "serial_number", "fieldtype": "Data", "width": 140},
        {"label": "IP Address", "fieldname": "ip_address", "fieldtype": "Data", "width": 120},
        {"label": "MAC Address", "fieldname": "mac_address", "fieldtype": "Data", "width": 140},
        {"label": "Lokasi", "fieldname": "location", "fieldtype": "Data", "width": 130},
        {"label": "Ditugaskan Ke", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Device Role", "fieldname": "device_role", "fieldtype": "Data", "width": 120},
        {"label": "Tanggal Beli", "fieldname": "purchase_date", "fieldtype": "Date", "width": 110},
        {"label": "Garansi Sampai", "fieldname": "warranty_until", "fieldtype": "Date", "width": 120},
    ]
    conditions = []
    values = {}
    if filters.get("asset_type"):
        conditions.append("asset_type = %(asset_type)s")
        values["asset_type"] = filters["asset_type"]
    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters["status"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = "SELECT name, asset_name, asset_type, status, brand, model, serial_number, ip_address, mac_address, location, assigned_to, device_role, purchase_date, warranty_until FROM `tabNextHD Asset` " + where_clause + " ORDER BY creation DESC"
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
