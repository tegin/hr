# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl

from datetime import datetime, timedelta

from odoo.tests import TransactionCase

from odoo.exceptions import ValidationError

from odoo.tests.common import Form

class TestHREmployeePPE(TransactionCase):
    def setUp(self):
        super().setUp()
        self.product_employee_ppe_expirable = self.env['product.template'].create(
            {
                'name': 'Product Test Employee PPE',
                'is_employee_material': True,
                'is_ppe': True,
                'indications': "Test indications",
                'expirable_ppe': True
            }
        )
        self.product_employee_ppe_no_expirable = self.env['product.template'].create(
            {
                'name': 'Product Test Employee No PPE',
                'is_employee_material': True,
                'is_ppe': True,
                'indications': "Test indications",
                'expirable_ppe': False,
            }
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
                'name': 'Employee Material PPE Expirable',
                'product_id': self.product_employee_ppe_expirable.product_variant_id.id,
                'quantity': 3
            },
            {
                'name': 'Employee Material No Expirable',
                'product_id': self.product_employee_ppe_no_expirable.product_variant_id.id,
                'quantity': 2
            }
        ]

        self.employee_material_request = self.env['hr.employee.material.request'].sudo(self.user.id).create(
            {
                'name': 'Employee Material Request Test',
                'line_ids': [(0, 0, line) for line in lines],
            }
        )

        self.hr_employee_ppe_expirable = self.employee_material_request.line_ids[0]
        self.hr_employee_ppe_no_expirable = self.employee_material_request.line_ids[1]

    def test_compute_fields(self):
        self.hr_employee_ppe_expirable._compute_fields()
        self.assertTrue(self.hr_employee_ppe_expirable.is_ppe)
        self.assertTrue(self.hr_employee_ppe_expirable.expire_ppe)
        self.assertEqual(self.hr_employee_ppe_expirable.indications, self.product_employee_ppe_expirable.indications)

    def test_validate_allocation(self):
        self.assertFalse(self.hr_employee_ppe_expirable.issued_by)
        self.hr_employee_ppe_expirable.sudo(self.user).validate_allocation()
        self.assertTrue(self.hr_employee_ppe_expirable.issued_by)
        self.assertEqual(self.hr_employee_ppe_expirable.issued_by, self.user)

    def test_cron_ppe_expiry_verification_expired_product(self):
        self.hr_employee_ppe_expirable.start_date = "2020-01-01"
        self.hr_employee_ppe_expirable.end_date = "2020-12-31"
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_expirable.state, 'valid')
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertEqual(self.hr_employee_ppe_expirable.state, "expired")

    def test_cron_ppe_expiry_verification_no_expired_product(self):
        self.hr_employee_ppe_expirable.end_date = (
            datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.hr_employee_ppe_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_expirable.state, 'valid')
        self.hr_employee_ppe_expirable.cron_ppe_expiry_verification()
        self.assertNotEqual(self.hr_employee_ppe_expirable.state, "expired")

    def test_cron_ppe_expiry_verification_no_expirable_product(self):
        self.hr_employee_ppe_no_expirable.validate_allocation()
        self.assertEqual(self.hr_employee_ppe_no_expirable.state, 'valid')
        self.hr_employee_ppe_no_expirable.cron_ppe_expiry_verification()
        self.assertNotEqual(self.hr_employee_ppe_no_expirable.state, "expired")

    def test_check_dates(self):
        self.hr_employee_ppe_expirable._compute_fields()
        with self.assertRaises(ValidationError):
            self.hr_employee_ppe_expirable.validate_allocation()

        with self.assertRaises(ValidationError):
            self.hr_employee_ppe_expirable.start_date = "2020-01-01"
            self.hr_employee_ppe_expirable.end_date = "2019-12-31"
            self.hr_employee_ppe_expirable.validate_allocation()

    def test_compute_contains_ppe(self):
        # Without materials ppe
        product_employee_no_ppe = self.env['product.template'].create(
            {
                'name': 'Product Test Employee No PPE',
                'is_employee_material': True,
                'is_ppe': False,
            }
        )
        lines = [{
                'name': 'Employee Material PPE Expirable',
                'product_id': product_employee_no_ppe.product_variant_id.id,
                'quantity': 3
            }]

        employee_material_request = self.env['hr.employee.material.request'].sudo(self.user.id).create(
            {
                'name': 'Employee Material Request Test',
                'line_ids': [(0, 0, line) for line in lines],
            }
        )
        employee_material_request._compute_contains_ppe()
        self.assertFalse(employee_material_request.contains_ppe)

        # With materials ppe
        lines.append({
                'name': 'Employee Material PPE Expirable',
                'is_ppe': True,
                'product_id': self.product_employee_ppe_expirable.product_variant_id.id,
                'quantity': 3
            })
        employee_material_request['line_ids'] = [(0, 0, line) for line in lines]
        employee_material_request._compute_contains_ppe()
        self.assertTrue(employee_material_request.contains_ppe)

    def test_action_view_ppe_report(self):
        action = self.employee_material_request.action_view_ppe_report()
        self.assertEqual(action['name'], 'Receipt of Personal protection Equipment')
        self.assertEqual(len(action["context"]["active_ids"]), 1)
        self.assertEqual(action["context"]["active_ids"][0], self.employee_material_request.id)
        self.assertEqual(action['report_type'], 'qweb-pdf')

