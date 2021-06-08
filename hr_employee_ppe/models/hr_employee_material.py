# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeMaterial(models.Model):

    _name = "hr.employee.material"
    _inherit = ["hr.employee.material"]

    name = fields.Char(
        compute='_compute_name',
    )
    is_ppe = fields.Boolean()
    #start_date = fields.Date(string="Start Date", default=fields.Date.today())
    end_date = fields.Date()
    description = fields.Text()
    #partner_id = fields.Many2one(comodel_name="res.partner", string="Issued By", help="Certification Authority")
    indications = fields.Text(
        help="Situations in which the employee should use this equipment.",
    )
    expire = fields.Boolean(help="True if the PPE expires")
    certification = fields.Char(
        string="Certification Number", help="Certification Number"
    )
    issued_by = fields.Many2one(comodel_name="res.users")
    """
    status = fields.Selection(
        [("valid", "Valid"), ("expired", "Expired")],
        compute="_compute_status",
        readonly=True,
        help="PPE Status",
    )
    """

    @api.onchange('product_id')
    def _compute_fields(self):
        for rec in self:
            if rec.product_id.is_ppe:
                rec.is_ppe = rec.product_id.is_ppe
                if rec.product_id.expirable:
                    rec.expire = rec.product_id.expirable
                if rec.product_id.indications:
                    rec.indications = rec.product_id.indications
                if rec.product_id.description:
                    rec.description = rec.product_id.description
                if rec.product_id.certification:
                    rec.certification = rec.product_id.certification

    def _validate_allocation_vals(self):
        res = super()._validate_allocation_vals()
        res['issued_by'] = self.env.user
        return res

    def validate_allocation(self):
        self._check_dates()
        super().validate_allocation()

    @api.depends("end_date", "start_date")
    def _compute_state(self):
        for rec in self:
            if rec.state == "valid" and rec.expire and rec.end_date:
                if rec.end_date < fields.Date.today():
                    rec.status = "expired"

    @api.model
    def cron_ppe_expiry_verification(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        domain = []
        domain.extend([("end_date", "<", date_ref)])
        ppes_to_check_expiry = self.search(domain)
        for record in ppes_to_check_expiry:
            record.status = "expired"

    def _check_dates(self):
        for record in self:
            if record.expire:
                if not record.end_date:
                    raise ValidationError(
                        _(
                            """You must inform start date and
                            end date for expirable PPEs."""
                        )
                    )
                if record.end_date < record.start_date:
                    raise ValidationError(
                        _("End date cannot occur earlier than the start date.")
                    )

    def action_view_ppe_report(self):
        report = self.env['ir.actions.report']._get_report_from_name(
            'hr_employee_ppe.hr_employee_ppe_report_template')
        return report.report_action(self)
