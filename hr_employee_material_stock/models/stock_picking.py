# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from datetime import date

class StockPicking(models.Model):

    _inherit = 'stock.picking'

    material_request_id = fields.Many2one(related='group_id.material_request_id')

    def action_done(self):
        super().action_done()
        if self.material_request_id:
            for move in self.move_ids_without_package:
                if move.state == 'done':
                    request_lines = self.material_request_id.sudo().line_ids.filtered(lambda x: x.product_id == move.product_id)
                    for line in request_lines:
                        qty_initial = line.product_uom_id._compute_quantity(line.quantity, line.product_uom_id)
                        qty_done = line.product_uom_id._compute_quantity(line.qty_delivered, line.product_uom_id)
                        if qty_done:
                            if qty_initial <= qty_done:
                                line.state = 'valid'
                            line.start_date = date.today()


