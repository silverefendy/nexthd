import frappe
from frappe.model.document import Document

UNIT_TO_MINUTES = {
    "Menit": 1,
    "Jam": 60,
    "Hari": 1440,
}


class NextHDSLAPolicy(Document):
    def validate(self):
        self.response_time_minutes = self.response_value * UNIT_TO_MINUTES.get(self.response_unit, 1)
        self.resolution_time_minutes = self.resolution_value * UNIT_TO_MINUTES.get(self.resolution_unit, 1)
