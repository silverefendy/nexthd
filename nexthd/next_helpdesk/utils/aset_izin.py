import frappe

# Peran staf: tidak dibatasi aturan ini.
PERAN_STAF = {"Agent", "Agent Manager", "IT Manager", "IT Auditor", "System Manager"}


def _requester_murni(user):
    """True jika pengguna punya peran Requester dan tidak punya peran staf."""
    if not user or user == "Administrator":
        return False
    peran = set(frappe.get_roles(user))
    if peran & PERAN_STAF:
        return False
    return "Requester" in peran


def get_permission_query_conditions(user=None):
    """Filter daftar NextHD Asset: requester murni hanya melihat aset miliknya."""
    user = user or frappe.session.user
    if not _requester_murni(user):
        return ""
    user_escaped = frappe.db.escape(user)
    # requester murni melihat aset jika assigned_to = dirinya ATAU dirinya ada di tabel asset_users
    return """(
        `tabNextHD Asset`.`assigned_to` = {0}
        OR EXISTS (
            SELECT 1 FROM `tabNextHD Asset User`
            WHERE parent = `tabNextHD Asset`.`name`
            AND user = {0}
        )
    )""".format(user_escaped)


def has_permission(doc, ptype=None, user=None, **kwargs):
    """Cek satu dokumen NextHD Asset: requester murni hanya boleh aset miliknya."""
    user = user or frappe.session.user
    if not _requester_murni(user):
        return True
    # requester murni boleh jika assigned_to = dirinya ATAU dirinya ada di tabel asset_users
    if doc.get("assigned_to") == user:
        return True
    # cek tabel asset_users
    asset_users = frappe.get_all("NextHD Asset User",
        filters={"parent": doc.get("name"), "user": user},
        fields=["name"])
    return len(asset_users) > 0
