import frappe


def execute():
	"""Migrate NextHD Asset location to Link field and create default locations"""
	# 1. Buat record NextHD Location default jika belum ada
	default_locations = ["Pabrik CML", "Sena"]
	for loc_name in default_locations:
		if not frappe.db.exists("NextHD Location", loc_name):
			loc = frappe.get_doc({
				"doctype": "NextHD Location",
				"location_name": loc_name
			})
			loc.insert()
			frappe.db.commit()

	# 2. Migrasi data location di NextHD Asset
	assets = frappe.get_all("NextHD Asset", fields=["name", "location"])
	for asset in assets:
		if not asset.location:
			continue

		# Pangkas spasi di awal/akhir
		location_clean = asset.location.strip()

		# Normalisasi nilai
		if location_clean == "":
			# Kosong tetap kosong
			continue
		elif location_clean in ["Pabrik", "Pabrik CML"]:
			location_clean = "Pabrik CML"
		elif location_clean == "Sena":
			location_clean = "Sena"
		else:
			# Nilai tidak dikenal: log tapi jangan dihapus
			frappe.log_error(
				f"Asset {asset.name}: location '{asset.location}' tidak dikenal, dibiarkan apa adanya",
				"Asset Location Migration"
			)
			continue

		# Update menggunakan frappe.db.set_value
		if location_clean != asset.location:
			frappe.db.set_value("NextHD Asset", asset.name, "location", location_clean)
			frappe.db.commit()
