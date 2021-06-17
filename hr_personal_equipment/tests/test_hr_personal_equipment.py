# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

class TestHRPersonalEquipment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product_personal_equipment_1 = self.env['product.template'].create(
            {
                'name': 'Product Test Personal Equipment 1',
                'is_personal_equipment': True}
        )
        self.product_personal_equipment_2 = self.env['product.template'].create(
            {
                'name': 'Product Test Personal Equipment 2',
                'is_personal_equipment': True}
        )
        self.user = self.env['res.users'].sudo().create(
            {
                'name': 'Test User',
                'login': 'user@test.com',
                'email': 'user@test.com',
                "groups_id": [
                    (4, self.env.ref('base.group_user').id),
                    (4, self.env.ref('hr.group_hr_user').id)
                ],
            }
        )
        self.employee = self.env['hr.employee'].create(
            {
                'name': 'Employee Test',
                'user_id': self.user.id
            }
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
            }
        )

    def test_request_compute_name(self):
        self.assertTrue(self.personal_equipment_request.name)
        self.assertEqual(self.personal_equipment_request.name, "Personal Equipment Request by Test User")

    def test_accept_request(self):
        self.assertEqual(self.personal_equipment_request.state, 'draft')
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, 'draft')
        self.personal_equipment_request.accept_request()
        self.assertEqual(self.personal_equipment_request.state, 'accepted')
        self.assertEqual(self.personal_equipment_request.line_ids[0].state, 'accepted')

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




