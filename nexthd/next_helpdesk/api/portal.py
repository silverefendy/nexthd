"""
NextHD - Portal API Endpoints

Endpoint untuk portal web NextHD (halaman www/).
Path panggil: nexthd.next_helpdesk.api.portal.<fungsi>
"""

import frappe
from frappe import _
from frappe.utils import now, get_fullname
from frappe.utils.html_utils import sanitize_html

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


@frappe.whitelist(methods=["GET"])
def get_ticket_options():
	"""Mengembalikan opsi dinamis untuk form tiket dan filter antrian."""
	require_it_role()

	meta = frappe.get_meta("NextHD Ticket")

	# Ambil opsi dari field Select
	def get_field_options(fieldname):
		field = meta.get_field(fieldname)
		if field and field.fieldtype == "Select" and field.options:
			return [opt for opt in field.options.split("\n") if opt.strip()]
		return []

	status_options = get_field_options("status")
	priority_options = get_field_options("priority")
	ticket_type_options = get_field_options("ticket_type")
	impact_options = get_field_options("impact")
	urgency_options = get_field_options("urgency")

	# Kategori dari DocType NextHD Category
	categories = frappe.get_list("NextHD Category", pluck="name")

	# Field wajib dari meta yang termasuk form buat tiket
	form_fields = ["ticket_type", "subject", "description", "category", "impact", "urgency", "requested_by"]
	required = []
	for fieldname in form_fields:
		field = meta.get_field(fieldname)
		if field and field.reqd:
			required.append(fieldname)

	return {
		"status": status_options,
		"priority": priority_options,
		"ticket_type": ticket_type_options,
		"impact": impact_options,
		"urgency": urgency_options,
		"categories": categories,
		"required": required
	}


@frappe.whitelist(methods=["GET"])
def list_tickets(view="all", status=None, priority=None, ticket_type=None, category=None,
                  search=None, order_by="modified desc", page=1, page_size=20):
	"""Mengembalikan daftar tiket dengan filter dan pagination."""
	require_it_role()

	# Whitelist view
	VIEW_WHITELIST = ["all", "mine", "unassigned", "overdue"]
	if view not in VIEW_WHITELIST:
		frappe.throw(_("View tidak valid"), frappe.ValidationError)

	# Whitelist order_by
	ORDER_BY_WHITELIST = ["modified desc", "creation desc", "sla_resolution_by asc"]
	if order_by not in ORDER_BY_WHITELIST:
		frappe.throw(_("Order by tidak valid"), frappe.ValidationError)

	# Validasi page dan page_size
	try:
		page = int(page)
		page_size = int(page_size)
	except (ValueError, TypeError):
		frappe.throw(_("Page dan page_size harus angka"), frappe.ValidationError)

	if page < 1:
		frappe.throw(_("Page harus >= 1"), frappe.ValidationError)
	if page_size < 1 or page_size > 50:
		page_size = 50

	# Build filters
	filters = {}

	# View filter
	if view == "mine":
		filters["assigned_to"] = frappe.session.user
	elif view == "unassigned":
		filters["assigned_to"] = ["is", "not set"]
	elif view == "overdue":
		filters["sla_resolution_by"] = ["<", now()]
		filters["status"] = ["not in", ["Selesai", "Ditutup"]]

	# Additional filters (hanya jika nilai non-kosong dan ada di opsi meta)
	# Note: status parameter tidak boleh menggantikan filter status dari view
	if status and view != "overdue":
		meta = frappe.get_meta("NextHD Ticket")
		status_field = meta.get_field("status")
		if status_field and status in (status_field.options or "").split("\n"):
			filters["status"] = status

	if priority:
		meta = frappe.get_meta("NextHD Ticket")
		priority_field = meta.get_field("priority")
		if priority_field and priority in (priority_field.options or "").split("\n"):
			filters["priority"] = priority

	if ticket_type:
		meta = frappe.get_meta("NextHD Ticket")
		type_field = meta.get_field("ticket_type")
		if type_field and ticket_type in (type_field.options or "").split("\n"):
			filters["ticket_type"] = ticket_type

	if category:
		categories = frappe.get_list("NextHD Category", pluck="name")
		if category in categories:
			filters["category"] = category

	# Search filter
	or_filters = None
	if search:
		if len(search) > 100:
			search = search[:100]
		or_filters = [
			["name", "like", "%" + search + "%"],
			["subject", "like", "%" + search + "%"]
		]

	# Query fields
	fields = [
		"name", "subject", "status", "priority", "ticket_type", "category",
		"requested_by", "assigned_to", "team", "sla_response_by", "sla_resolution_by",
		"creation", "modified"
	]

	# Get total count
	total_result = frappe.get_list(
		"NextHD Ticket",
		fields=["count(name) as total"],
		filters=filters,
		or_filters=or_filters
	)
	total = total_result[0].total if total_result else 0

	# Get rows
	limit_start = (page - 1) * page_size
	rows = frappe.get_list(
		"NextHD Ticket",
		fields=fields,
		filters=filters,
		or_filters=or_filters,
		order_by=order_by,
		limit_start=limit_start,
		limit_page_length=page_size
	)

	return {
		"rows": rows,
		"total": total,
		"page": page,
		"page_size": page_size,
		"server_now": now()
	}


@frappe.whitelist(methods=["GET"])
def get_ticket(name):
	"""Mengembalikan detail tiket beserta worklog dan waiting_log."""
	require_it_role()

	# Validasi parameter
	if not name or len(name) > 140:
		frappe.throw(_("Nama tiket tidak valid"), frappe.ValidationError)

	# Get doc dengan permission check
	doc = frappe.get_doc("NextHD Ticket", name)
	doc.check_permission("read")

	# Sanitasi deskripsi
	description = sanitize_html(doc.description) if doc.description else ""

	# Build worklog rows
	worklog_rows = []
	for row in doc.worklog:
		worklog_rows.append({
			"waktu": str(row.waktu) if row.waktu else "",
			"teknisi": row.teknisi or "",
			"aktivitas": row.aktivitas or "",
			"hasil": row.hasil or "",
			"durasi_menit": row.durasi_menit or 0
		})

	# Build waiting_log rows
	waiting_log_rows = []
	for row in doc.waiting_log:
		waiting_log_rows.append({
			"asked_on": str(row.asked_on) if row.asked_on else "",
			"asked_by": row.asked_by or "",
			"question": row.question or "",
			"replied_on": str(row.replied_on) if row.replied_on else "",
			"reply": row.reply or ""
		})

	return {
		"name": doc.name,
		"subject": doc.subject,
		"ticket_type": doc.ticket_type,
		"status": doc.status,
		"priority": doc.priority,
		"category": doc.category,
		"impact": doc.impact,
		"urgency": doc.urgency,
		"requested_by": doc.requested_by,
		"assigned_to": doc.assigned_to,
		"team": doc.team,
		"affected_asset": doc.affected_asset,
		"related_problem": doc.related_problem,
		"sla_response_by": str(doc.sla_response_by) if doc.sla_response_by else "",
		"sla_resolution_by": str(doc.sla_resolution_by) if doc.sla_resolution_by else "",
		"responded_on": str(doc.responded_on) if doc.responded_on else "",
		"resolved_on": str(doc.resolved_on) if doc.resolved_on else "",
		"closed_on": str(doc.closed_on) if doc.closed_on else "",
		"creation": str(doc.creation),
		"modified": str(doc.modified),
		"description": description,
		"worklog": worklog_rows,
		"waiting_log": waiting_log_rows,
		"server_now": now()
	}


@frappe.whitelist(methods=["POST"])
def create_ticket(data):
	"""Membuat tiket baru."""
	require_it_role()

	# Parse data jika berupa string
	if isinstance(data, str):
		data = frappe.parse_json(data)

	if not isinstance(data, dict):
		frappe.throw(_("Data harus berupa object"), frappe.ValidationError)

	# Whitelist kunci yang diizinkan
	ALLOWED_KEYS = {
		"ticket_type", "subject", "description", "category", "impact", "urgency",
		"requested_by", "affected_asset", "team", "assigned_to"
	}

	# Filter data - abaikan kunci terlarang
	filtered_data = {}
	for key, value in data.items():
		if key in ALLOWED_KEYS:
			filtered_data[key] = value

	# Sanitasi deskripsi saat disimpan
	if filtered_data.get("description"):
		filtered_data["description"] = sanitize_html(filtered_data["description"])

	# Validasi requested_by - hanya boleh user sendiri atau user dengan permission
	if filtered_data.get("requested_by"):
		if filtered_data["requested_by"] != frappe.session.user:
			# Hanya user dengan permission boleh membuat tiket untuk user lain
			if not frappe.has_permission("NextHD Ticket", "create", for_user=filtered_data["requested_by"]):
				frappe.throw(_("Anda tidak memiliki izin untuk membuat tiket untuk user lain"), frappe.PermissionError)

	# Validasi field wajib
	meta = frappe.get_meta("NextHD Ticket")
	required_fields = ["subject", "ticket_type", "requested_by"]
	for fieldname in required_fields:
		field = meta.get_field(fieldname)
		if field and field.reqd and not filtered_data.get(fieldname):
			# Default requested_by ke user saat ini jika kosong
			if fieldname == "requested_by":
				filtered_data["requested_by"] = frappe.session.user
			else:
				frappe.throw(_("{0} wajib diisi").format(field.label), frappe.ValidationError)

	# Cek field reqd lain dari meta
	for fieldname in ["category", "impact", "urgency"]:
		field = meta.get_field(fieldname)
		if field and field.reqd and not filtered_data.get(fieldname):
			frappe.throw(_("{0} wajib diisi").format(field.label), frappe.ValidationError)

	# Validasi panjang
	if filtered_data.get("subject") and len(filtered_data["subject"]) > 140:
		frappe.throw(_("Subject maksimal 140 karakter"), frappe.ValidationError)
	if filtered_data.get("description") and len(filtered_data["description"]) > 20000:
		frappe.throw(_("Deskripsi maksimal 20000 karakter"), frappe.ValidationError)

	# Buat dokumen tanpa ignore_permissions
	doc = frappe.get_doc({"doctype": "NextHD Ticket", **filtered_data})
	doc.insert()

	return {"name": doc.name}
