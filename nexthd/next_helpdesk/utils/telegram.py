"""
NextHD - Telegram Notification Utility

Modul ini menangani semua pengiriman notifikasi ke Telegram.
Referensi: NEXTHD_SPEC.md bagian 5

STATUS: SKELETON - belum diimplementasikan, untuk Devin
"""

import frappe
import requests


def get_bot_token():
	"""
	Ambil bot token dari NextHD Settings.
	TODO (Devin): implementasi setelah Doctype NextHD Settings dibuat.
	"""
	return frappe.db.get_single_value("NextHD Settings", "telegram_bot_token")


def send_telegram_message(chat_id: str, message: str):
	"""
	Kirim pesan ke Telegram user tertentu.

	Args:
		chat_id: Telegram chat_id user (disimpan di NextHD User Profile)
		message: Isi pesan (boleh pakai Markdown/HTML sesuai parse_mode)

	TODO (Devin):
	- Ambil bot_token via get_bot_token()
	- POST ke https://api.telegram.org/bot{token}/sendMessage
	- Gunakan frappe.enqueue untuk kirim secara async (background job),
	  JANGAN kirim langsung secara sync di dalam request utama
	- Tangani error (chat_id invalid, network timeout, dll) dengan
	  frappe.log_error, jangan sampai proses utama (simpan tiket dll) gagal
	  hanya karena notifikasi Telegram gagal terkirim
	"""
	raise NotImplementedError("TODO: implementasikan pengiriman pesan Telegram")


def notify_ticket_created(ticket_name: str):
	"""Trigger saat NextHD Ticket baru dibuat -> notifikasi ke Team/Agent terkait."""
	raise NotImplementedError


def notify_ticket_assigned(ticket_name: str, agent_user: str):
	"""Trigger saat ticket di-assign ke Agent tertentu."""
	raise NotImplementedError


def notify_new_reply(ticket_name: str):
	"""Trigger saat ada comment/reply baru di timeline ticket."""
	raise NotImplementedError


def notify_ticket_resolved(ticket_name: str):
	"""Trigger saat status ticket berubah jadi Selesai -> notifikasi ke Requester."""
	raise NotImplementedError


def notify_sla_breach_warning(ticket_name: str):
	"""Trigger dari scheduled job saat SLA mendekati breach (H-30 menit)."""
	raise NotImplementedError


def notify_change_request_approval_needed(change_request_name: str):
	"""Trigger saat Change Request masuk status Diajukan -> notifikasi ke Approver."""
	raise NotImplementedError


def link_telegram_account(user: str, telegram_username: str, verification_code: str):
	"""
	Proses linking akun Telegram ke User NextHD.
	Dipanggil dari webhook bot saat user kirim /start + kode verifikasi.

	TODO (Devin):
	- Desain alur verifikasi (misal: user generate kode dari halaman profile,
	  lalu kirim kode itu ke bot untuk konfirmasi kepemilikan)
	- Simpan chat_id ke NextHD User Profile setelah verifikasi berhasil
	"""
	raise NotImplementedError
