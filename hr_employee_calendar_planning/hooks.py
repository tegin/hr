# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID
from collections import defaultdict


def post_init_hook(cr, registry, employees=None):
    """Split current calendars by date ranges and assign new ones for
    having proper initial data.
    """
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        if not employees:
            employees = env['hr.employee'].search([(
                'resource_calendar_id', '!=', False,
            )])
        for employee in employees:
            calendar_lines = [(0, 0, {
                'date_start': False,
                'date_end': False,
                'calendar_id': employee.resource_calendar_id.id,
            })]
            employee.resource_calendar_id = False
            employee.calendar_ids = calendar_lines
