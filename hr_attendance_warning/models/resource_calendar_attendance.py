# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time
import pytz


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    margin_from = fields.Integer(string="Margin from", default=0)
    margin_to = fields.Integer(string="Margin to", default=0)
    next_check_from = fields.Datetime(default=False)
    next_check_to = fields.Datetime(default=False)

    def _compute_next_check_from(self):
        now = fields.Datetime.now()
        now = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(now)
        )
        real_dayofweek = now.weekday()
        diff = abs(int(self.dayofweek) - real_dayofweek)
        days = diff if int(self.dayofweek) > real_dayofweek else 7 - diff
        if not self.next_check_from and days == 7:
            days = 0
        now = now + timedelta(
            days=days,
            hours=-now.hour,
            minutes=-now.minute,
            seconds=-now.second,
        )
        datetime_tx = (now + timedelta(
            hours=self.hour_from,
            minutes=self.margin_from)).astimezone(pytz.utc)
        self.next_check_from = fields.Datetime.to_string(datetime_tx)

    def _compute_next_check_to(self):
        now = fields.Datetime.now()
        now = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(now)
        )
        real_dayofweek = now.weekday()
        diff = abs(int(self.dayofweek) - real_dayofweek)
        days = diff if int(self.dayofweek) > real_dayofweek else 7 - diff
        if not self.next_check_to and days == 7:
            days = 0
        now = now + timedelta(
            days=days,
            hours=-now.hour,
            minutes=-now.minute,
            seconds=-now.second,
        )
        datetime_tx = (now + timedelta(
            hours=self.hour_to,
            minutes=self.margin_to)).astimezone(pytz.utc)
        self.next_check_to = fields.Datetime.to_string(datetime_tx)

    @api.onchange('dayofweek', 'hour_from', 'margin_from')
    def _onchange_from(self):
        self.next_check_from = False
        if self.margin_from:
            self._compute_next_check_from()

    @api.onchange('dayofweek', 'hour_to', 'margin_to')
    def _onchange_to(self):
        self.next_check_to = False
        if self.margin_to:
            self._compute_next_check_to()

    @api.model
    def cron_attendance_checks(self):
        now = fields.Datetime.now()
        today = fields.Date.today()
        for attendance in self.search([
            ('margin_from', '>', 0),
            '|', ('date_from', '=', False), ('date_from', '<=', today),
            '|', ('date_to', '=', False), ('date_to', '>=', today),
            '|', ('next_check_from', '=', False), ('next_check_from', '<', now)
        ]):
            attendance._check_issue_start(today)
            attendance._compute_next_check_from()

        for attendance in self.search([
            ('margin_to', '>', 0),
            '|', ('date_from', '=', False), ('date_from', '<=', today),
            '|', ('date_to', '=', False), ('date_to', '>=', today),
            '|', ('next_check_to', '=', False), ('next_check_to', '<', now)
        ]):
            attendance._check_issue_end(today)
            attendance._compute_next_check_to()

    def _check_issue_start(self, date):
        date_t = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(date)
        )
        day_date = fields.Date.from_string(date)
        self.ensure_one()
        # If it's a different day there cannot be a warning.
        if day_date.weekday() != int(self.dayofweek):
            return
        # Special case, attendance until its next check is properly calculated
        if not self.next_check_from:
            return
        # Convention: If there is no margin we dont evaluate the interval
        if not self.margin_from:
            return
        for employee in self.calendar_id.employee_ids:
            intervals = self.calendar_id._get_day_work_intervals(
                day_date,
                start_time=float_to_time(self.hour_from),
                end_time=float_to_time(self.hour_to),
                compute_leaves=True,
                resource_id=employee.id
            )
            if len(intervals) != 0:
                min_check_in = fields.Datetime.to_string(
                    (date_t + timedelta(hours=self.hour_from,
                                        minutes=-self.margin_from)
                     ).astimezone(pytz.utc))
                max_check_in = fields.Datetime.to_string(
                    (date_t + timedelta(hours=self.hour_from,
                                        minutes=self.margin_from)
                     ).astimezone(pytz.utc))
                check_in = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', min_check_in),
                    ('check_in', '<=', max_check_in)
                ], order='check_in desc', limit=1)
                if not check_in:
                    employee._create_warning(
                        w_type='no_check_in',
                        min_int=min_check_in,
                        max_int=max_check_in,
                        date=date,
                    )
        return

    def _check_issue_end(self, date):
        date_t = fields.Datetime.context_timestamp(
            self, fields.Datetime.from_string(date)
        )
        day_date = fields.Date.from_string(date)
        self.ensure_one()
        # If it's a different day there cannot be a warning.
        if day_date.weekday() != int(self.dayofweek):
            return
        # Special case, attendance until its next check is properly calculated
        if not self.next_check_to:
            return
        # Convention: If there is no margin we don't evaluate the interval
        if not self.margin_to:
            return
        for employee in self.calendar_id.employee_ids:
            intervals = self.calendar_id._get_day_work_intervals(
                day_date,
                start_time=float_to_time(self.hour_from),
                end_time=float_to_time(self.hour_to),
                compute_leaves=True,
                resource_id=employee.id
            )
            if len(intervals) != 0:
                min_check_out = fields.Datetime.to_string(
                    (date_t + timedelta(hours=self.hour_to,
                                        minutes=-self.margin_to)
                     ).astimezone(pytz.utc))
                max_check_out = fields.Datetime.to_string(
                    (date_t + timedelta(hours=self.hour_to,
                                        minutes=self.margin_to)
                     ).astimezone(pytz.utc))
                check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_in', '>=', min_check_out),
                    ('check_in', '<=', max_check_out)
                ], order='check_in desc', limit=1)
                if not check_out:
                    employee._create_warning(
                        w_type='no_check_out',
                        min_int=min_check_out,
                        max_int=max_check_out,
                        date=date,
                    )
        return
