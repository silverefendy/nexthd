import frappe
from urllib.parse import quote
from nexthd.next_helpdesk.api.portal import IT_ROLES

def get_context(context):
    # Guest redirect ke login
    if frappe.session.user == "Guest":
        redirect_to = quote("/nexthd")
        frappe.local.flags.redirect_location = "/login?redirect-to=" + redirect_to
        raise frappe.Redirect

    # Cek peran IT
    roles = set(frappe.get_roles())
    if not roles.intersection(IT_ROLES):
        # Redirect ke halaman tentang untuk non-IT
        frappe.local.flags.redirect_location = "/nexthd/tentang"
        raise frappe.Redirect

    # Peran IT: tampilkan dashboard
    context.no_cache = 1
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.title = "Beranda"
