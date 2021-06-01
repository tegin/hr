# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrEmployeeMaterialRequest(models.Model):

    _name = 'hr.employee.material.request'
    _description = 'This model allows to create a employee material request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute="_compute_name")
    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=True, default=lambda self: self._default_employee_id()
    )
    line_ids = fields.One2many(string="Material", comodel_name="hr.employee.material",
                               inverse_name="material_request_id")
    state = fields.Selection([("draft", "Draft"),
                              ("accepted", "Accepted"),
                              ("cancelled", "Cancelled")],
                             default='draft', track_visibility=True)

    def _default_employee_id(self):
        return self.env.user.employee_ids[:1]

    @api.depends("employee_id")
    def _compute_name(self):
        for rec in self:
            rec.name = _("Material Request by %s") % rec.employee_id.name

    def accept_request(self):
        for rec in self:
            rec.state = 'accepted'
            rec.line_ids.update({'state': 'accepted'})

    def cancel_request(self):
        for rec in self:
            rec.state = 'cancelled'
            rec.line_ids.update({'state': 'cancelled'})

    @api.onchange("employee_id", "line_ids")
    def _set_employee_material_fields(self):
        for rec in self:
            if rec.line_ids:
                for line in rec.line_ids:
                    rec._set_employee_material_fields_values(line)

    def _set_employee_material_fields_values(self, line):
        line.employee_id = self.employee_id

