# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
