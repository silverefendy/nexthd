"""
NextHD - Scheduled Tasks

Contains scheduled jobs for SLA monitoring and other periodic tasks.
Referensi: NEXTHD_SPEC.md bagian 8
"""

import frappe
from datetime import datetime, timedelta
from frappe.utils import now_datetime


def check_sla_breach_warnings():
	"""
	Scheduled job to check for tickets approaching SLA breach.
	Runs every 15 minutes. Sends warning only once per ticket (throttled by sla_warning_sent flag).
	"""
	try:
		now_time = now_datetime()
		thirty_minutes_from_now = now_time + timedelta(minutes=30)

		tickets = frappe.db.get_all("NextHD Ticket",
			filters=[
				["status", "in", ["Baru", "Sedang Dikerjakan", "Menunggu User"]],
				["sla_resolution_by", "<=", thirty_minutes_from_now],
				["sla_resolution_by", ">", now_time],
				["sla_warning_sent", "=", 0]
			],
			pluck="name"
		)

		for ticket_name in tickets:
			from nexthd.next_helpdesk.utils.telegram import notify_sla_breach_warning
			notify_sla_breach_warning(ticket_name)
			# Mark as warned so we don't spam
			frappe.db.set_value("NextHD Ticket", ticket_name, "sla_warning_sent", 1)

		if tickets:
			frappe.db.commit()

		frappe.logger().info(f"SLA breach warning check completed. Warned {len(tickets)} tickets.")

	except Exception as e:
		frappe.log_error(f"Error in SLA breach warning check: {str(e)}")


def check_sla_response_breach():
	"""
	Scheduled job to check for tickets approaching SLA response breach.
	Runs every 5 minutes to check for tickets within 15 minutes of response SLA deadline.
	"""
	try:
		now_time = now_datetime()
		fifteen_minutes_from_now = now_time + timedelta(minutes=15)
		
		# Query tickets with response SLA approaching
		tickets = frappe.db.get_all("NextHD Ticket",
			filters=[
				["status", "=", "Baru"],
				["sla_response_by", "<=", fifteen_minutes_from_now],
				["sla_response_by", ">", now_time]
			],
			pluck="name"
		)
		
		for ticket_name in tickets:
			# Send warning for response SLA
			# Similar to resolution SLA but for initial response
			from nexthd.next_helpdesk.utils.telegram import send_telegram_message, get_user_chat_id
			
			ticket = frappe.get_doc("NextHD Ticket", ticket_name)
			
			# Notify team members
			if ticket.team:
				team = frappe.get_doc("NextHD Team", ticket.team)
				for member in team.members:
					chat_id = get_user_chat_id(member.user)
					if chat_id:
						message = (
							f"⏰ <b>Peringatan SLA Response</b>\n"
							f"Tiket: {ticket_name}\n"
							f"Subjek: {ticket.subject}\n"
							f"Prioritas: {ticket.priority}\n"
							f"SLA response akan terlampaui dalam 15 menit. Segera respon!"
						)
						send_telegram_message(chat_id, message)
		
		frappe.logger.info(f"SLA response breach check completed. Checked {len(tickets)} tickets.")
	
	except Exception as e:
		frappe.log_error(f"Error in SLA response breach check: {str(e)}")
