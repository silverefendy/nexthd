import frappe
from frappe import _
from frappe.model.document import Document
DIRECTIONAL = ("Berjalan di", "Bergantung pada", "Bagian dari")
class NextHDAssetRelationship(Document):
    def validate(self):
        self.check_self_relation()
        self.check_duplicate()
        if self.relation_type in DIRECTIONAL:
            self.check_cycle()
    def check_self_relation(self):
        if self.source_asset == self.target_asset:
            frappe.throw(_("Aset tidak boleh berelasi dengan dirinya sendiri."))
    def check_duplicate(self):
        f = {"source_asset": self.source_asset, "target_asset": self.target_asset, "relation_type": self.relation_type, "name": ["!=", self.name]}
        exists = frappe.db.exists("NextHD Asset Relationship", f)
        if exists:
            frappe.throw(_("Relasi yang sama sudah ada: {0}").format(exists))
    def check_cycle(self):
        visited = set()
        stack = [self.target_asset]
        while stack:
            current = stack.pop()
            if current == self.source_asset:
                frappe.throw(_("Relasi ini membentuk siklus (A ke B ... ke A)."))
            if current in visited:
                continue
            visited.add(current)
            f = {"source_asset": current, "relation_type": ["in", list(DIRECTIONAL)], "name": ["!=", self.name]}
            stack.extend(frappe.get_all("NextHD Asset Relationship", filters=f, pluck="target_asset"))
