import frappe


def execute():
	"""Create custom roles for NextHD"""
	roles = [
		{
			"role_name": "IT Manager",
			"description": "IT Manager role with full access to NextHD",
			"desk_access": 1
		},
		{
			"role_name": "IT Auditor",
			"description": "IT Auditor role with read-only access to NextHD",
			"desk_access": 1
		}
	]

	for role_data in roles:
		if not frappe.db.exists("Role", role_data["role_name"]):
			role = frappe.get_doc("Role", role_data)
			role.insert()
			frappe.db.commit()
