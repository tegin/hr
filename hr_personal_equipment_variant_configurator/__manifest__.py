# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Personal Equipment Variant Configurator',
    'description': """
        Manage variants of personal equipment""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca',
    'website': 'www.creublanca.es',
    'depends': ['hr_personal_equipment', 'product_variant_configurator'],
    'data': [
        'views/hr_personal_equipment_request.xml',
    ],
    'demo': [
    ],
}
