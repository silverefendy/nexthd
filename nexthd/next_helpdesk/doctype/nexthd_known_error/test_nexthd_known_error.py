import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDKnownError(FrappeTestCase):
	def setUp(self):
		super().setUp()

	def tearDown(self):
		super().tearDown()
		frappe.db.delete("NextHD Known Error", {"title": ["like", "%Test%"]})

	def test_create_known_error(self):
		"""Test creating a basic known error"""
		ke = frappe.get_doc({
			"doctype": "NextHD Known Error",
			"title": "Test Known Error"
		})
		ke.insert()
		self.assertEqual(ke.title, "Test Known Error")
		self.assertTrue(ke.name.startswith("KE-2026-"))

	def test_known_error_with_symptom_and_workaround(self):
		"""Test creating a known error with symptom and workaround"""
		ke = frappe.get_doc({
			"doctype": "NextHD Known Error",
			"title": "Test Known Error with Details",
			"symptom": "System crashes when opening large files",
			"workaround": "Reduce file size before opening or use alternative viewer"
		})
		ke.insert()
		self.assertEqual(ke.symptom, "System crashes when opening large files")
		self.assertEqual(ke.workaround, "Reduce file size before opening or use alternative viewer")

	def test_known_error_with_related_problem(self):
		"""Test creating a known error linked to a problem"""
		# Create a test problem first
		problem = frappe.get_doc({
			"doctype": "NextHD Problem",
			"title": "Test Related Problem",
			"status": "Selesai"
		})
		problem.insert()

		# Create known error linked to problem
		ke = frappe.get_doc({
			"doctype": "NextHD Known Error",
			"title": "Test Known Error with Problem",
			"related_problem": problem.name
		})
		ke.insert()
		self.assertEqual(ke.related_problem, problem.name)
