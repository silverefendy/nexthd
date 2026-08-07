import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDCategory(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Clean up before each test
		frappe.db.delete("NextHD Category", {"category_name": "Test Category"})

	def test_create_category(self):
		"""Test creating a simple category"""
		category = frappe.get_doc({
			"doctype": "NextHD Category",
			"category_name": "Test Category"
		})
		category.insert()
		self.assertEqual(category.category_name, "Test Category")

	def test_category_with_parent(self):
		"""Test creating a category with parent"""
		parent = frappe.get_doc({
			"doctype": "NextHD Category",
			"category_name": "Parent Category"
		})
		parent.insert()

		child = frappe.get_doc({
			"doctype": "NextHD Category",
			"category_name": "Child Category",
			"parent_category": "Parent Category"
		})
		child.insert()
		self.assertEqual(child.parent_category, "Parent Category")

	def test_unique_category_name(self):
		"""Test that category names must be unique"""
		category1 = frappe.get_doc({
			"doctype": "NextHD Category",
			"category_name": "Unique Category"
		})
		category1.insert()

		category2 = frappe.get_doc({
			"doctype": "NextHD Category",
			"category_name": "Unique Category"
		})
		with self.assertRaises(frappe.UniqueValidationError):
			category2.insert()

	def tearDown(self):
		super().tearDown()
		# Clean up after each test
		frappe.db.delete("NextHD Category", {"category_name": ["like", "%Test%"]})
		frappe.db.delete("NextHD Category", {"category_name": ["like", "%Parent%"]})
		frappe.db.delete("NextHD Category", {"category_name": ["like", "%Child%"]})
		frappe.db.delete("NextHD Category", {"category_name": ["like", "%Unique%"]})
