# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    material_request_id = fields.Many2one(related='group_id.material_request_id')
    def button_validate(self):
        super().button_validate()
        for rec in self:
            print(self.group_id)
            print(self.group_id.material_request_id)
            rec.material_request_id.state = 'valid'
