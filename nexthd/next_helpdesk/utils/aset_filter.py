# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


@frappe.whitelist()
def get_asset_list_for_ticket(doctype, txt, searchfield, start, page_len, filters):
    """
    Query Link untuk dropdown Affected Asset di NextHD Ticket.
    Mengembalikan list tuple (value, label) sesuai format query Link Frappe.
    """
    filters = filters or {}
    requested_by = filters.get("requested_by")
    try:
        semua = int(filters.get("semua") or 0)
    except (TypeError, ValueError):
        semua = 0

    like = "%{0}%".format(txt or "")
    or_filters = [
        [doctype, "asset_name", "like", like],
        [doctype, "name", "like", like],
    ]

    if not requested_by or semua == 1:
        base_filters = {}
    else:
        assigned = frappe.get_all(doctype, filters={"assigned_to": requested_by}, pluck="name")
        shared = frappe.get_all("NextHD Asset User", filters={"user": requested_by}, pluck="parent")
        names = list(set(assigned + shared))
        if not names:
            return []
        base_filters = {"name": ["in", names]}

    assets = frappe.get_list(
        doctype,
        fields=["name", "asset_name"],
        filters=base_filters,
        or_filters=or_filters,
        start=start,
        page_length=page_len,
    )
    return [(a.name, "{0} ({1})".format(a.asset_name, a.name)) for a in assets]
