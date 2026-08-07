"""
NextHD - Scheduled Tasks

Contains scheduled jobs for SLA monitoring and other periodic tasks.
Referensi: NEXTHD_SPEC.md bagian 8
"""

import frappe
from datetime import datetime, timedelta
from frappe.utils import now


def check_sla_breach_warnings():
	"""
	Scheduled job to check for tickets approaching SLA breach.
	Runs every 15 minutes to check for tickets within 30 minutes of SLA deadline.
	
	This should be registered in hooks.py under scheduler_events:
		scheduler_events = {
			"cron": {
				"*/15 * * * *": ["nexthd.next_helpdesk.tasks.check_sla_breach_warnings"]
			}
		}
	"""
	try:
		# Get current time
		now_time = now()
		
		# Check for tickets with SLA resolution deadline in the next 30 minutes
		thirty_minutes_from_now = now_time + timedelta(minutes=30)
		
		# Query tickets that:
		# - Have sla_resolution_by set
		# - sla_resolution_by is within 30 minutes from now
		# - Status is not Selesai or Ditutup
		# - Haven't been warned in the last hour (to avoid duplicate warnings)
		
		tickets = frappe.db.get_all("NextHD Ticket", {
			"status": ["in", ["Baru", "Sedang Dikerjakan", "Menunggu User"]],
			"sla_resolution_by": ["<=", thirty_minutes_from_now],
			"sla_resolution_by": [">", now_time]
		}, pluck="name")
		
		for ticket_name in tickets:
			# Check if we've already warned about this ticket recently
			# Use a simple flag or check the last notification time
			# For now, we'll send the notification
			from nexthd.next_helpdesk.utils.telegram import notify_sla_breach_warning
			notify_sla_breach_warning(ticket_name)
		
		frappe.logger.info(f"SLA breach warning check completed. Checked {len(tickets)} tickets.")
	
	except Exception as e:
		frappe.log_error(f"Error in SLA breach warning check: {str(e)}")


def check_sla_response_breach():
	"""
	Scheduled job to check for tickets approaching SLA response breach.
	Runs every 5 minutes to check for tickets within 15 minutes of response SLA deadline.
	"""
	try:
		now_time = now()
		fifteen_minutes_from_now = now_time + timedelta(minutes=15)
		
		# Query tickets with response SLA approaching
		tickets = frappe.db.get_all("NextHD Ticket", {
			"status": "Baru",
			"sla_response_by": ["<=", fifteen_minutes_from_now],
			"sla_response_by": [">", now_time]
		}, pluck="name")
		
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
