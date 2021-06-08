# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Employee Material Stock',
    'summary': """
        This addon allows to integrate hr_employee_material with stock""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': ['hr_employee_material', 'stock'
    ],
    'data': [
        'views/stock_move.xml',
        'views/procurement_group.xml',
        'views/hr_employee_material.xml',
        'views/hr_employee_material_request.xml',
        'views/stock_picking.xml'
    ],
    'demo': [
    ],
}
