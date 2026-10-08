# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_asset_list_for_ticket(doctype, txt, searchfield, start, page_len, filters):
	"""
	Query Link standar untuk dropdown Affected Asset di NextHD Ticket.
	Menampilkan aset yang terkait dengan pelapor lebih dulu.
	"""
	requested_by = filters.get("requested_by") if filters else None
	semua = filters.get("semua") if filters else 0

	# Jika requested_by kosong atau flag semua=1: kembalikan semua aset yang boleh dibaca
	if not requested_by or semua == 1:
		assets = frappe.get_list(
			doctype,
			fields=["name", "asset_name"],
			filters=[
				[doctype, "asset_name", "like", "%{0}%".format(txt)],
				[doctype, "name", "like", "%{0}%".format(txt)],
			],
			or_filters=[
				[doctype, "asset_name", "like", "%{0}%".format(txt)],
				[doctype, "name", "like", "%{0}%".format(txt)],
			],
			start=start,
			page_length=page_len
		)
		return [{"value": a.name, "label": "{0} ({1})".format(a.asset_name, a.name)} for a in assets]

	# Jika tidak: kumpulkan nama aset di mana assigned_to = requested_by ATAU requested_by ada di asset_users
	# Query untuk assigned_to
	assigned_assets = frappe.get_all(
		doctype,
		filters={"assigned_to": requested_by},
		fields=["name"]
	)
	assigned_names = [a.name for a in assigned_assets]

	# Query untuk asset_users
	user_assets = frappe.get_all(
		"NextHD Asset User",
		filters={"user": requested_by},
		fields=["parent"]
	)
	user_asset_names = [u.parent for u in user_assets]

	# Gabungkan dan dedup
	all_asset_names = list(set(assigned_names + user_asset_names))

	if not all_asset_names:
		return []

	# Ambil aset dengan name in daftar itu (aturan izin tetap berlaku)
	assets = frappe.get_list(
		doctype,
		fields=["name", "asset_name"],
		filters={
			"name": ["in", all_asset_names]
		},
		or_filters=[
			[doctype, "asset_name", "like", "%{0}%".format(txt)],
			[doctype, "name", "like", "%{0}%".format(txt)],
		],
		start=start,
		page_length=page_len
	)
	return [{"value": a.name, "label": "{0} ({1})".format(a.asset_name, a.name)} for a in assets]
