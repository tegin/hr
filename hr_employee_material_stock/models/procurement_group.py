# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ProcurementGroup(models.Model):

    _inherit = 'procurement.group'

    material_request_id = fields.Many2one("hr.employee.material.request")
