# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tools import mute_logger

from odoo.addons.hr_employee_calendar_planning.tests import (
    test_hr_employee_calendar_planning,
)

from ..hooks import post_init_hook


class TestHrContractEmployeeCalendarPlanning(
    test_hr_employee_calendar_planning.TestHrEmployeeCalendarPlanning
):
    @mute_logger("odoo.models.unlink")
    def test_write_conflicting_calendar_dropped(self):
        """Writing a resource_calendar_id on hr.version that differs from
        the employee's calendar must be silently dropped - hr.version's
        own `_inverse_resource_calendar_id` would otherwise clobber the
        employee's calendar_ids-managed schedule (core hr behavior, same
        conflict this module used to patch on hr.contract)."""
        old_calendar = self.employee.resource_calendar_id
        self.assertNotEqual(old_calendar, self.calendar2)

        self.employee.version_id.write({"resource_calendar_id": self.calendar2.id})

        self.assertEqual(self.employee.resource_calendar_id, old_calendar)
        self.assertEqual(self.employee.version_id.resource_calendar_id, old_calendar)

    def test_write_matching_calendar_not_dropped(self):
        """Writing the SAME calendar the employee already has is a no-op
        either way, so it isn't blocked - nothing conflicts."""
        calendar = self.employee.resource_calendar_id
        # should not raise / should just go through
        self.employee.version_id.write({"resource_calendar_id": calendar.id})
        self.assertEqual(self.employee.resource_calendar_id, calendar)

    def test_create_new_version_syncs_to_employee_calendar(self):
        """A new hr.version's resource_calendar_id is forced to match the
        employee's current calendar at creation time, regardless of what
        was passed in - mirrors the pre-19.0 behavior on hr.contract."""
        employee_calendar = self.employee.resource_calendar_id
        self.assertNotEqual(employee_calendar, self.calendar2)

        new_version = self.env["hr.version"].create(
            {
                "employee_id": self.employee.id,
                "date_version": "2030-01-01",
                "resource_calendar_id": self.calendar2.id,
            }
        )
        self.assertEqual(new_version.resource_calendar_id, employee_calendar)

    @mute_logger("odoo.models.unlink")
    def test_post_init_hook_migrates_version_calendars(self):
        """Historical hr.version calendars that differ from the employee's
        current one get reflected as calendar_ids lines by the
        post_init_hook (equivalent of the old hr.contract migration)."""
        self.employee.calendar_ids = [(5, 0, 0)]
        version = self.env["hr.version"].create(
            {
                "employee_id": self.employee.id,
                "date_version": "2018-11-30",
                "contract_date_start": "2018-11-30",
                "contract_date_end": "2019-11-30",
            }
        )
        # bypass the create() override to force a genuinely different,
        # pre-existing-looking calendar mismatch for the hook to migrate
        self.env.cr.execute(
            "UPDATE hr_version SET resource_calendar_id = %s WHERE id = %s",
            (self.calendar1.id, version.id),
        )
        version.invalidate_recordset(["resource_calendar_id"])
        self.assertNotEqual(version.resource_calendar_id, self.employee.resource_calendar_id)

        post_init_hook(self.env)

        migrated = self.employee.calendar_ids.filtered(
            lambda x: x.calendar_id == self.calendar1
        )
        self.assertTrue(migrated)
