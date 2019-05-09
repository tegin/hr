# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrAttendanceWarning(models.Model):

    _name = 'hr.attendance.warning'
    _description = 'Hr Attendance Warning'
    _inherit = 'mail.thread'
    _order = 'state, create_date desc'

    name = fields.Char(
        default='/',
        required=True,
        readonly=True
    )
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=False,
        readonly=False, ondelete='cascade')

    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('solved', 'Solved'),
        ], string='State',
        required=True, readonly=True,
        default='pending', track_visibility="onchange"
    )

    solved_by = fields.Many2one(
        'res.users', string='Solved by',
        readonly=True)
    solved_on = fields.Datetime(string='Solved on', readonly=True)

    solver_comment = fields.Text(
        string='Comments',
        readonly=True,
        states={'pending': [('readonly', False)]},
    )

    warning_line_ids = fields.One2many(
        'hr.attendance.warning.line',
        inverse_name='warning_id',
        readonly=False,
    )

    day_date = fields.Date(
        string='Created on',
        compute='_compute_day_date', readonly=True)

    @api.depends('create_date')
    def _compute_day_date(self):
        for record in self:
            date_t = fields.Datetime.from_string(record.create_date)
            record.day_date = fields.Date.to_string(date_t)

    @api.model
    def get_name(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'hr.attendance.warning') or '/'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals.update({'name': self.get_name(vals)})
        return super(HrAttendanceWarning, self).create(vals)

    def _pending2solved_values(self):
        return {
            'state': 'solved',
            'solved_on': fields.Datetime.now(),
            'solved_by': self.env.user.id,
        }

    @api.multi
    def pending2solved(self):
        for record in self:
            record.write(record._pending2solved_values())
            for line in record.warning_line_ids:
                line.write({'state': 'solved'})

    def _solved2pending_values(self):
        return {
            'state': 'pending',
            'solved_on': False,
            'solved_by': False,
        }

    @api.multi
    def solved2pending(self):
        for record in self:
            record.write(record._solved2pending_values())
            for line in record.warning_line_ids:
                line.write({'state': 'pending'})


class HrAttendanceWarningLine(models.Model):

    _name = 'hr.attendance.warning.line'

    warning_id = fields.Many2one('hr.attendance.warning', readonly=True)
    employee_id = fields.Many2one('hr.employee',
                                  related='warning_id.employee_id')
    state = fields.Selection(
        [
            ('pending', 'Pending'),
            ('solved', 'Solved'),
        ], readonly=True,
        default='pending'
    )

    min_int = fields.Datetime(default=False, readonly=True)
    max_int = fields.Datetime(default=False, readonly=True)

    warning_type = fields.Selection(
        selection=[('no_check_in', 'Didn\'t check in'),
                   ('no_check_out', 'Didn\'t check out'),
                   ('out_of_interval', 'Out of working hours'),
                   ('no_hours', 'Not enough hours'),
                   ],
        string='Type', readonly=False, required=False,
    )

    message = fields.Char(
        string='Message',
        compute='_compute_message',
        readonly=True,
    )

    @api.depends('warning_type', 'warning_id', 'min_int', 'max_int')
    def _compute_message(self):
        for warning in self:
            if warning.warning_type == 'no_check_in':
                warning.message = 'Didn\'t check in between "%s" and "%s" ' % (
                    warning.min_int,
                    warning.max_int,
                )
            elif warning.warning_type == 'no_check_out':
                warning.message = 'Didn\'t check out between "%s" and "%s" ' %\
                    (
                        warning.min_int,
                        warning.max_int,
                    )
            elif warning.warning_type == 'out_of_interval':
                warning.message = 'Came to work out of working hours'
