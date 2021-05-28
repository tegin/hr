# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Employee Material',
    'summary': """
        This addon allows to manage employee material""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.creublanca.es',
    'depends': ["product", "hr", "mail"
    ],
    'data': [
        'security/hr_employee_material_security.xml',
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/hr_employee_material.xml',
        'views/hr_employee_material_request.xml',
    ],
    'demo': [
    ],
}
