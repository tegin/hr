# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import timedelta


class HrAttendance(models.Model):
    _name = 'hr.attendance'
    _inherit = ['hr.attendance', 'mail.thread']

    employee_id = fields.Many2one(
        track_visibility='onchange'
    )
    check_in = fields.Datetime(
        track_visibility='onchange'
    )
    check_out = fields.Datetime(
        track_visibility='onchange'
    )
    time_changed_manually = fields.Boolean(
        string="Time changed",
        readonly=True,
        compute='_compute_time_changed_manually',
        store=True,
    )

    @api.one
    @api.depends('message_ids.tracking_value_ids')
    def _compute_time_changed_manually(self):
        if not self.time_changed_manually:
            for tracking in self.message_ids.mapped('tracking_value_ids'):
                for field in ['check_in', 'check_out']:
                    if tracking.field == field:
                        d1 = tracking.value_datetime
                        d2 = tracking.message_id.date
                        if (
                            not d1
                            or d1 < d2 - timedelta(seconds=60)
                            or d1 > d2 + timedelta(seconds=60)
                        ):
                            self.time_changed_manually = True
