import frappe

# True = hanya user yang login. Ubah ke False saat siap dipublikasikan.
PRIVATE_MODE = True


def get_context(context):
    if PRIVATE_MODE and frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/nexthd"
        raise frappe.Redirect
    context.no_cache = 1
    context.title = "NextHD"
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
