# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
                ) + ' %s' % self.id,
            }).id
        else:
            self.resource_calendar_id.attendance_ids.unlink()
        vals_list = []
        for line in self.calendar_ids:
            for calendar_line in line.calendar_id.attendance_ids:
                vals_list.append((0, 0, {
                    'name': calendar_line.name,
                    'dayofweek': calendar_line.dayofweek,
                    'hour_from': calendar_line.hour_from,
                    'hour_to': calendar_line.hour_to,
                    'date_from': line.date_start,
                    'date_to': line.date_end,
                }))
        self.resource_calendar_id.attendance_ids = vals_list


class HrEmployeeCalendar(models.Model):
    _name = 'hr.employee.calendar'

    date_start = fields.Date(
        string="Start",
    )
    date_end = fields.Date(
        string="End",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
    )
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,

    )

    _sql_constraints = [
        ('date_consistency',
         'CHECK(date_start <= date_end)',
         'Date end should be higher than date start'),
    ]

    def create(self, vals):
        record = super(HrEmployeeCalendar, self).create(vals)
        record.employee_id._regenerate_calendar()
        return record

    def write(self, vals):
        res = super(HrEmployeeCalendar, self).write(vals)
        for employee in self.mapped('employee_id'):
            employee._regenerate_calendar()
        return res

    @api.constrains('employee_id', 'date_start', 'date_end')
    def _constrain_overlap(self):
        for record in self:
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id),
            ]
            if record.date_end and record.date_start:
                domain += [
                    '|', '|', '|', '|', '|',
                    '&', ('date_start', '<=', record.date_start),
                    ('date_end', '>=', record.date_start),
                    '&', ('date_start', '<=', record.date_start),
                    ('date_end', '=', False),
                    '&', ('date_start', '<=', record.date_end),
                    ('date_end', '>=', record.date_end),
                    '&', ('date_start', '=', False),
                    ('date_end', '>=', record.date_end),
                    '&', ('date_start', '<=', record.date_end),
                    ('date_end', '=', False),
                    '&', ('date_start', '=', False),
                    ('date_end', '=', False),
                ]
            elif record.date_end:
                domain += [
                    '|', ('date_start', '=', False),
                    ('date_start', '<=', record.date_end)
                ]
            elif record.date_start:
                domain += [
                    '|', ('date_end', '=', False),
                    ('date_end', '>=', record.date_start)
                ]
            if self.search(domain, limit=1):
                    raise ValidationError(
                        _('There cannot exist any overlaps in the '
                          'calendar planning.'))
