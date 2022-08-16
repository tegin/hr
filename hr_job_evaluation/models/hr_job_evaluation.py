# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class HrJobEvaluation(models.Model):
    _name = "hr.job.evaluation"
    _description = "HR Job Position Evaluation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    employee_id = fields.Many2one(
        "hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    job_id = fields.Many2one(
        "hr.job", required=True, readonly=True, states={"draft": [("readonly", False)]}
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("evaluation", "In Evaluation"),
            ("passed", "Evaluation Passed"),
            ("failure", "Evaluation Failed"),
        ],
        default="draft",
        readonly=True,
        tracking=True,
    )
    skill_ids = fields.One2many(
        "hr.job.evaluation.skill",
        inverse_name="evaluation_id",
        readonly=True,
        states={"evaluation": [("readonly", False)]},
    )
    evaluation = fields.Html(
        readonly=True, states={"evaluation": [("readonly", False)]}
    )

    @api.depends("employee_id", "job_id")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s (%s)" % (
                record.employee_id.display_name,
                record.job_id.display_name,
            )

    def start_evaluation(self):
        self.ensure_one()
        if self.state != "draft":
            return
        self.write(self._start_evaluation_vals())

    def _start_evaluation_vals(self):
        return {
            "state": "evaluation",
            "skill_ids": [
                (0, 0, skill._get_job_skill_vals(self.employee_id))
                for skill in self.job_id.skill_ids
            ],
        }

    def pass_evaluation(self):
        self.ensure_one()
        if self.skill_ids.filtered(lambda r: not r.skill_level_id):
            raise ValidationError(_("Level is required in all skill evaluations"))
        if self.state != "evaluation":
            return
        self.write(self._pass_evaluation_vals())
        self._store_skills()

    def _pass_evaluation_vals(self):
        return {"state": "passed"}

    def reject_evaluation(self):
        self.ensure_one()
        if self.state != "evaluation":
            return
        self.write(self._reject_evaluation_vals())
        self._store_skills()

    def _reject_evaluation_vals(self):
        return {"state": "failure"}

    def _store_skills(self):
        employee = self.employee_id
        for skill in self.skill_ids:
            if not skill.skill_level_id:
                # This should only happen on rejection
                continue
            employee_skill = employee.employee_skill_ids.filtered(
                lambda r: r.skill_id == skill.skill_id
            )
            if employee_skill:
                employee_skill.skill_level_id = skill.skill_level_id
            else:
                employee.write(
                    {"employee_skill_ids": [(0, 0, skill._get_employee_skill_vals())]}
                )


class HrJobEvaluationSkill(models.Model):
    _name = "hr.job.evaluation.skill"
    _description = "Reviewed Skills on a Job Evaluation"

    evaluation_id = fields.Many2one("hr.job.evaluation", required=True, readonly=True)
    skill_id = fields.Many2one("hr.skill", required=True, readonly=True)
    skill_level_id = fields.Many2one("hr.skill.level")
    expected_level_id = fields.Many2one("hr.skill.level", required=True, readonly=True)
    skill_type_id = fields.Many2one("hr.skill.type", required=True, readonly=True)
    level_progress = fields.Integer(
        related="skill_level_id.level_progress", readonly=True
    )
    passed = fields.Boolean(compute="_compute_passed", store=True)

    _sql_constraints = [
        (
            "_unique_skill",
            "unique (evaluation_id, skill_id)",
            "Two levels for the same skill is not allowed",
        ),
    ]

    @api.depends("skill_level_id")
    def _compute_passed(self):
        for record in self:
            record.passed = (
                float_compare(
                    record.level_progress,
                    record.expected_level_id.level_progress,
                    precision_digits=2,
                )
                >= 0
            )

    def _get_employee_skill_vals(self):
        return {
            "skill_level_id": self.skill_level_id.id,
            "skill_id": self.skill_id.id,
            "skill_type_id": self.skill_type_id.id,
        }
