# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):

    _name = 'product.template'
    _inherit = ['product.template']

    """
    product_id = fields.Many2one(
        required=True,
        comodel_name='product.product',
        domain="[('type', '=', 'consu')]"
    )
    """
    is_ppe = fields.Boolean(default=False)
    indications = fields.Text(
        string="Indications",
        help="Situations in which the employee should use this equipment. Only for ppe",
    )
    expirable = fields.Boolean(
        help='Select this option if the PPE has expiry date.', default=False
    )
    certification = fields.Char(
        string="Certification Number", help="Certification Number"
    )
    description = fields.Text()


