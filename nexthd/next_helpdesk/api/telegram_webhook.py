"""
NextHD - Telegram Webhook Endpoint

Menerima update dari Telegram Bot API dan memprosesnya.
Referensi: NEXTHD_SPEC.md bagian 5
"""

import frappe
import json
from frappe import _
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def telegram_webhook():
	"""
	Webhook endpoint untuk menerima update dari Telegram Bot API.
	Dipanggil oleh Telegram saat ada event baru (message, callback, dll).
	"""
	try:
		# Get the request data
		if frappe.request.method == "POST":
			data = frappe.request.get_json()
			
			if not data:
				frappe.log_error("Empty webhook data received")
				return {"status": "error", "message": "No data received"}
			
			# Process the update
			process_telegram_update(data)
			
			return {"status": "ok"}
		else:
			return {"status": "error", "message": "Only POST method allowed"}
	
	except Exception as e:
		frappe.log_error(f"Error in telegram webhook: {str(e)}")
		return {"status": "error", "message": str(e)}


def process_telegram_update(update):
	"""
	Process incoming Telegram update.
	
	Args:
		update: Dictionary containing the update data from Telegram
	"""
	# Extract message from update
	message = update.get("message")
	if not message:
		# Handle other update types (callback_query, edited_message, etc.)
		return
	
	# Extract chat_id and text
	chat = message.get("chat")
	if not chat:
		return
	
	chat_id = chat.get("id")
	text = message.get("text", "")
	
	if not text:
		return
	
	# Process commands
	if text.startswith("/"):
		process_command(chat_id, text, message)
	else:
		# Handle regular messages (for linking accounts)
		process_message(chat_id, text, message)


def process_command(chat_id, text, message):
	"""
	Process Telegram bot commands.
	
	Args:
		chat_id: Telegram chat ID
		text: Command text (e.g., /start, /help)
		message: Full message object
	"""
	from nexthd.next_helpdesk.utils.telegram import send_telegram_message
	
	if text == "/start":
		# Send welcome message with instructions
		welcome_message = (
			"👋 <b>Selamat datang di NextHD Bot!</b>\n\n"
			"Untuk menghubungkan akun Telegram Anda dengan NextHD:\n"
			"1. Buka halaman profil Anda di NextHD\n"
			"2. Klik tombol 'Link Telegram Account'\n"
			"3. Salin kode verifikasi 6 digit yang ditampilkan\n"
			"4. Kirim kode tersebut ke bot ini dalam 10 menit\n\n"
			"Contoh: 847291"
		)
		send_telegram_message(chat_id, welcome_message)
	
	elif text == "/help":
		help_message = (
			"📖 <b>Bantuan NextHD Bot</b>\n\n"
			"<b>Perintah yang tersedia:</b>\n"
			"/start - Memulai dan mendapatkan instruksi\n"
			"/help - Menampilkan pesan bantuan ini\n\n"
			"<b>Link Akun:</b>\n"
			"Kirim kode verifikasi 6 digit dari profil NextHD Anda\n"
			"Kode berlaku selama 10 menit"
		)
		send_telegram_message(chat_id, help_message)
	
	elif text.startswith("/link "):
		# Process link command
		code = text.replace("/link ", "").strip()
		process_link_code(chat_id, code)
	
	elif text.startswith("LINK "):
		# Process LINK command (alternative format)
		code = text.replace("LINK ", "").strip()
		process_link_code(chat_id, code)


def process_link_code(chat_id, code):
	"""
	Process account linking code using OTP-based verification.
	
	Args:
		chat_id: Telegram chat ID
		code: 6-digit verification code from NextHD profile
	"""
	from nexthd.next_helpdesk.utils.telegram import send_telegram_message, link_telegram_account
	
	try:
		# Find user profile with this verification code that hasn't expired
		profile_name = frappe.db.get_value(
			"NextHD User Profile",
			{
				"telegram_link_code": code,
				"telegram_link_code_expiry": (">", datetime.now())
			},
			"name"
		)
		
		if not profile_name:
			# Check if code exists but expired
			expired_profile = frappe.db.get_value(
				"NextHD User Profile",
				{"telegram_link_code": code},
				"name"
			)
			
			if expired_profile:
				send_telegram_message(
					chat_id,
					"❌ Kode verifikasi sudah kedaluwarsa (berlaku 10 menit). Silakan generate kode baru dari halaman profil NextHD Anda."
				)
			else:
				send_telegram_message(
					chat_id,
					"❌ Kode verifikasi tidak valid. Silakan generate kode baru dari halaman profil NextHD Anda."
				)
			return
		
		# Get the profile to check if already linked and get user
		profile = frappe.get_doc("NextHD User Profile", profile_name)
		
		# Check if already linked
		if profile.telegram_chat_id:
			send_telegram_message(
				chat_id,
				"❌ Akun Telegram Anda sudah terhubung sebelumnya."
			)
			return
		
		# Link the account
		success = link_telegram_account(profile.user, "", str(chat_id))
		
		if success:
			# Clear the link code and expiry after successful linking
			frappe.db.set_value("NextHD User Profile", profile_name, {
				"telegram_link_code": "",
				"telegram_link_code_expiry": None
			})
			frappe.db.commit()
			
			send_telegram_message(
				chat_id,
				f"✅ Akun Telegram berhasil dihubungkan dengan NextHD!\n\n"
				f"User: {profile.user}\n"
				f"Anda akan menerima notifikasi tiket melalui Telegram ini."
			)
		else:
			send_telegram_message(
				chat_id,
				"❌ Gagal menghubungkan akun. Silakan coba lagi nanti."
			)
	
	except Exception as e:
		frappe.log_error(f"Error processing link code: {str(e)}")
		send_telegram_message(
			chat_id,
			"❌ Terjadi kesalahan saat menghubungkan akun. Silakan coba lagi nanti."
		)


def process_message(chat_id, text, message):
	"""
	Process regular (non-command) messages.
	
	Args:
		chat_id: Telegram chat ID
		text: Message text
		message: Full message object
	"""
	from nexthd.next_helpdesk.utils.telegram import send_telegram_message
	
	# If the message looks like a verification code, try to process it
	if text.strip().isdigit() or len(text.strip()) <= 10:
		process_link_code(chat_id, text.strip())
	else:
		# Send help message for unrecognized messages
		help_message = (
			"🤔 Saya tidak mengerti pesan tersebut.\n\n"
			"Gunakan /help untuk melihat perintah yang tersedia."
		)
		send_telegram_message(chat_id, help_message)
