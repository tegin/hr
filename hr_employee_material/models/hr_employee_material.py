# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from datetime import date

class HrEmployeeMaterial(models.Model):

    _name = 'hr.employee.material'
    _description = 'Adds employee material information and allocation'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute='_compute_name')
    product_id = fields.Many2one(comodel_name='product.product', required=True,
                                 domain=[('is_employee_material', '=', '1')])
    employee_id = fields.Many2one(comodel_name='hr.employee')
    state = fields.Selection([("draft", "Draft"),
                              ("accepted", "Accepted"),
                              ("valid", "Valid"),
                              ("expired", "Expired"),
                              ("cancelled", "Cancelled")],
                             default="draft", track_visibility=True)
    start_date = fields.Date()
    material_request_id = fields.Many2one(comodel_name="hr.employee.material.request")
    quantity = fields.Integer(default=1)
    product_uom_id = fields.Many2one(
        "uom.uom",
        "Unit of Measure",
        default=lambda self: self._default_uom_id()
    )

    def _default_uom_id(self):
        return self.env.ref("uom.product_uom_unit")

    @api.depends('product_id', 'employee_id')
    def _compute_name(self):
        for rec in self:
            if rec.product_id.name and rec.employee_id.name:
                rec.name = rec.product_id.name + _(" to ") + rec.employee_id.name

    def validate_allocation(self):
        for rec in self:
            rec.state = 'valid'
            rec.start_date = date.today()

    def expire_allocation(self):
        for rec in self:
            rec.state = 'expired'
