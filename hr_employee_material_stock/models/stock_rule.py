# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom,
                               location_id, name, origin, values, group_id):
        result = super()._get_stock_move_values(
            product_id, product_qty, product_uom,
            location_id, name, origin, values, group_id
        )
        if values.get("employee_material_id"):
            result["employee_material_id"] = values.get("employee_material_id")
        return result
