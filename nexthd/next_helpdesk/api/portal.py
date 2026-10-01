"""
NextHD - Portal API Endpoints

Endpoint untuk portal web NextHD (halaman www/).
Path panggil: nexthd.next_helpdesk.api.portal.<fungsi>
"""

import frappe
from frappe import _
from frappe.utils import now, get_fullname, now_datetime
from frappe.utils.html_utils import sanitize_html
from urllib.parse import quote

IT_ROLES = ("Agent", "Agent Manager", "IT Manager", "IT Auditor", "System Manager")
WRITER_ROLES = ("Agent", "Agent Manager", "IT Manager", "System Manager")
MANAGER_ROLES = ("Agent Manager", "IT Manager", "System Manager")


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
		redirect_to = quote(frappe.request.path + (frappe.request.query_string or ""))
		frappe.local.flags.redirect_location = "/login?redirect-to=" + redirect_to
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
	total = len(frappe.get_list(
		"NextHD Ticket",
		pluck="name",
		filters=filters,
		or_filters=or_filters,
		limit_page_length=0
	))

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


def _is_writer():
	"""Cek apakah user adalah penulis (punya minimal satu WRITER_ROLES)."""
	roles = _user_roles()
	return bool(roles.intersection(WRITER_ROLES))


def _is_manager():
	"""Cek apakah user adalah manajer (punya minimal satu MANAGER_ROLES)."""
	roles = _user_roles()
	return bool(roles.intersection(MANAGER_ROLES))


@frappe.whitelist(methods=["GET"])
def get_ticket_actions(name):
	"""Mengembalikan aksi workflow yang tersedia untuk tiket."""
	require_it_role()

	# Validasi parameter
	if not name or len(name) > 140:
		frappe.throw(_("Nama tiket tidak valid"), frappe.ValidationError)

	# Get doc dengan permission check
	doc = frappe.get_doc("NextHD Ticket", name)
	doc.check_permission("read")

	# Cek apakah user adalah penulis
	is_writer = _is_writer()

	# Get transitions dari workflow
	from frappe.model.workflow import get_transitions
	transitions = get_transitions(doc)

	# Filter actions hanya untuk penulis
	if not is_writer:
		transitions = []

	# Cek permission penugasan
	can_assign_self = is_writer
	can_assign_other = _is_manager()
	can_worklog = is_writer

	return {
		"actions": transitions,
		"can_assign_self": can_assign_self,
		"can_assign_other": can_assign_other,
		"can_worklog": can_worklog
	}


@frappe.whitelist(methods=["POST"])
def do_ticket_action(name, action, question=None):
	"""Menjalankan aksi workflow pada tiket."""
	require_it_role()

	# Tolak jika bukan penulis
	if not _is_writer():
		frappe.throw(_("Anda tidak memiliki izin untuk melakukan aksi ini"), frappe.PermissionError)

	# Validasi parameter
	if not name or len(name) > 140:
		frappe.throw(_("Nama tiket tidak valid"), frappe.ValidationError)
	if not action:
		frappe.throw(_("Aksi tidak valid"), frappe.ValidationError)

	# Get doc dengan permission check
	doc = frappe.get_doc("NextHD Ticket", name)
	doc.check_permission("write")

	# Validasi action ada di transitions
	from frappe.model.workflow import get_transitions
	transitions = get_transitions(doc)
	valid_actions = [t.action for t in transitions]
	if action not in valid_actions:
		frappe.throw(_("Aksi tidak tersedia untuk status tiket ini"), frappe.ValidationError)

	# Jalankan workflow
	from frappe.model.workflow import apply_workflow
	apply_workflow(doc, action)

	# Khusus aksi "Tunggu User": update question di waiting_log
	if action == "Tunggu User":
		if not question or not question.strip():
			frappe.throw(_("Pertanyaan wajib diisi untuk aksi Tunggu User"), frappe.ValidationError)
		if len(question) > 500:
			frappe.throw(_("Pertanyaan maksimal 500 karakter"), frappe.ValidationError)

		# Sanitasi question
		question = sanitize_html(question)

		# Cari baris waiting_log terbuka dengan idx terbesar
		waiting_log = frappe.db.get_list(
			"NextHD Ticket Waiting Log",
			filters={"parent": name, "replied_on": ["is", "not set"]},
			fields=["name", "idx"],
			order_by="idx desc",
			limit=1
		)

		if not waiting_log:
			frappe.throw(_("Baris waiting_log tidak ditemukan setelah aksi Tunggu User"), frappe.ValidationError)

		# Update hanya kolom question
		frappe.db.set_value("NextHD Ticket Waiting Log", waiting_log[0].name, "question", question)

	# Reload doc untuk mendapatkan status baru
	doc.reload()

	# Kembalikan ringkasan tiket
	return {
		"status": doc.status,
		"ticket": get_ticket(name)
	}


@frappe.whitelist(methods=["POST"])
def add_worklog(name, aktivitas, hasil=None, durasi_menit=None):
	"""Menambahkan catatan worklog ke tiket."""
	require_it_role()

	# Tolak jika bukan penulis
	if not _is_writer():
		frappe.throw(_("Anda tidak memiliki izin untuk menambah worklog"), frappe.PermissionError)

	# Validasi parameter
	if not name or len(name) > 140:
		frappe.throw(_("Nama tiket tidak valid"), frappe.ValidationError)
	if not aktivitas or not aktivitas.strip():
		frappe.throw(_("Aktivitas wajib diisi"), frappe.ValidationError)
	if len(aktivitas) > 1000:
		frappe.throw(_("Aktivitas maksimal 1000 karakter"), frappe.ValidationError)

	# Whitelist hasil
	HASIL_OPTIONS = ["Berhasil", "Belum Berhasil", "Perlu Eskalasi", "Menunggu Sparepart"]
	if hasil and hasil not in HASIL_OPTIONS:
		frappe.throw(_("Hasil tidak valid"), frappe.ValidationError)

	# Validasi durasi
	if durasi_menit is not None:
		try:
			durasi_menit = int(durasi_menit)
		except (ValueError, TypeError):
			frappe.throw(_("Durasi harus berupa angka"), frappe.ValidationError)
		if durasi_menit < 0 or durasi_menit > 1440:
			frappe.throw(_("Durasi harus antara 0 dan 1440 menit"), frappe.ValidationError)

	# Get doc dengan permission check
	doc = frappe.get_doc("NextHD Ticket", name)
	doc.check_permission("write")

	# Tolak jika tiket sudah ditutup
	if doc.status in ["Selesai", "Ditutup"]:
		frappe.throw(_("Tidak dapat menambah worklog pada tiket yang sudah selesai/ditutup"), frappe.ValidationError)

	# Tambah worklog
	doc.append("worklog", {
		"waktu": now_datetime(),
		"teknisi": frappe.session.user,
		"aktivitas": aktivitas,
		"hasil": hasil,
		"durasi_menit": durasi_menit or 0
	})
	doc.save()

	return {"success": True}


@frappe.whitelist(methods=["POST"])
def assign_ticket(name, user=None):
	"""Menugaskan tiket ke user."""
	require_it_role()

	# Tolak jika bukan penulis
	if not _is_writer():
		frappe.throw(_("Anda tidak memiliki izin untuk menugaskan tiket"), frappe.PermissionError)

	# Validasi parameter
	if not name or len(name) > 140:
		frappe.throw(_("Nama tiket tidak valid"), frappe.ValidationError)

	# Get doc dengan permission check
	doc = frappe.get_doc("NextHD Ticket", name)
	doc.check_permission("write")

	if user:
		# Dengan user: hanya manajer
		if not _is_manager():
			frappe.throw(_("Hanya manajer yang dapat menugaskan ke user lain"), frappe.PermissionError)

		# Validasi user ada
		if not frappe.db.exists("User", user):
			frappe.throw(_("User tidak ditemukan"), frappe.ValidationError)

		# Validasi user punya peran IT
		user_roles = frappe.get_roles(user)
		if not set(user_roles).intersection(IT_ROLES):
			frappe.throw(_("User tidak memiliki peran IT"), frappe.ValidationError)

		doc.assigned_to = user
	else:
		# Tanpa user: "Ambil untuk saya"
		# Hanya jika belum ditugaskan atau user adalah manajer
		if doc.assigned_to and doc.assigned_to != frappe.session.user and not _is_manager():
			frappe.throw(_("Tiket sudah ditugaskan ke user lain"), frappe.ValidationError)

		doc.assigned_to = frappe.session.user

	doc.save()

	return {"assigned_to": doc.assigned_to}


@frappe.whitelist(methods=["GET"])
def list_it_users():
	"""Mengembalikan daftar user dengan peran IT (hanya untuk manajer)."""
	require_it_role()

	# Hanya manajer
	if not _is_manager():
		frappe.throw(_("Hanya manajer yang dapat melihat daftar user IT"), frappe.PermissionError)

	# Ambil user dengan peran IT
	users = frappe.get_all(
		"User",
		filters={"enabled": 1},
		fields=["name", "full_name"]
	)

	# Filter user yang punya peran IT
	it_users = []
	for user in users:
		user_roles = frappe.get_roles(user.name)
		if set(user_roles).intersection(IT_ROLES):
			it_users.append({
				"name": user.name,
				"full_name": user.full_name or user.name
			})

	return {"users": it_users}


@frappe.whitelist(methods=["GET"])
def search_assets(query):
	"""Mencari aset untuk dropdown (batas 20 hasil)."""
	require_it_role()

	if not query or len(query) < 2:
		return {"assets": []}

	if len(query) > 100:
		query = query[:100]

	# Cek permission baca NextHD Asset
	if not frappe.has_permission("NextHD Asset", "read"):
		return {"assets": []}

	assets = frappe.get_list(
		"NextHD Asset",
		filters={"name": ["like", "%" + query + "%"]},
		fields=["name", "asset_name"],
		limit=20
	)

	return {"assets": assets}


@frappe.whitelist(methods=["GET"])
def search_users(query):
	"""Mencari user untuk dropdown (batas 20 hasil)."""
	require_it_role()

	if not query or len(query) < 2:
		return {"users": []}

	if len(query) > 100:
		query = query[:100]

	users = frappe.get_all(
		"User",
		filters={
			"enabled": 1,
			"name": ["like", "%" + query + "%"]
		},
		fields=["name", "full_name"],
		limit=20
	)

	# Filter user yang punya peran IT
	it_users = []
	for user in users:
		user_roles = frappe.get_roles(user.name)
		if set(user_roles).intersection(IT_ROLES):
			it_users.append({
				"name": user.name,
				"full_name": user.full_name or user.name
			})

	return {"users": it_users}
