# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Hr Contract Employee Calendar Planning",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "cibex,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "auto_install": True,
    # hr_contract no longer exists (merged into hr.version, part of core
    # hr) - see models/hr_version.py.
    "depends": ["hr", "hr_employee_calendar_planning"],
    "data": ["views/hr_version.xml"],
    "post_init_hook": "post_init_hook",
}
