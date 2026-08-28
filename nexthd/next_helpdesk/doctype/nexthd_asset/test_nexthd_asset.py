import frappe
from frappe.tests.utils import FrappeTestCase
from datetime import date, timedelta


class TestNextHDAsset(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test user
		if not frappe.db.exists("User", "test_asset_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_asset_user@example.com",
				"first_name": "Test",
				"last_name": "Asset User",
				"username": "testassetuser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_asset_user@example.com")

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Asset", {"asset_name": ["like", "%Test%"]})
		frappe.db.delete("NextHD Asset Category", {"category_name": ["like", "%Test%"]})
		frappe.set_user("Administrator")

	def test_create_asset(self):
		"""Test creating a basic asset"""
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Laptop",
			"asset_type": "Laptop",
			"status": "Aktif"
		})
		asset.insert()
		self.assertEqual(asset.asset_name, "Test Laptop")
		self.assertEqual(asset.asset_type, "Laptop")
		self.assertTrue(asset.name.startswith("AST-2026-"))

	def test_asset_with_assignment(self):
		"""Test creating an asset assigned to a user"""
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Assigned Laptop",
			"asset_type": "Laptop",
			"status": "Aktif",
			"assigned_to": self.test_user.name,
			"location": "Office A"
		})
		asset.insert()
		self.assertEqual(asset.assigned_to, self.test_user.name)
		self.assertEqual(asset.location, "Office A")

	def test_asset_with_warranty(self):
		"""Test creating an asset with warranty dates"""
		purchase_date = date.today()
		warranty_until = purchase_date + timedelta(days=365)
		
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Warranty Laptop",
			"asset_type": "Laptop",
			"status": "Aktif",
			"purchase_date": purchase_date,
			"warranty_until": warranty_until
		})
		asset.insert()
		self.assertEqual(asset.purchase_date, purchase_date)
		self.assertEqual(asset.warranty_until, warranty_until)

	def test_invalid_warranty_dates(self):
		"""Test that invalid warranty dates raise error"""
		purchase_date = date.today()
		warranty_until = purchase_date - timedelta(days=365)  # Invalid: before purchase
		
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Invalid Warranty",
			"asset_type": "Laptop",
			"status": "Aktif",
			"purchase_date": purchase_date,
			"warranty_until": warranty_until
		})
		with self.assertRaises(frappe.ValidationError):
			asset.insert()

	def test_asset_status_options(self):
		"""Test different asset status options"""
		statuses = ["Aktif", "Rusak", "Diperbaiki", "Dihapus"]
		for status in statuses:
			asset = frappe.get_doc({
				"doctype": "NextHD Asset",
				"asset_name": f"Test {status} Asset",
				"asset_type": "PC",
				"status": status
			})
			asset.insert()
			self.assertEqual(asset.status, status)

	def test_asset_type_options(self):
		"""Test different asset type options"""
		asset_types = ["Laptop", "PC", "Server", "Network Device", "Printer", "Lainnya"]
		for asset_type in asset_types:
			asset = frappe.get_doc({
				"doctype": "NextHD Asset",
				"asset_name": f"Test {asset_type}",
				"asset_type": asset_type,
				"status": "Aktif"
			})
			asset.insert()
			self.assertEqual(asset.asset_type, asset_type)

	# EAV Test Cases - Session A

	def test_create_asset_category_unique(self):
		"""Test creating NextHD Asset Category with unique constraint"""
		# Create first category
		category1 = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Laptop Category",
			"description": "Test description"
		})
		category1.insert()
		self.assertEqual(category1.category_name, "Test Laptop Category")

		# Try to create duplicate - should fail
		category2 = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Laptop Category",
			"description": "Another description"
		})
		with self.assertRaises(frappe.UniqueValidationError):
			category2.insert()

	def test_asset_category_required_field(self):
		"""Test that asset_category field is required (reqd=1)"""
		# First create a category to link to
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test PC Category"
		})
		category.insert()

		# Try to create asset without asset_category - should fail with MandatoryError
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test PC Without Category",
			"asset_type": "PC",
			"status": "Aktif"
			# Missing asset_category
		})
		with self.assertRaises(frappe.MandatoryError):
			asset.insert()

	def test_asset_with_category(self):
		"""Test creating asset with asset_category filled"""
		# Create a category
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Server Category"
		})
		category.insert()

		# Create asset with category
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Server With Category",
			"asset_type": "Server",
			"status": "Aktif",
			"asset_category": category.name
		})
		asset.insert()
		self.assertEqual(asset.asset_category, category.name)

	def test_asset_attributes_child_table(self):
		"""Test inserting multiple rows to asset_attributes child table"""
		# Create a category first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Monitor Category"
		})
		category.insert()

		# Create asset with attributes
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Monitor With Attributes",
			"asset_type": "Lainnya",
			"status": "Aktif",
			"asset_category": category.name
		})

		# Add multiple attribute rows
		asset.append("asset_attributes", {
			"attribute_name": "Panel Type",
			"attribute_value": "IPS",
			"unit": ""
		})
		asset.append("asset_attributes", {
			"attribute_name": "Refresh Rate",
			"attribute_value": "144",
			"unit": "Hz"
		})
		asset.append("asset_attributes", {
			"attribute_name": "Power Consumption",
			"attribute_value": "45",
			"unit": "W"
		})

		asset.insert()

		# Verify attributes were saved
		self.assertEqual(len(asset.asset_attributes), 3)
		self.assertEqual(asset.asset_attributes[0].attribute_name, "Panel Type")
		self.assertEqual(asset.asset_attributes[0].attribute_value, "IPS")
		self.assertEqual(asset.asset_attributes[1].unit, "Hz")
		self.assertEqual(asset.asset_attributes[2].attribute_value, "45")

	def test_asset_category_permission_agent_read_only(self):
		"""Test that Agent role can read but not create/write/delete NextHD Asset Category"""
		# Create a test user with Agent role
		if not frappe.db.exists("User", "test_agent@example.com"):
			agent_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_agent@example.com",
				"first_name": "Test",
				"last_name": "Agent",
				"username": "testagent"
			})
			agent_user.insert()
			# Add Agent role (in real scenario this would be done via UI)
			agent_user.add_roles("Agent")
		else:
			agent_user = frappe.get_doc("User", "test_agent@example.com")

		# Create a category as Administrator first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Permission Category"
		})
		category.insert()

		# Switch to Agent role context
		frappe.set_user("test_agent@example.com")

		# Agent should be able to read
		read_category = frappe.get_doc("NextHD Asset Category", category.name)
		self.assertEqual(read_category.category_name, "Test Permission Category")

		# Agent should NOT be able to create
		new_category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Agent Should Not Create"
		})
		with self.assertRaises(frappe.PermissionError):
			new_category.insert()

		# Agent should NOT be able to write
		read_category.description = "Agent modified this"
		with self.assertRaises(frappe.PermissionError):
			read_category.save()

		# Agent should NOT be able to delete
		with self.assertRaises(frappe.PermissionError):
			read_category.delete()

		# Switch back to Administrator
		frappe.set_user("Administrator")

	def test_regression_old_fields_still_work(self):
		"""Regression test: old fields (cpu, brand, etc.) should still work"""
		# Create a category first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test PC Old Fields"
		})
		category.insert()

		# Create asset with old fields still populated
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test PC Old Fields",
			"asset_type": "PC",
			"status": "Aktif",
			"asset_category": category.name,
			"brand": "Dell",
			"model": "OptiPlex 7090",
			"serial_number": "SN123456",
			"cpu": "Intel Core i7-11700",
			"ram": "32GB DDR4",
			"storage": "1TB NVMe SSD",
			"os": "Windows 11",
			"peripheral_notes": "Monitor 27inch, Keyboard, Mouse"
		})

		asset.insert()

		# Verify all old fields are still accessible
		self.assertEqual(asset.brand, "Dell")
		self.assertEqual(asset.model, "OptiPlex 7090")
		self.assertEqual(asset.serial_number, "SN123456")
		self.assertEqual(asset.cpu, "Intel Core i7-11700")
		self.assertEqual(asset.ram, "32GB DDR4")
		self.assertEqual(asset.storage, "1TB NVMe SSD")
		self.assertEqual(asset.os, "Windows 11")
		self.assertEqual(asset.peripheral_notes, "Monitor 27inch, Keyboard, Mouse")

	# EAV Test Cases - Session B

	def test_asset_attribute_optional_fields(self):
		"""Test inserting Asset Attribute with only attribute_name and attribute_value (new fields optional)"""
		# Create a category first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Optional Fields Category"
		})
		category.insert()

		# Create asset with attribute row WITHOUT new optional fields
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Asset Optional Fields",
			"asset_type": "Lainnya",
			"status": "Aktif",
			"asset_category": category.name
		})

		# Add attribute row with only required fields (attribute_name, attribute_value)
		asset.append("asset_attributes", {
			"attribute_name": "Resolution",
			"attribute_value": "1920x1080"
			# brand, serial_number, sumber, catatan NOT filled - should still work
		})

		asset.insert()

		# Verify attribute was saved successfully
		self.assertEqual(len(asset.asset_attributes), 1)
		self.assertEqual(asset.asset_attributes[0].attribute_name, "Resolution")
		self.assertEqual(asset.asset_attributes[0].attribute_value, "1920x1080")
		# New fields should be empty/None
		self.assertEqual(asset.asset_attributes[0].brand, "")
		self.assertEqual(asset.asset_attributes[0].serial_number, "")
		self.assertEqual(asset.asset_attributes[0].sumber, "")
		self.assertEqual(asset.asset_attributes[0].catatan, "")

	def test_asset_attribute_all_fields_filled(self):
		"""Test inserting Asset Attribute with ALL fields filled (including new brand/serial_number/sumber/catatan)"""
		# Create a category first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test All Fields Category"
		})
		category.insert()

		# Create asset with attribute row with ALL fields filled
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Asset All Fields",
			"asset_type": "Lainnya",
			"status": "Aktif",
			"asset_category": category.name
		})

		# Add attribute row with all fields filled
		asset.append("asset_attributes", {
			"attribute_name": "RAM",
			"attribute_value": "32GB",
			"unit": "GB",
			"brand": "Kingston",
			"serial_number": "KVR32E16S8-8",
			"sumber": "PO-2026-001",
			"catatan": "Upgrade from 16GB, purchased separately"
		})

		asset.insert()

		# Verify all fields were saved correctly
		self.assertEqual(len(asset.asset_attributes), 1)
		self.assertEqual(asset.asset_attributes[0].attribute_name, "RAM")
		self.assertEqual(asset.asset_attributes[0].attribute_value, "32GB")
		self.assertEqual(asset.asset_attributes[0].unit, "GB")
		self.assertEqual(asset.asset_attributes[0].brand, "Kingston")
		self.assertEqual(asset.asset_attributes[0].serial_number, "KVR32E16S8-8")
		self.assertEqual(asset.asset_attributes[0].sumber, "PO-2026-001")
		self.assertEqual(asset.asset_attributes[0].catatan, "Upgrade from 16GB, purchased separately")

	def test_regression_existing_asset_attribute_data(self):
		"""Regression test: existing asset AST-2608-0001 should not be affected by new fields"""
		# Check if the existing asset exists (migrated manually in Session A)
		if frappe.db.exists("NextHD Asset", "AST-2608-0001"):
			existing_asset = frappe.get_doc("NextHD Asset", "AST-2608-0001")
			
			# Verify the asset still exists and has its attributes
			self.assertIsNotNone(existing_asset.name)
			self.assertEqual(existing_asset.name, "AST-2608-0001")
			
			# Verify asset_attributes child table still has data
			# (This record should have 5 attribute rows from manual migration)
			self.assertGreaterEqual(len(existing_asset.asset_attributes), 1)
			
			# Verify original fields (attribute_name, attribute_value, unit) still work
			first_attr = existing_asset.asset_attributes[0]
			self.assertIsNotNone(first_attr.attribute_name)
			self.assertIsNotNone(first_attr.attribute_value)
			# New fields should be empty for existing data (not migrated)
			self.assertEqual(first_attr.brand, "")
			self.assertEqual(first_attr.serial_number, "")
			self.assertEqual(first_attr.sumber, "")
			self.assertEqual(first_attr.catatan, "")

	def test_peripheral_notes_label_change(self):
		"""Test that peripheral_notes label changed to 'Remarks / Catatan' but field still works"""
		# Create a category first
		category = frappe.get_doc({
			"doctype": "NextHD Asset Category",
			"category_name": "Test Label Change Category"
		})
		category.insert()

		# Create asset with peripheral_notes filled
		asset = frappe.get_doc({
			"doctype": "NextHD Asset",
			"asset_name": "Test Label Change Asset",
			"asset_type": "PC",
			"status": "Aktif",
			"asset_category": category.name,
			"peripheral_notes": "Monitor 24inch, Keyboard, Mouse, UPS"
		})

		asset.insert()

		# Verify field still works (fieldname unchanged, only label changed)
		self.assertEqual(asset.peripheral_notes, "Monitor 24inch, Keyboard, Mouse, UPS")
		
		# Verify fieldname is still "peripheral_notes" (not changed)
		self.assertEqual(asset.meta.get_field("peripheral_notes").fieldname, "peripheral_notes")
		
		# Verify label is "Remarks / Catatan" (changed from "Peripheral / Catatan")
		self.assertEqual(asset.meta.get_field("peripheral_notes").label, "Remarks / Catatan")

