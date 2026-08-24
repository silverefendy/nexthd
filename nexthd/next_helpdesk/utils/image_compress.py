import frappe
import os
from PIL import Image

MAX_DIMENSION = 1600
JPEG_QUALITY = 72


def compress_photo_on_upload(doc, method=None):
	"""Hook: File.after_insert — kompres file kalau file ini attached ke field
	'image' milik DocType NextHD Photo"""
	if doc.attached_to_doctype != "NextHD Photo":
		return
	if doc.attached_to_field != "image":
		return
	if not doc.file_url:
		return

	file_path = doc.get_full_path()
	if not os.path.exists(file_path):
		return

	try:
		img = Image.open(file_path)
		original_format = img.format

		# Resize kalau sisi terpanjang melebihi MAX_DIMENSION
		width, height = img.size
		if max(width, height) > MAX_DIMENSION:
			ratio = MAX_DIMENSION / float(max(width, height))
			new_size = (int(width * ratio), int(height * ratio))
			img = img.resize(new_size, Image.LANCZOS)

		# Convert ke RGB kalau mau disimpan sebagai JPEG (buang alpha channel)
		save_format = original_format
		if original_format not in ("PNG",):
			save_format = "JPEG"
			if img.mode in ("RGBA", "P"):
				img = img.convert("RGB")

		if save_format == "JPEG":
			img.save(file_path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
		else:
			img.save(file_path, format=save_format, optimize=True)

		# Update file_size di DocType File supaya konsisten dengan ukuran baru
		new_size = os.path.getsize(file_path)
		frappe.db.set_value("File", doc.name, "file_size", new_size)

	except Exception:
		frappe.log_error(
			title="Gagal kompres foto NextHD Photo",
			message=frappe.get_traceback()
		)
