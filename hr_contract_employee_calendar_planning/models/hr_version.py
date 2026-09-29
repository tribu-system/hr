from odoo import api, models


class HrVersion(models.Model):
    # NOTE v19: hr.contract was removed from core entirely in the
    # hr.version employee-versioning rewrite (18.0/19.0) - hr.version is
    # its replacement (contract_date_start/contract_date_end/wage/
    # resource_calendar_id/etc. live there now, delegated onto
    # hr.employee via `_inherits`). This override used to target
    # hr.contract; the conflict it works around still exists in the same
    # shape on hr.version (see `_inverse_resource_calendar_id` in
    # odoo/addons/hr/models/hr_version.py, which does the exact same
    # `employee.resource_id.calendar_id = version.resource_calendar_id`
    # clobbering that this module patches around), so the fix is the same
    # one, just re-targeted.
    _inherit = "hr.version"

    def write(self, vals):
        if (
            vals.get("resource_calendar_id")
            and self.employee_id
            and vals.get("resource_calendar_id")
            != self.employee_id.resource_calendar_id.id
        ):
            # in the write method of hr.version, when writing the
            # resource_calendar_id the employee resource_calendar_id is
            # set to the same id (see hr.version._inverse_resource_calendar_id)
            # this interferes with the logic of hr_employee_calendar_planning,
            # which assumes that calendar times are managed by
            # resource.calendar.attendances in auto-generated calendars
            # based on the employee's calendar_ids.
            # since the default calendar for new versions is the employee calendar,
            # and we set the correct calendar for the existing version
            # in the post_init_hook, we resolve this conflict by not allowing
            # calendar changes in versions.
            vals.pop("resource_calendar_id")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        # the create method of hr.version syncs version
        # calendars with employee calendars
        # in order to not overwrite the employee calendar
        # we set the version calendar to match the employee calendar
        for vals in vals_list:
            employee_version = (
                self.env["hr.employee"]
                .browse([vals.get("employee_id")])
                .resource_calendar_id
            )
            if employee_version:
                vals.update({"resource_calendar_id": employee_version.id})
        return super().create(vals_list)
