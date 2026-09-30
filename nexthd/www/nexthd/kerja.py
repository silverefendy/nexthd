import frappe
from nexthd.next_helpdesk.api.portal import page_guard


def get_context(context):
	page_guard(context)
	context.title = "Ruang Kerja"
