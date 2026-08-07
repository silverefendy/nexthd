import frappe
from frappe.tests.utils import FrappeTestCase


class TestNextHDTeam(FrappeTestCase):
	def setUp(self):
		super().setUp()
		# Create a test user
		if not frappe.db.exists("User", "test_user@example.com"):
			self.test_user = frappe.get_doc({
				"doctype": "User",
				"email": "test_user@example.com",
				"first_name": "Test",
				"last_name": "User",
				"username": "testuser"
			})
			self.test_user.insert()
		else:
			self.test_user = frappe.get_doc("User", "test_user@example.com")

	def tearDown(self):
		super().tearDown()
		# Clean up
		frappe.db.delete("NextHD Team", {"team_name": ["like", "%Test%"]})

	def test_create_team(self):
		"""Test creating a team"""
		team = frappe.get_doc({
			"doctype": "NextHD Team",
			"team_name": "Test Team"
		})
		team.insert()
		self.assertEqual(team.team_name, "Test Team")

	def test_team_with_member(self):
		"""Test creating a team with members"""
		team = frappe.get_doc({
			"doctype": "NextHD Team",
			"team_name": "Test Team with Members"
		})
		team.append("members", {
			"user": self.test_user.name
		})
		team.insert()
		self.assertEqual(len(team.members), 1)
		self.assertEqual(team.members[0].user, self.test_user.name)

	def test_unique_team_name(self):
		"""Test that team names must be unique"""
		team1 = frappe.get_doc({
			"doctype": "NextHD Team",
			"team_name": "Unique Team"
		})
		team1.insert()

		team2 = frappe.get_doc({
			"doctype": "NextHD Team",
			"team_name": "Unique Team"
		})
		with self.assertRaises(frappe.UniqueValidationError):
			team2.insert()
