# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    # NOTE v19: `sinid` used to be a native hr.employee field (alongside
    # `ssnid`, which still is - now delegated from hr.version via
    # `_inherits`, see hr/models/hr_employee.py) - it was dropped from
    # core entirely during the hr.version/employee-versioning rewrite
    # (18.0), so this module now needs to (re)declare it itself instead of
    # just exposing an existing core field in the view, which is all the
    # pre-19.0 version of this module ever had to do.
    sinid = fields.Char(
        string="SIN No", help="Social Insurance Number", groups="hr.group_hr_user"
    )
