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
