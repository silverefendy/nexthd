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
	"""
	bot_token = get_bot_token()
	if not bot_token:
		frappe.log_error("Telegram bot token not configured in NextHD Settings")
		return

	url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
	payload = {
		"chat_id": chat_id,
		"text": message,
		"parse_mode": "HTML"
	}

	try:
		response = requests.post(url, json=payload, timeout=10)
		response.raise_for_status()
	except Exception as e:
		frappe.log_error(f"Failed to send Telegram message to {chat_id}: {str(e)}")


def notify_ticket_created(doc, method):
	"""
	Hook dipanggil oleh Frappe saat NextHD Ticket baru di-insert.
	Signature (doc, method) adalah standar Frappe doc_events hook.
	"""
	if not is_telegram_enabled():
		return

	frappe.enqueue(
		"nexthd.next_helpdesk.utils.telegram._send_ticket_created_notification",
		queue="short",
		ticket_name=doc.name
	)


def _send_ticket_created_notification(ticket_name: str):
	"""Internal function to send ticket created notification"""
	try:
		ticket = frappe.get_doc("NextHD Ticket", ticket_name)
		notified_users = set()

		# Notify team members if team is assigned
		if ticket.team:
			team = frappe.get_doc("NextHD Team", ticket.team)
			for member in team.members:
				chat_id = get_user_chat_id(member.user)
				if chat_id and member.user not in notified_users:
					message = (
						f"🎫 <b>Tiket Baru</b>\n"
						f"No: {ticket_name}\n"
						f"Subjek: {ticket.subject}\n"
						f"Prioritas: {ticket.priority}\n"
						f"Dilaporkan oleh: {ticket.requested_by}\n"
						f"Kategori: {ticket.category or 'N/A'}"
					)
					send_telegram_message(chat_id, message)
					notified_users.add(member.user)

		# Notify assigned agent if assigned (skip if already notified as team member)
		if ticket.assigned_to and ticket.assigned_to not in notified_users:
			chat_id = get_user_chat_id(ticket.assigned_to)
			if chat_id:
				message = (
					f"🎫 <b>Tiket Baru Ditugaskan ke Anda</b>\n"
					f"No: {ticket_name}\n"
					f"Subjek: {ticket.subject}\n"
					f"Prioritas: {ticket.priority}"
				)
				send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in ticket created notification: {str(e)}")


def notify_ticket_assigned(ticket_name: str, agent_user: str):
	"""
	Trigger saat ticket di-assign ke Agent tertentu.
	Dikirim secara async via frappe.enqueue.
	"""
	if not is_telegram_enabled():
		return

	frappe.enqueue(
		"nexthd.next_helpdesk.utils.telegram._send_ticket_assigned_notification",
		queue="short",
		ticket_name=ticket_name,
		agent_user=agent_user
	)


def notify_ticket_updated(doc, method):
	"""
	Wrapper function for ticket update events.
	Called from hooks.py on_update event.
	Handles both assignment and resolution notifications.
	"""
	if not is_telegram_enabled():
		return
	
	try:
		# Check if assigned_to changed
		if doc.assigned_to and not doc.is_new():
			old_doc = doc.get_doc_before_save()
			if old_doc and old_doc.assigned_to != doc.assigned_to:
				notify_ticket_assigned(doc.name, doc.assigned_to)
		
		# Check if status changed to Selesai
		if doc.status == "Selesai" and not doc.is_new():
			old_doc = doc.get_doc_before_save()
			if old_doc and old_doc.status != "Selesai":
				notify_ticket_resolved(doc.name)
	except Exception as e:
		frappe.log_error(f"Error in ticket updated notification: {str(e)}")


def _send_ticket_assigned_notification(ticket_name: str, agent_user: str):
	"""Internal function to send ticket assigned notification"""
	try:
		ticket = frappe.get_doc("NextHD Ticket", ticket_name)
		chat_id = get_user_chat_id(agent_user)
		
		if chat_id:
			message = (
				f"✅ <b>Tiket Ditugaskan</b>\n"
				f"No: {ticket_name}\n"
				f"Subjek: {ticket.subject}\n"
				f"Prioritas: {ticket.priority}\n"
				f"Anda telah ditugaskan untuk menangani tiket ini."
			)
			send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in ticket assigned notification: {str(e)}")


def notify_new_reply(doc, method):
	"""
	Trigger saat ada comment/reply baru di timeline ticket.
	Dikirim secara async via frappe.enqueue.
	"""
	if not is_telegram_enabled():
		return
	
	# Check if comment is related to NextHD Ticket
	if doc.reference_doctype != "NextHD Ticket":
		return
	
	frappe.enqueue(
		"nexthd.next_helpdesk.utils.telegram._send_new_reply_notification",
		queue="short",
		ticket_name=doc.reference_name
	)


def _send_new_reply_notification(ticket_name: str):
	"""Internal function to send new reply notification"""
	try:
		ticket = frappe.get_doc("NextHD Ticket", ticket_name)
		
		# Notify requester
		if ticket.requested_by:
			chat_id = get_user_chat_id(ticket.requested_by)
			if chat_id:
				message = (
					f"💬 <b>Balasan Baru</b>\n"
					f"Tiket: {ticket_name}\n"
					f"Subjek: {ticket.subject}\n"
					f"Ada balasan baru pada tiket Anda."
				)
				send_telegram_message(chat_id, message)
		
		# Notify assigned agent
		if ticket.assigned_to:
			chat_id = get_user_chat_id(ticket.assigned_to)
			if chat_id:
				message = (
					f"💬 <b>Balasan Baru</b>\n"
					f"Tiket: {ticket_name}\n"
					f"Subjek: {ticket.subject}\n"
					f"Ada balasan baru pada tiket yang Anda tugaskan."
				)
				send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in new reply notification: {str(e)}")


def notify_ticket_resolved(ticket_name: str):
	"""
	Trigger saat status ticket berubah jadi Selesai -> notifikasi ke Requester.
	Dikirim secara async via frappe.enqueue.
	"""
	if not is_telegram_enabled():
		return

	frappe.enqueue(
		"nexthd.next_helpdesk.utils.telegram._send_ticket_resolved_notification",
		queue="short",
		ticket_name=ticket_name
	)


def _send_ticket_resolved_notification(ticket_name: str):
	"""Internal function to send ticket resolved notification"""
	try:
		ticket = frappe.get_doc("NextHD Ticket", ticket_name)
		chat_id = get_user_chat_id(ticket.requested_by)
		
		if chat_id:
			message = (
				f"✅ <b>Tiket Diselesaikan</b>\n"
				f"Tiket: {ticket_name}\n"
				f"Subjek: {ticket.subject}\n"
				f"Tiket Anda telah diselesaikan. Mohon konfirmasi jika sudah sesuai."
			)
			send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in ticket resolved notification: {str(e)}")


def notify_sla_breach_warning(ticket_name: str):
	"""
	Trigger dari scheduled job saat SLA mendekati breach (H-30 menit).
	Dikirim secara async via frappe.enqueue.
	"""
	if not is_telegram_enabled():
		return

	frappe.enqueue(
		"nexthd.next_helpdesk.utils.telegram._send_sla_breach_warning_notification",
		queue="short",
		ticket_name=ticket_name
	)


def _send_sla_breach_warning_notification(ticket_name: str):
	"""Internal function to send SLA breach warning notification"""
	try:
		ticket = frappe.get_doc("NextHD Ticket", ticket_name)
		
		# Notify assigned agent
		if ticket.assigned_to:
			chat_id = get_user_chat_id(ticket.assigned_to)
			if chat_id:
				message = (
					f"⚠️ <b>Peringatan SLA</b>\n"
					f"Tiket: {ticket_name}\n"
					f"Subjek: {ticket.subject}\n"
					f"Prioritas: {ticket.priority}\n"
					f"SLA akan terlampaui dalam 30 menit. Segera tangani!"
				)
				send_telegram_message(chat_id, message)
		
		# Notify team if assigned
		if ticket.team:
			team = frappe.get_doc("NextHD Team", ticket.team)
			for member in team.members:
				chat_id = get_user_chat_id(member.user)
				if chat_id:
					message = (
						f"⚠️ <b>Peringatan SLA Tim</b>\n"
						f"Tiket: {ticket_name}\n"
						f"Subjek: {ticket.subject}\n"
						f"SLA akan terlampaui dalam 30 menit."
					)
					send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in SLA breach warning notification: {str(e)}")


def notify_change_request_approval_needed(doc, method):
	"""
	Trigger saat Change Request masuk status Diajukan -> notifikasi ke Approver.
	Dikirim secara async via frappe.enqueue.
	"""
	if not is_telegram_enabled():
		return
	
	# Only notify when status changes to Diajukan
	if doc.status != "Diajukan":
		return
	
	# Check if this is a status change
	if doc.is_new():
		return
	
	old_doc = doc.get_doc_before_save()
	if old_doc and old_doc.status != "Diajukan":
		frappe.enqueue(
			"nexthd.next_helpdesk.utils.telegram._send_change_request_approval_notification",
			queue="short",
			change_request_name=doc.name
		)


def _send_change_request_approval_notification(change_request_name: str):
	"""Internal function to send change request approval notification"""
	try:
		cr = frappe.get_doc("NextHD Change Request", change_request_name)
		
		# Notify users with IT Manager or Agent Manager roles
		managers = frappe.get_all("Has Role", {
			"role": ["in", ["IT Manager", "Agent Manager"]],
			"parenttype": "User"
		}, pluck="parent")
		
		for manager in managers:
			chat_id = get_user_chat_id(manager)
			if chat_id:
				message = (
					f"📋 <b>Change Request Menunggu Persetujuan</b>\n"
					f"No: {change_request_name}\n"
					f"Judul: {cr.title}\n"
					f"Tipe: {cr.change_type}\n"
					f"Risiko: {cr.risk_level}\n"
					"Mohon review dan setujui/tolak."
				)
				send_telegram_message(chat_id, message)
	except Exception as e:
		frappe.log_error(f"Error in change request approval notification: {str(e)}")


def link_telegram_account(user: str, telegram_username: str, chat_id: str):
	"""
	Proses linking akun Telegram ke User NextHD.
	Dipanggil dari webhook bot saat user kirim /start + kode verifikasi.
	Jika User Profile belum ada, akan dibuat otomatis.
	"""
	try:
		# Try to get existing profile
		profile_name = frappe.db.get_value("NextHD User Profile", {"user": user}, "name")
		
		if profile_name:
			profile = frappe.get_doc("NextHD User Profile", profile_name)
			if profile.telegram_chat_id:
				# Already linked
				return False
		else:
			# Create new profile if not exists
			profile = frappe.new_doc("NextHD User Profile")
			profile.user = user

		# Link the account
		profile.telegram_username = telegram_username
		profile.telegram_chat_id = chat_id
		profile.save(ignore_permissions=True)
		frappe.db.commit()

		return True
	except Exception as e:
		frappe.log_error(f"Error linking Telegram account for {user}: {str(e)}")
		return False


def get_user_chat_id(user: str) -> str:
	"""
	Get Telegram chat_id for a user.
	
	Args:
		user: User email or username
		
	Returns:
		Telegram chat_id or None if not linked
	"""
	try:
		profile_name = frappe.db.get_value("NextHD User Profile", {"user": user}, "name")
		if profile_name:
			profile = frappe.get_doc("NextHD User Profile", profile_name)
			return profile.telegram_chat_id
		return None
	except Exception:
		return None


def is_telegram_enabled() -> bool:
	"""Check if Telegram notification is enabled in settings"""
	try:
		enabled = frappe.db.get_single_value("NextHD Settings", "enable_telegram_notification")
		return bool(enabled)
	except Exception:
		return False
