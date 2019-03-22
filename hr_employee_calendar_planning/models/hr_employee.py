# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
    )

    def _regenerate_calendar(self):
        self.ensure_one()
        if not self.resource_calendar_id or self.resource_calendar_id.active:
            self.resource_calendar_id = self.env['resource.calendar'].create({
                'active': False,
                'name': _(
                    'Auto generated calendar for employee'
                ) + ' %s' % self.name,
            }).id
        else:
            self.resource_calendar_id.attendance_ids.unlink()
        vals_list = []
        for line in self.calendar_ids:
            for attendance_line in line.calendar_id.attendance_ids:
                data = attendance_line.copy_data({
                    'calendar_id': self.resource_calendar_id.id,
                    'date_from': line.date_start,
                    'date_to': line.date_end,
                })[0]
                vals_list.append((0, 0, data))
        self.resource_calendar_id.attendance_ids = vals_list
