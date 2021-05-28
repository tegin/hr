# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    is_employee_material = fields.Boolean(default=False)

