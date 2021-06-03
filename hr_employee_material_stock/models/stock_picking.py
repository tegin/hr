# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    material_request_id = fields.Many2one(related='group_id.material_request_id')

    def action_done(self):
        super().action_done()
        print(self.group_id)
        print(self.group_id.material_request_id)
        if self.material_request_id:
            for move in self.move_ids_without_package:
                if move.state == 'done':
                    request_lines = self.material_request_id.line_ids.filtered(lambda x: x.product_id == move.product_id)
                    for line in request_lines:
                        line.state = 'valid'
