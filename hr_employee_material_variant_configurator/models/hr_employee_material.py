# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrEmployeeMaterial(models.Model):

    _inherit = ['hr.employee.material', 'product.configurator']
    _name = 'hr.employee.material'

    product_tmpl_id = fields.Many2one(domain=[('is_employee_material', '=', True)])
