import frappe
from nexthd.next_helpdesk.api.portal import resolve_home, IT_ROLES

# True = hanya user yang login. Ubah ke False saat siap dipublikasikan.
PRIVATE_MODE = True


def get_context(context):
    # Deteksi peran IT
    roles = set(frappe.get_roles())
    is_it = bool(roles.intersection(IT_ROLES))
    context.is_it = is_it

    # Jika IT, berikan csrf_token untuk API calls
    if is_it:
        context.csrf_token = frappe.sessions.get_csrf_token()

    # Jika PRIVATE_MODE dan Guest, redirect ke login
    if PRIVATE_MODE and frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/nexthd/tentang"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "NextHD"
    context.home_url = resolve_home(roles)
    stats = {}
    for key, dt in (
        ("tiket", "NextHD Ticket"),
        ("problem", "NextHD Problem"),
        ("known_error", "NextHD Known Error"),
        ("aset", "NextHD Asset"),
    ):
        try:
            stats[key] = frappe.db.count(dt)
        except Exception:
            stats[key] = 0
    context.stats = stats
