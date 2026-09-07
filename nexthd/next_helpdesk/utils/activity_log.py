# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import now


def _add_activity_log_entry(doctype, docname, status_from=None, status_to=None,
                              entry_type="Otomatis", note=None,
                              related_doctype=None, related_document=None):
    """
    Insert activity log entry using direct SQL to avoid child table sync issues.
    
    This function MUST use frappe.db.sql() INSERT directly instead of ORM insert()
    to prevent the bug where new rows don't sync to in-memory child tables.
    See: docs/POLA_KERJA_DAN_BUG.md bug session 22 Agustus item B
    """
    if not note and entry_type == "Otomatis" and status_from and status_to:
        note = f"Status berubah dari {status_from} ke {status_to}"

    frappe.db.sql("""
        INSERT INTO `tabNextHD Activity Log` 
        (name, parent, parenttype, parentfield, idx,
         timestamp, updated_by, entry_type, status_from, status_to, note,
         related_doctype, related_document,
         creation, modified, modified_by, owner)
        VALUES (%(name)s, %(parent)s, %(parenttype)s, 'activity_log',
                (SELECT n FROM (SELECT COALESCE(MAX(idx), 0) + 1 AS n FROM `tabNextHD Activity Log` 
                 WHERE parent = %(parent)s) AS t),
                %(timestamp)s, %(user)s, %(entry_type)s, %(status_from)s, %(status_to)s, %(note)s,
                %(related_doctype)s, %(related_document)s,
                NOW(), NOW(), %(user)s, %(user)s)
    """, {
        "name": frappe.generate_hash(length=10),
        "parent": docname,
        "parenttype": doctype,
        "timestamp": now(),
        "user": frappe.session.user,
        "entry_type": entry_type,
        "status_from": status_from,
        "status_to": status_to,
        "note": note,
        "related_doctype": related_doctype,
        "related_document": related_document
    })
    frappe.db.commit()


@frappe.whitelist()
def log_cross_document_link(source_doctype, source_name, target_doctype, target_name):
    """
    Insert 2 baris Activity Log saling menunjuk antara source dan target.
    
    Called from Client Scripts after successful document conversion.
    """
    _add_activity_log_entry(
        doctype=source_doctype, docname=source_name,
        entry_type="Otomatis",
        note=f"Dibuat {target_doctype.replace('NextHD ', '')} terkait",
        related_doctype=target_doctype, related_document=target_name
    )
    _add_activity_log_entry(
        doctype=target_doctype, docname=target_name,
        entry_type="Otomatis",
        note=f"Dibuat dari {source_doctype.replace('NextHD ', '')} ini",
        related_doctype=source_doctype, related_document=source_name
    )
