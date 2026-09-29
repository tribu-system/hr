# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestHrEmployeeSsn(TransactionCase):
    def test_sinid_field_read_write(self):
        """`sinid` was dropped from core hr.employee in the 18.0
        hr.version rewrite - this module has to (re)provide it, unlike its
        pre-19.0 version which only had to expose an existing core field.
        """
        employee = self.env["hr.employee"].create(
            {"name": "Test Employee", "sinid": "123-456-789"}
        )
        self.assertEqual(employee.sinid, "123-456-789")

        employee.sinid = "987-654-321"
        self.assertEqual(employee.sinid, "987-654-321")

    def test_ssnid_still_available_alongside_sinid(self):
        """`ssnid` (the sibling field this module's view sits next to) is
        still reachable on hr.employee, now via `_inherits` delegation to
        hr.version rather than as a native field - confirms the view's
        `position="after" ref` anchor is still valid in 19.0.
        """
        employee = self.env["hr.employee"].create(
            {"name": "Test Employee", "ssnid": "111-22-3333", "sinid": "SIN-001"}
        )
        self.assertEqual(employee.ssnid, "111-22-3333")
        self.assertEqual(employee.sinid, "SIN-001")
