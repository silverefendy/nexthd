"""
NextHD - Installation hooks
Dipanggil otomatis oleh Frappe saat: bench install-app nexthd
"""

import frappe


def after_install():
	"""Seed default data setelah install"""
	create_default_roles()
	create_default_business_hours()
	create_default_sla_policies()
	frappe.db.commit()
	print("NextHD: Default data berhasil dibuat.")


def create_default_roles():
	"""Buat roles yang dibutuhkan NextHD jika belum ada"""
	roles = ["Requester", "Agent", "Agent Manager", "IT Manager", "IT Auditor"]
	for role_name in roles:
		if not frappe.db.exists("Role", role_name):
			role = frappe.new_doc("Role")
			role.role_name = role_name
			role.desk_access = 1
			role.save(ignore_permissions=True)
			print(f"NextHD: Created role '{role_name}'")


def create_default_business_hours():
	"""Buat Business Hours default (Senin-Jumat 08:00-17:00) jika belum ada"""
	working_days = [
		{"day": "Senin", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
		{"day": "Selasa", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
		{"day": "Rabu", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
		{"day": "Kamis", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
		{"day": "Jumat", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 1},
		{"day": "Sabtu", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 0},
		{"day": "Minggu", "start_time": "08:00:00", "end_time": "17:00:00", "is_working_day": 0},
	]

	for day_config in working_days:
		day = day_config["day"]
		if frappe.db.exists("NextHD Business Hours", day):
			continue

		bh = frappe.new_doc("NextHD Business Hours")
		bh.day = day
		bh.start_time = day_config["start_time"]
		bh.end_time = day_config["end_time"]
		bh.is_working_day = day_config["is_working_day"]
		bh.save(ignore_permissions=True)
		print(f"NextHD: Created business hours for '{day}'")


def create_default_sla_policies():
	"""Buat SLA Policy default untuk setiap level prioritas"""
	policies = [
		{"priority": "Kritis",  "response_time_minutes": 30,   "resolution_time_minutes": 240},
		{"priority": "Tinggi",  "response_time_minutes": 120,  "resolution_time_minutes": 480},
		{"priority": "Sedang",  "response_time_minutes": 480,  "resolution_time_minutes": 1440},
		{"priority": "Rendah",  "response_time_minutes": 1440, "resolution_time_minutes": 4320},
	]

	for policy_data in policies:
		priority = policy_data["priority"]
		if frappe.db.exists("NextHD SLA Policy", priority):
			continue

		policy = frappe.new_doc("NextHD SLA Policy")
		policy.priority = priority
		policy.response_time_minutes = policy_data["response_time_minutes"]
		policy.resolution_time_minutes = policy_data["resolution_time_minutes"]
		policy.save(ignore_permissions=True)
		print(f"NextHD: Created SLA Policy for '{priority}'")
