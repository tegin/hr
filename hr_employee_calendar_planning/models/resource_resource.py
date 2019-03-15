# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    calendar_id = fields.Many2one(required=False)
