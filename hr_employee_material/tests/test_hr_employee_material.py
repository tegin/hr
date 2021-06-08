# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

class TestHREmployeeMaterial(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product_employee_material_1 = self.env['product.template'].create(
            {
                'name': 'Product Test Employee Material 1',
                'is_employee_material': True}
        )
        self.product_employee_material_2 = self.env['product.template'].create(
            {
                'name': 'Product Test Employee Material 2',
                'is_employee_material': True}
        )
        self.user = self.env['res.users'].sudo().create(
            {
                'name': 'Test User',
                'login': 'user@test.com',
                'email': 'user@test.com',
                "groups_id": [
                    (4, self.env.ref('base.group_user').id),
                    (4, self.env.ref("hr_employee_material.hr_employee_material_group").id)
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
                'name': 'Employee Material 1',
                'product_id': self.product_employee_material_1.product_variant_id.id,
                'quantity': 3
            },
            {
                'name': 'Employee Material 2',
                'product_id': self.product_employee_material_2.product_variant_id.id,
                'quantity': 2
            }
        ]

        self.employee_material_request = self.env['hr.employee.material.request'].sudo(self.user.id).create(
            {
                'name': 'Employee Material Request Test',
                'line_ids':  [(0, 0, line) for line in lines],
            }
        )

    def test_request_compute_name(self):
        self.assertTrue(self.employee_material_request.name)
        self.assertEqual(self.employee_material_request.name, "Material Request by Test User")

    def test_accept_request(self):
        self.assertEqual(self.employee_material_request.state, 'draft')
        self.assertEqual(self.employee_material_request.line_ids[0].state, 'draft')
        self.employee_material_request.accept_request()
        self.assertEqual(self.employee_material_request.state, 'accepted')
        self.assertEqual(self.employee_material_request.line_ids[0].state, 'accepted')

    def test_cancel_request(self):
        self.assertEqual(self.employee_material_request.state, 'draft')
        self.assertEqual(self.employee_material_request.line_ids[0].state, 'draft')
        self.employee_material_request.cancel_request()
        self.assertEqual(self.employee_material_request.state, 'cancelled')
        self.assertEqual(self.employee_material_request.line_ids[0].state, 'cancelled')

    def test_allocation_compute_name(self):
        self.assertEqual(self.employee_material_request.line_ids[0].name,
                         'Product Test Employee Material 1 to Test User')

    def test_validate_allocation(self):
        self.employee_material_request.accept_request()
        allocation = self.employee_material_request.line_ids[0]
        self.assertEqual(allocation.state, 'accepted')
        allocation.validate_allocation()
        self.assertEqual(allocation.state, 'valid')

    def test_expire_allocation(self):
        self.employee_material_request.accept_request()
        allocation = self.employee_material_request.line_ids[0]
        allocation.validate_allocation()
        self.assertEqual(allocation.state, 'valid')
        allocation.expire_allocation()
        self.assertEqual(allocation.state, 'expired')




