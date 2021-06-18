# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

class TestHRPersonalEquipment(TransactionCase):

    def setUp(self):
        super().setUp()

        self.warehouse = self.env.ref('stock.warehouse0')
        self.company = self.env.ref('base.main_company')
        self.ressuply_loc = self.env['stock.location'].create({
            'name': 'Warehouse Test',
            'location_id': self.warehouse.view_location_id.id,
        })
        self.location_employee = self.env['stock.location'].create({
            'name': 'Employee Personal Equipment Virtual Location',
            'location_id': self.warehouse.view_location_id.id,
            'usage': 'transit'
        })
        self.route = self.env['stock.location.route'].create({
            'name': 'Employee Personal Equipment Route',
            'product_categ_selectable': False,
            'product_selectable': True,
            'company_id': self.company.id,
            'sequence': 10,
        })
        self.env['stock.rule'].create({
            'name': 'Employee Personal Equipment Rule',
            'route_id': self.route.id,
            'location_src_id': self.ressuply_loc.id,
            'location_id': self.location_employee.id,
            'action': 'pull',
            'picking_type_id': self.warehouse.int_type_id.id,
            'procure_method': 'make_to_stock',
            'warehouse_id': self.warehouse.id,
            'company_id': self.company.id,
            'propagate': 'False',
        })
        self.user = self.env['res.users'].sudo().create(
            {
                'name': 'Test User',
                'login': 'user@test.com',
                'email': 'user@test.com',
                "groups_id": [
                    (4, self.env.ref('base.group_user').id),
                    (4, self.env.ref('hr.group_hr_user').id),
                    (4, self.env.ref('stock.group_stock_manager').id)
                ],
            }
        )
        self.employee = self.env['hr.employee'].create(
            {
                'name': 'Employee Test',
                'user_id': self.user.id
            }
        )
        self.product_personal_equipment_1 = self.env['product.template'].create(
            {
                'name': 'Product Test Personal Equipment',
                'is_personal_equipment': True,
                'route_ids': [(6, 0, self.route.ids)],
                'qty_available': 100,
                'type': 'product'}
        )
        self.product_personal_equipment_2 = self.env['product.template'].create(
            {
                'name': 'Service Test Personal Equipment 2',
                'is_personal_equipment': True,
                'type': 'service'}
        )
        lines = [
            {
                'name': 'Personal Equipment 1',
                'product_id': self.product_personal_equipment_1.product_variant_id.id,
                'quantity': 3
            },
            {
                'name': 'Personal Equipment 2',
                'product_id': self.product_personal_equipment_2.product_variant_id.id,
                'quantity': 2
            }
        ]

        self.personal_equipment_request = self.env['hr.personal.equipment.request'].sudo(self.user.id).create(
            {
                'name': 'Personal Equipment Request Test',
                'line_ids':  [(0, 0, line) for line in lines],
                'location_id': self.location_employee.id
            }
        )


    def test_get_procurement_group_without_group_set(self):
        self.assertEqual(self.personal_equipment_request.state, 'draft')
        self.assertFalse(self.personal_equipment_request.procurement_group_id)
        self.assertFalse(self.personal_equipment_request.line_ids[0].procurement_group_id)
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, 'accepted')
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(self.personal_equipment_request.line_ids[0].procurement_group_id)

    def test_get_procurement_group_with_group_set(self):
        self.assertEqual(self.personal_equipment_request.state, 'draft')
        procurement_group_id = self.env['procurement.group'].create({
            'move_type': 'direct',
        })
        self.personal_equipment_request.procurement_group_id = procurement_group_id.id
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(self.personal_equipment_request.line_ids[0].procurement_group_id)
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, 'accepted')
        self.assertTrue(self.personal_equipment_request.procurement_group_id)
        self.assertTrue(self.personal_equipment_request.line_ids[0].procurement_group_id)
        self.assertEqual(self.personal_equipment_request.procurement_group_id.id, procurement_group_id.id)

    def test_compute_picking_count(self):
        self.assertEqual(self.personal_equipment_request.picking_count, 0)
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.picking_count, 1)

"""
    def test_cancel_request(self):
        self.assertEqual(self.personal_equipment_request.state, 'draft')
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, 'draft')
        self.personal_equipment_request.cancel_request()
        self.assertEqual(self.personal_equipment_request.state, 'cancelled')
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, 'cancelled')

    def test_allocation_compute_name(self):
        self.assertEqual(self.personal_equipment_request.line_ids[0].name,
                         'Product Test Personal Equipment 1 to Test User')

    def test_validate_allocation(self):
        self.personal_equipment_request.accept_request()
        allocation = self.personal_equipment_request.line_ids[0]
        self.assertEqual(allocation.state, 'accepted')
        allocation.validate_allocation()
        self.assertEqual(allocation.state, 'valid')

    def test_expire_allocation(self):
        self.personal_equipment_request.accept_request()
        allocation = self.personal_equipment_request.line_ids[0]
        allocation.validate_allocation()
        self.assertEqual(allocation.state, 'valid')
        allocation.expire_allocation()
        self.assertEqual(allocation.state, 'expired')

"""


