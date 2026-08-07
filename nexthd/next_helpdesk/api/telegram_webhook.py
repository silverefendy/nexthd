"""
NextHD - Telegram Webhook Endpoint

Menerima update dari Telegram Bot API dan memprosesnya.
Referensi: NEXTHD_SPEC.md bagian 5
"""

import frappe
import json
from frappe import _

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
			"2. Klik 'Link Telegram Account'\n"
			"3. Masukkan kode verifikasi yang ditampilkan\n"
			"4. Kirim kode tersebut ke bot ini\n\n"
			"Contoh: LINK 12345"
		)
		send_telegram_message(chat_id, welcome_message)
	
	elif text == "/help":
		help_message = (
			"📖 <b>Bantuan NextHD Bot</b>\n\n"
			"<b>Perintah yang tersedia:</b>\n"
			"/start - Memulai dan mendapatkan instruksi\n"
			"/help - Menampilkan pesan bantuan ini\n\n"
			"<b>Link Akun:</b>\n"
			"Kirim kode verifikasi dari profil NextHD Anda\n"
			"Format: LINK <kode_verifikasi>"
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
	Process account linking code.
	
	Args:
		chat_id: Telegram chat ID
		code: Verification code from NextHD profile
	"""
	from nexthd.next_helpdesk.utils.telegram import send_telegram_message, link_telegram_account
	
	try:
		# Find user profile with this verification code
		# In production, this should use a proper verification system
		# For now, we'll use a simple approach where the code is the username
		
		# Try to find user by username
		user = frappe.db.get_value("User", {"username": code}, "name")
		
		if not user:
			send_telegram_message(
				chat_id,
				"❌ Kode verifikasi tidak valid. Silakan periksa kode di profil NextHD Anda."
			)
			return
		
		# Link the account
		success = link_telegram_account(user, "", str(chat_id))
		
		if success:
			send_telegram_message(
				chat_id,
				f"✅ Akun Telegram berhasil dihubungkan dengan NextHD!\n\n"
				f"Username: {user}\n"
				f"Anda akan menerima notifikasi tiket melalui Telegram ini."
			)
		else:
			send_telegram_message(
				chat_id,
				"❌ Gagal menghubungkan akun. Akun mungkin sudah terhubung sebelumnya."
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
