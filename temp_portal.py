"""
NextHD - Portal API Endpoints

Endpoint untuk portal web NextHD (halaman www/).
Path panggil: nexthd.next_helpdesk.api.portal.<fungsi>
"""

import frappe
from frappe import _
from frappe.utils import now, get_fullname

IT_ROLES = ("Agent", "Agent Manager", "IT Manager", "IT Auditor", "System Manager")


def _user_roles():
	"""Mengembalikan set peran user saat ini."""
	return set(frappe.get_roles())


def require_it_role():
	"""Menolak Guest dan user tanpa peran IT dengan PermissionError."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Anda harus login untuk mengakses halaman ini"), frappe.PermissionError)

	roles = _user_roles()
	if not roles.intersection(IT_ROLES):
		frappe.throw(_("Anda tidak memiliki izin untuk mengakses halaman ini"), frappe.PermissionError)


def resolve_home(roles):
	"""Mengembalikan halaman home berdasarkan peran user.
	-/nexthd/kerja jika ada irisan dengan IT_ROLES, selain itu None.
	"""
	if roles.intersection(IT_ROLES):
		return "/nexthd/kerja"
	return None


def page_guard(context):
	"""Penjaga akses untuk halaman www/.
	1. Guest -> redirect ke login
	2. Login tapi bukan peran IT -> PermissionError
	3. Set no_cache dan csrf_token
	"""
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=" + frappe.request.path
		raise frappe.Redirect

	require_it_role()

	context.no_cache = 1
	context.csrf_token = frappe.sessions.get_csrf_token()


@frappe.whitelist(methods=["GET"])
def get_session_info():
	"""Mengembalikan informasi sesi user untuk portal.
	Mengharuskan user login dan memiliki peran IT.
	"""
	require_it_role()

	roles = _user_roles()
	it_roles_list = sorted(list(roles.intersection(IT_ROLES)))

	return {
		"user": frappe.session.user,
		"full_name": get_fullname(frappe.session.user),
		"roles": it_roles_list,
		"home": "/nexthd/kerja",
		"can_create": frappe.has_permission("NextHD Ticket", "create"),
		"server_now": now()
	}
