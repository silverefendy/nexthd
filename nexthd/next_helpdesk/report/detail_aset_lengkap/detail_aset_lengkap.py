import frappe

def execute(filters=None):
    filters = filters or {}
    columns = [
        {"label": "Asset ID", "fieldname": "name", "fieldtype": "Link", "options": "NextHD Asset", "width": 130},
        {"label": "Nama Aset", "fieldname": "asset_name", "fieldtype": "Data", "width": 160},
        {"label": "Tipe", "fieldname": "asset_type", "fieldtype": "Data", "width": 100},
        {"label": "Kategori", "fieldname": "asset_category", "fieldtype": "Link", "options": "NextHD Asset Category", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": "Lokasi", "fieldname": "location", "fieldtype": "Data", "width": 120},
        {"label": "Ditugaskan Ke", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 140},
        {"label": "Spesifikasi (EAV)", "fieldname": "spesifikasi", "fieldtype": "Small Text", "width": 300},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Data", "width": 110},
        {"label": "Serial Number", "fieldname": "serial_number", "fieldtype": "Data", "width": 140},
        {"label": "Sumber", "fieldname": "sumber", "fieldtype": "Data", "width": 110},
        {"label": "Catatan", "fieldname": "catatan", "fieldtype": "Small Text", "width": 200},
        {"label": "Tanggal Beli", "fieldname": "purchase_date", "fieldtype": "Date", "width": 110},
        {"label": "Garansi Sampai", "fieldname": "warranty_until", "fieldtype": "Date", "width": 120},
    ]
    conditions = []
    values = {}
    if filters.get("asset_type"):
        conditions.append("a.asset_type = %(asset_type)s")
        values["asset_type"] = filters["asset_type"]
    if filters.get("status"):
        conditions.append("a.status = %(status)s")
        values["status"] = filters["status"]
    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    query = """
        SELECT
            a.name, a.asset_name, a.asset_type, a.asset_category, a.status,
            a.location, a.assigned_to, a.purchase_date, a.warranty_until,
            GROUP_CONCAT(DISTINCT CONCAT(att.attribute_name, ': ', att.attribute_value)
                ORDER BY att.idx SEPARATOR '; ') AS spesifikasi,
            GROUP_CONCAT(DISTINCT att.brand SEPARATOR ', ') AS brand,
            GROUP_CONCAT(DISTINCT att.serial_number SEPARATOR ', ') AS serial_number,
            GROUP_CONCAT(DISTINCT att.sumber SEPARATOR ', ') AS sumber,
            GROUP_CONCAT(DISTINCT att.catatan SEPARATOR '; ') AS catatan
        FROM `tabNextHD Asset` a
        LEFT JOIN `tabNextHD Asset Attribute` att ON att.parent = a.name
        """ + where_clause + """
        GROUP BY a.name
        ORDER BY a.creation DESC
    """
    data = frappe.db.sql(query, values, as_dict=True)
    return columns, data
