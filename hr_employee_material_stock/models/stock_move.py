# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

class StockMove(models.Model):

    _inherit = 'stock.move'
    employee_material_id = fields.Many2one('hr.employee.material', "Employee material")

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append('employee_material_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super()._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.employee_material_id.id)
        return keys_sorted

    def _action_cancel(self):
        super()._action_cancel()
        for rec in self.sudo():
            if not rec.employee_material_id.qty_delivered:
                rec.employee_material_id.update({'state': 'cancelled'})
            else:
                rec.employee_material_id.update({'state': 'valid'})
